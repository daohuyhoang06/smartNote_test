from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

from utils.api_response import ok, fail  # <-- helper chung

class OneTokenLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return fail("Missing username/password", status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if not user:
            return fail("Invalid credentials", status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return fail("User is inactive", status=status.HTTP_403_FORBIDDEN)

        # Tạo access token và nhúng claim để FE decode
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # === Các claim tùy biến FE sẽ thấy khi decode ===
        access["sub"] = str(user.id)          # subject
        access["uid"] = user.id
        access["username"] = user.username
        access["email"] = user.email or ""
        # Nếu có role/permissions:
        # access["role"] = user.role or "user"

        token_str = str(access)

        # (tuỳ chọn) thời gian sống cho FE
        exp_ts = int(access["exp"])  # epoch seconds

        return ok(
            data={
                "token": token_str,        # <--- chỉ 1 token duy nhất
                "token_type": "Bearer",
                "expires_at": exp_ts       # FE có thể tính countdown
            },
            message="Logged in"
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return fail("Missing 'refresh' token", status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)   # parse + validate
            token.blacklist()               # đưa vào blacklist
            # 205 Reset Content thường không có body; để trả JSON thống nhất dùng 200 OK
            return ok(message="Logged out")  # data = {}
        except TokenError as e:
            # ví dụ: token hết hạn / đã blacklist / không hợp lệ
            return fail(str(e), status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        outs = OutstandingToken.objects.filter(user=user)
        total = outs.count()
        blacklisted = 0
        for t in outs:
            _, created = BlacklistedToken.objects.get_or_create(token=t)
            if created:
                blacklisted += 1

        # Trả về thống kê để FE biết đã blacklist bao nhiêu token đang còn hiệu lực
        return ok(
            data={"total_outstanding": total, "newly_blacklisted": blacklisted},
            message="Logged out from all devices"
        )
