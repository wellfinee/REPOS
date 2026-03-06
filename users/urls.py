from django.urls import path
from .views import StudentAdminUpdateView, UserProfileView, UserSearchView

urlpatterns = [
    path("users/<uuid:user_id>/", UserProfileView.as_view(), name="user-profile"),
    path("users/<uuid:user_id>/profile/", UserProfileView.as_view(), name="user-profile-legacy"),
    path("users/search/", UserSearchView.as_view(), name="user-search"),
    path("students/<uuid:user_id>/", StudentAdminUpdateView.as_view(), name="student-admin-patch"),
]
