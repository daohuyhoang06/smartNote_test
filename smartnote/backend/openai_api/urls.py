from django.urls import path
from .views import GenerateFillInBlankView

urlpatterns = [
    path("gen_fill_blank/", GenerateFillInBlankView.as_view(), name="gen_fill_blank"),
]
