from rest_framework import viewsets, permissions
from owned_data.drf import CollaborateType, OwnedDataModelViewSet
from .models import Post
from .serializers import PostSerializer


class AdminPostViewSet(OwnedDataModelViewSet, viewsets.ModelViewSet):

    serializer_class = PostSerializer
    queryset = Post.objects.all()

    # owned-data attributes
    owned_data_fields = ["author"]
    owned_data_collaborators = {
        CollaborateType.GET: ["g:editor"],
        CollaborateType.PUT: ["g:editor"],
        CollaborateType.PATCH: ["g:editor"],
    }
    owned_data_filter_by_fields = True
    owned_data_apply_default_permissions = True
    permission_classes = [permissions.IsAuthenticated]


class PublicPostViewSet(OwnedDataModelViewSet, viewsets.ModelViewSet):

    serializer_class = PostSerializer
    queryset = Post.objects.filter(is_draft=False)

    # owned-data attributes
    owned_data_fields = ["author"]
    owned_data_collaborators = {
        CollaborateType.GET: ["*"],
    }
    owned_data_filter_by_fields = False
    owned_data_apply_default_permissions = True

