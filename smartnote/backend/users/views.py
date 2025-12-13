from rest_framework import generics, permissions, status
from .models import User
from .serializers import UserSerializer
from utils.api_response import ok, fail  # <-- helper chung

# API lấy danh sách user và tạo user mới
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer

    # Cho phép ai cũng tạo (POST), nhưng GET (list) thì phải đăng nhập
    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    # Tắt authentication riêng cho POST để khỏi dính CSRF khi test bằng Postman/cURL
    def get_authenticators(self):
        request = getattr(self, "request", None)
        if request and request.method == "POST":
            return []
        return super().get_authenticators()


    # Bọc list()
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return ok(serializer.data, message="Fetched")

    # Bọc create()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Nếu bạn dùng HyperlinkedModelSerializer, DRF có thể cung cấp Location header
        headers = self.get_success_headers(serializer.data)
        # Khuyên trả luôn object vừa tạo cho FE dùng
        return ok(serializer.data, message="Created", status=status.HTTP_201_CREATED, headers=headers)


class UserSelfView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Không dùng id — lấy trực tiếp user đang đăng nhập
    def get_object(self):
        return self.request.user

    # Bọc retrieve()
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        return ok(data, message="Fetched")

    # Bọc update() (hỗ trợ PUT/PATCH)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ok(serializer.data, message="Updated")

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    # Bọc destroy()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        # Dùng 200 để trả JSON thống nhất (thay vì 204)
        return ok(message="Deleted")
