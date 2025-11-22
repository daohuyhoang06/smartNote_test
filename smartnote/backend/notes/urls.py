from django.urls import path
from . import views
from .views import ( 
    NoteDetailView,
    NoteDetailWithTopicsPagination,
    TopicListCreateView,
    TopicDetailView,
    AddWordToTopicView,
    DeleteWordFromTopicView,
    TopicSearchView
)

urlpatterns = [
    # Note (sổ tay của user)
    path("note/all/", NoteDetailView.as_view(), name="note-detail"),  # trả về toàn bộ topics trong note
    path("note/paginated/", NoteDetailWithTopicsPagination.as_view(), name="note-detail-paginated"),

    # Topic (ghi chú trong Note)
    path("topics/", TopicListCreateView.as_view(), name="topic-list-create"),
    path("topic/<int:pk>/", TopicDetailView.as_view(), name="topic-detail"),
    path("topic/<int:pk>/add-word/<str:query>/", AddWordToTopicView.as_view(), name="topic-add-words"),
    path(
        "topic/<int:pk>/delete-word/<int:voca_topic_id>/<int:voca_detail_id>/",
        DeleteWordFromTopicView.as_view(),
        name="delete-word-from-topic",
    ),
    path("topics/search/", TopicSearchView.as_view(), name="topic-search"),
   
]
