from django.urls import path
from . import views

urlpatterns = [
    path('search/word/<str:pk>/', views.searchWord),
    path('search/kanji/<str:pk>/', views.searchKanji),
]