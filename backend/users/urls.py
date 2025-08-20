from django.urls import path

from users.views import GoogleLoginAPIView, SignupView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("google/", GoogleLoginAPIView.as_view(), name="google-login"),
]
