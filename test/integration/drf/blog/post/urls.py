from django.urls import path, include

from rest_framework import routers

from post.views import PublicPostViewSet, AdminPostViewSet

router = routers.DefaultRouter()
router.register("me/posts", AdminPostViewSet, basename="admin_post")
router.register("posts", PublicPostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
]
