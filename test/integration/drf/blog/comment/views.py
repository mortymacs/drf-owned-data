from rest_framework import viewsets
from owned_data.views import CollaborateType, OwnedDataViewSet
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer



class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
