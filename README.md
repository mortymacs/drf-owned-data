# Owned Data

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/mortymacs/owned_data/Python%20package)](https://github.com/mortymacs/owned_data/actions/workflows/python-test.yml)
[![PyPi version](https://badgen.net/pypi/v/owned_data/)](https://pypi.org/project/owned_data)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/owned_data.svg)](https://pypi.python.org/pypi/owned_data/)
[![PyPI version fury.io](https://badge.fury.io/py/owned_data.svg)](https://pypi.python.org/pypi/owned_data/)
[![PyPI download month](https://img.shields.io/pypi/dm/owned_data.svg)](https://pypi.python.org/pypi/owned_data/)

Data ownership library based on data columns (filter and permission).

Supported frameworks:
    * DjangoRestFramework

## Quick Start

```shell
pip install owned_data
```

Sample:
```python
owned_data_fields = [
    "user",
    "title__icontains=draft",
]
owned_data_collaborators = {
    CollaborateType.GET: ["*"],
    CollaborateType.DELETE: ["g:admin"],
    CollaborateType.POST: ["g:bot", "g:platform"],
}
```
`owned_data_fields` will be translated into: `Model.filter(user=request.id, comment__user=request.id, title__icontains='draft')`.
By defining `owned_data_collaborators` we let other users, groups, or permissions can have action
on the owned-data records.

### Fields format:

It can be a list of strings like `["user", "author"]` that which will be translated into:
```python
self.get_query().filter(Q(user=request.user) & Q(author=request.user))
```

It also can be a list of list of strings like `[["user"], ["author", "is_draft=True"]]` which will be translate into:
```python
self.get_query().filter(Q(user=request.user) | Q(Q(author=request.user) & Q(is_draft=True)))
```

Collaborators format:

| Prefix | Description | Sample                                               |
|--------|-------------|------------------------------------------------------|
| u:     | user        | `["u:admin", "u:test"]`                              |
| g:     | group       | `["g:editors", "g:customers"]`                       |
| p:     | permission  | `["p:change_user", "p:delete_session"]`              |
| f:     | function    | `["f:validate_permission", "f:Permission.validate"]` |
| *      | anyone      | `["*"]`                                              |

> **Note:** to use `f:`, if it doesn't have ".", it looks for the method inside the current class which starts with `owned_data_collaborate_`.
For example: `owned_data_collaborate_bot`

## Sample

We need to create a sample model which consists of blog Post and Comment models.

_models.py_
```python
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"User: {self.author.id}, Post: {self.title}"


class Comment(models.Model):
    body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"User: {self.user.id}, Comment: {self.id}, Post: {self.post.id}"
```

And a serializer based on ModelSerializer.

_serializers.py_
```python
from rest_framework import serializers

from .models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):

    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "body",
            "comments",
        )
```

Now it's time for views.

_views.py_
```python
from rest_framework import viewsets
from owned_data.views import OwnedDataViewSet

from .serializers import PostSerializer, CommentSerializer


class PostViewSet(OwnedDataModelViewSet):
    owned_data_fields = ["author"]
    owned_data_collaborators = {
        CollaborateType.GET: ["*"],
        CollaborateType.PUT: ["g:editors"],
        CollaborateType.PATCH: ["g:editors"],
        CollaborateType.DELETE: ["f:bot"],
    }
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def owned_data_collaborate_bot(self):
        return Group.objects.get(name="bot")


class CommentViewSet(OwnedDataModelViewSet):
    owned_data_fields = ["user"]
    owned_data_collaborators = {
        CollaborateType.GET: ["*"],
    }
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
```

## Issue

In case of any problem or bug, please [file an issue](https://github.com/mortymacs/drf-owned-data/issues/new) 📌

## Contribution

That's great if you want to contribute to the project. Please [file an issue](https://github.com/mortymacs/drf-owned-data/issues/new) and send your PR 🎉

Before sending the PR, please check your changes by `Make test` and `Make lint`.

## License

Please read the [license](./LICENSE) agreement.
