from rest_framework import permissions, viewsets
from owned_data.drf import CollaborateType, OwnedDataModelViewSet
from .models import Post
from .serializers import PostSerializer


class PostViewSet(OwnedDataModelViewSet, viewsets.ModelViewSet):

    # owner_fields = ["author", "comments__user"]    # AND
    owned_data_fields = [["author"], ["comments__user"]]  # OR
    owned_data_collaborators = {CollaborateType.DELETE: ["g:staff"]}
    # owned_data_fields = ["author"]  # OR
    # owner_fields = [["author", "comments__user"], ["title__icontains='hello'", "author={request_user_id}"]]
    serializer_class = PostSerializer
    queryset = Post.objects.all()



