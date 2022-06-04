from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class RegisterSerializer(serializers.ModelSerializer):
    """Register serializer."""

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def to_representation(self, instance):
        """DRF built-in method."""
        return {
            "username": instance.username,
            "email": instance.email,
        }

    def validate(self, attrs):
        """Customized 'validate' method to encrypt password."""
        if attrs.get("password"):
            attrs["password"] = make_password(attrs["password"])
        return super().validate(attrs)


class LoginSerializer(serializers.Serializer):
    """Login serializer."""

    username = serializers.CharField()
    password = serializers.CharField()


