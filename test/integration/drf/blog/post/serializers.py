from rest_framework import serializers
from .models import Post
from comment.serializers import CommentSerializer


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "body",
            "is_draft",
        )

    def validate(self, attrs):
        attrs["author"] = self.context["request"].user
        return super().validate(attrs)
