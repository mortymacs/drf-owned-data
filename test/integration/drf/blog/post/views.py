from rest_framework import permissions, viewsets
from owned_data.views import CollaborateType, OwnedDataViewSet
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer


class PostViewSet(OwnedDataViewSet, viewsets.ModelViewSet):

    # owner_fields = ["author", "comments__user"]    # AND
    owned_data_fields = [["author"], ["comments__user"]]  # OR
    owned_data_collaborators = {CollaborateType.DELETE: ["g:staff"]}
    # owned_data_fields = ["author"]  # OR
    # owner_fields = [["author", "comments__user"], ["title__icontains='hello'", "author={request_user_id}"]]
    serializer_class = PostSerializer
    queryset = Post.objects.all()



