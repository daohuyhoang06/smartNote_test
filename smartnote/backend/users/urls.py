from django.urls import path
from .views import UserListCreateView, UserSelfView
from .views_auth import OneTokenLoginView
urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('user/me/', UserSelfView.as_view(), name='user-self'),
    path("login/", OneTokenLoginView.as_view(), name="one_token_login"),
    # path("logout/", LogoutView.as_view(), name="logout"),
    # path("logout_all/", LogoutAllView.as_view(), name="logout_all"),
]
