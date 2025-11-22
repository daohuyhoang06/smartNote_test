# notes/pagination.py
from rest_framework.pagination import PageNumberPagination
from utils.api_response import ok  # dùng helper đã tạo

class NotePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    # view sẽ gán: self.pagination_class.note = note
    note = None

    def get_paginated_response(self, data):
        note_meta = None
        if getattr(self, "note", None):
            created_at = getattr(self.note, "created_at", None)
            # chuyển datetime -> ISO 8601 (an toàn cho JSON)
            created_iso = created_at.isoformat() if hasattr(created_at, "isoformat") else created_at
            note_meta = {
                "id": getattr(self.note, "id", None),
                "created_at": created_iso,
            }

        payload = {
            "count": self.page.paginator.count,
            "page": self.page.number,
            "page_size": self.get_page_size(self.request),
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "note": note_meta,     # metadata về note (nếu có)
            "results": data,       # danh sách item đã serialize
        }
        return ok(payload, message="Fetched")
