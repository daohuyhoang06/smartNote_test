from rest_framework import generics, mixins, permissions, status
from rest_framework.views import APIView
from rest_framework.exceptions import NotAuthenticated, NotFound
from django.shortcuts import get_object_or_404
from urllib.parse import unquote_plus
import re
from rapidfuzz import fuzz
from django.db.models import Case, When, IntegerField

from .models import Note, Topic, Voca, VocaTopic, VocaDetail
from .serializers import NoteSerializer, TopicSerializer
from .permissions import IsOwnerOnly
from .pagination import NotePagination
from django.db import transaction
from notes.tasks import sync_and_generate_exercises_task
from drf_spectacular.openapi import AutoSchema
from utils.api_response import ok, fail, fail_errors  # <-- thêm fail_errors


# ---------------------------------------------------------------------
# Lấy chi tiết Note (sổ tay của user)
# ---------------------------------------------------------------------
class NoteDetailView(generics.RetrieveAPIView):
    serializer_class = NoteSerializer
    schema = AutoSchema()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOnly]

    def get_object(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            raise NotAuthenticated("Bạn cần đăng nhập để truy cập sổ tay.")

        try:
            note = user.note  # OneToOneField -> thuộc tính ngược
        except Note.DoesNotExist:
            raise NotFound("Không tìm thấy sổ tay của bạn.")
        return note

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        return ok(data, message="Fetched")


# ---------------------------------------------------------------------
# Lấy danh sách Topic trong Note có phân trang
# ---------------------------------------------------------------------
class NoteDetailWithTopicsPagination(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    schema = AutoSchema()
    serializer_class = TopicSerializer
    pagination_class = NotePagination

    def get_queryset(self):
        user = self.request.user
        note, _ = Note.objects.get_or_create(user=user)
        # giữ lại note để gán vào paginator instance ở list()
        self._note = note
        return Topic.objects.filter(note=note).order_by('-id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # gọi paginate -> DRF khởi tạo self.paginator
        page = self.paginate_queryset(queryset)

        # gán note cho **instance** paginator (sau khi paginator đã có)
        if hasattr(self, "paginator") and self.paginator:
            self.paginator.note = getattr(self, "_note", None)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)  # NotePagination -> ok(...)

        # Không phân trang
        serializer = self.get_serializer(queryset, many=True)
        note_meta = None
        if getattr(self, "_note", None):
            created_at = getattr(self._note, "created_at", None)
            created_iso = created_at.isoformat() if hasattr(created_at, "isoformat") else created_at
            note_meta = {"id": getattr(self._note, "id", None), "created_at": created_iso}

        payload = {
            "count": len(serializer.data),
            "page": 1,
            "page_size": len(serializer.data),
            "next": None,
            "previous": None,
            "note": note_meta,
            "results": serializer.data,
        }
        return ok(payload, message="Fetched")


# ---------------------------------------------------------------------
# Danh sách + Tạo Topic
# ---------------------------------------------------------------------
class TopicListCreateView(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          generics.GenericAPIView):

    queryset = Topic.objects.all().order_by('-created_at')
    serializer_class = TopicSerializer
    schema = AutoSchema()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Topic.objects.filter(note__user=user).order_by('-id')

    def perform_create(self, serializer):
        user = self.request.user
        note, _ = Note.objects.get_or_create(user=user)
        serializer.save(note=note)

    # GET (list)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            payload = {
                "count": self.paginator.page.paginator.count,
                "page": self.paginator.page.number,
                "page_size": self.paginator.get_page_size(request),
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
                "results": ser.data,
            }
            return ok(payload, message="Fetched")
        ser = self.get_serializer(queryset, many=True)
        return ok(ser.data, message="Fetched")

    # POST (create) — trả lỗi có errors khi validate fail
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return fail_errors(serializer.errors, message="Validation error", status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # nên trả luôn object vừa tạo cho FE dùng
        return ok("", message="Created", status=status.HTTP_201_CREATED, headers=headers)


# ---------------------------------------------------------------------
# Chi tiết 1 Topic
# ---------------------------------------------------------------------
class TopicDetailView(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      generics.GenericAPIView):
    """
    GET    /topics/<pk>/   -> retrieve
    DELETE /topics/<pk>/   -> delete
    """
    serializer_class = TopicSerializer
    schema = AutoSchema()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Khi drf_yasg gọi trong lúc build schema, thuộc tính này = True
        if getattr(self, 'swagger_fake_view', False):
            return Topic.objects.none()

        user = self.request.user
        # Phòng hờ trường hợp chưa auth
        if not user or not user.is_authenticated:
            return Topic.objects.none()

        return Topic.objects.filter(note__user=user)
        # Hoặc dùng id cho chắc:
        # return Topic.objects.filter(note__user_id=user.id)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = self.get_serializer(instance)
        return ok(ser.data, message="Fetched")

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return fail_errors(serializer.errors, message="Validation error")
        self.perform_update(serializer)
        return ok(serializer.data, message="Updated")

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if not serializer.is_valid():
            return fail_errors(serializer.errors, message="Validation error")
        self.perform_update(serializer)
        return ok(serializer.data, message="Updated")

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ok(message="Deleted", status=status.HTTP_200_OK)


# ---------------------------------------------------------------------
# Thêm từ vào Topic
# ---------------------------------------------------------------------
class AddWordToTopicView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    schema = AutoSchema()

    def post(self, request, pk, query):
        topic = get_object_or_404(Topic, pk=pk, note__user=request.user)
        words_str = request.data.get("words", query)

        if not words_str:
            # lỗi có trường errors
            return fail_errors({"words": ["Missing 'words' field"]}, status=400)

        serializer = TopicSerializer(topic, context={"request": request})
        voca_details = serializer._process_vocas(topic, words_str) or []

        # nếu cần chạy task sau commit:
        # if voca_details:
        #     ids = [d.id for d in voca_details if d]
        #     if ids:
        #         transaction.on_commit(lambda: sync_and_generate_exercises_task.delay(ids))

        added_count = len([d for d in voca_details if d])
        return ok("", message="Words added successfully")


# ---------------------------------------------------------------------
# Xóa từ khỏi Topic
# ---------------------------------------------------------------------
class DeleteWordFromTopicView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    schema = AutoSchema()

    def delete(self, request, pk, voca_topic_id, voca_detail_id):
        topic = get_object_or_404(Topic, pk=pk, note__user=request.user)
        voca_topic = get_object_or_404(VocaTopic, pk=voca_topic_id, topic=topic)
        voca = voca_topic.voca

        voca_detail = get_object_or_404(VocaDetail, pk=voca_detail_id, voca_topic=voca_topic)
        voca_detail.delete()

        if not VocaDetail.objects.filter(voca_topic=voca_topic).exists():
            voca_topic.delete()

        if not voca.voca_topics.exists():
            voca.delete()

        return ok(message="Deleted", status=status.HTTP_200_OK)

    # GET để test nhanh
    def get(self, request, pk, voca_topic_id, voca_detail_id):
        return self.delete(request, pk, voca_topic_id, voca_detail_id)


# ---------------------------------------------------------------------
# Tìm kiếm Topic (fuzzy)
# ---------------------------------------------------------------------
def _normalize_q(s: str) -> str:
    s = unquote_plus(s or "").strip()
    # gom mọi loại “gạch” về "/"
    s = s.replace("\\", "/").replace("\u2215", "/").replace("\uff0f", "/")
    s = re.sub(r"[-\u2010-\u2015_\s]+", "/", s)
    s = re.sub(r"/{2,}", "/", s)
    return s


class TopicSearchView(generics.ListAPIView):
    serializer_class = TopicSerializer
    schema = AutoSchema()
    permission_classes = [permissions.IsAuthenticated]

    FIELD_WHITELIST = {"title"}  # đổi theo model thực tế

    def get_queryset(self):
        user = self.request.user
        qs = Topic.objects.filter(note__user=user).order_by("-id")

        raw_q = self.request.query_params.get("q", "")
        field = self.request.query_params.get("field", "title")
        field = field if field in self.FIELD_WHITELIST else "title"

        q = _normalize_q(raw_q)
        if not q:
            # KHÔNG trả hết nếu thiếu q (list() sẽ trả 400 ở ngoài)
            return qs.none()

        # 1) exact
        exact = qs.filter(**{f"{field}__iexact": q})
        if exact.exists():
            return exact

        # 2) icontains (nhanh, load DB)
        ic = qs.filter(**{f"{field}__icontains": q})
        if ic.exists():
            return ic

        # 3) fuzzy (giới hạn ứng viên để tránh nặng)
        candidates = list(qs.values_list("id", field)[:1500])  # tuỳ chỉnh ngưỡng
        scored = []
        ql = q.lower()
        for tid, text in candidates:
            s = (text or "").lower()
            score = fuzz.ratio(s, ql)
            if score >= 60:  # 60–80 thường hợp lý
                scored.append((score, tid))

        if not scored:
            return qs.none()

        # sắp theo điểm giảm dần, giữ thứ tự với Case/When
        scored.sort(key=lambda x: x[0], reverse=True)
        ordered_ids = [tid for _, tid in scored]
        whens = [When(id=tid, then=pos) for pos, tid in enumerate(ordered_ids)]
        return qs.filter(id__in=ordered_ids).annotate(
            _rank=Case(*whens, default=999999, output_field=IntegerField())
        ).order_by("_rank")

    # bọc list() — check param `q` và trả lỗi có errors
    def list(self, request, *args, **kwargs):
        raw_q = request.query_params.get("q", "")
        q = _normalize_q(raw_q)
        if not q:
            return fail_errors({"q": ["This query param is required"]}, message="Validation error", status=400)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            payload = {
                "count": self.paginator.page.paginator.count,
                "page": self.paginator.page.number,
                "page_size": self.paginator.get_page_size(request),
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
                "results": ser.data,
            }
            return ok(payload, message="Fetched")

        ser = self.get_serializer(queryset, many=True)
        return ok(ser.data, message="Fetched")
