from rest_framework import permissions

class IsOwnerOnly(permissions.BasePermission):
    """
    Quyền cho Note/Notebook:
    - User chỉ được đọc và thao tác (sửa, xóa) trên dữ liệu của chính mình.
    - Không có chuyện admin hay user khác đọc được notes/notebooks của người khác.
    """

    def has_object_permission(self, request, view, obj):
        # Nếu là Notebook
        if hasattr(obj, "user"):
            return obj.user == request.user

        # Nếu là Note (lấy user qua notebook)
        if hasattr(obj, "note"):
            return obj.note.user == request.user

        return False
