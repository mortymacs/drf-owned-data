from django.db import models
from django.contrib.auth.models import User
from post.models import Post


class Comment(models.Model):
    body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"User: {self.user.id}, Comment: {self.id}, Post: {self.post.id}"

