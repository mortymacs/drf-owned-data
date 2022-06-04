from rest_framework import permissions, status, views
from rest_framework.response import Response
from .serializers import LoginSerializer
from django.contrib.auth import authenticate, logout
from rest_framework import generics
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """Register user view."""

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginView(views.APIView):
    """Login view."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Handle POST method to authenticate a user."""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            username=serializer.data["username"],
            password=serializer.data["password"],
        )
        if not user:
            return Response(
                data={"message": "invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                data={"message": "user is not activated yet"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = Token.objects.get_or_create(user=user)
        return Response(data={"token": token[0].key})


class LogoutView(views.APIView):
    """Logout view."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Handle GET request to logout a user."""
        request.user.auth_token.delete()
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
