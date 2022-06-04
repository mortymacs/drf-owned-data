from django.urls import path, include

from account.views import LoginView, LogoutView, RegisterView


urlpatterns = [
    path("posts/", include(("post.urls", "post"))),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
