from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):
    command = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timeout = models.PositiveIntegerField(default=60)

    def __str__(self):
        return f"Job: {self.user.id} [timeout:{self.timeout}]"

