from django.urls import path

from .views import HomeView, LandingView, check_requires, UserDetailView

app_name = "main"

urlpatterns = [
    # Home
    path("", HomeView.as_view(), name="home"),
    path("landing/", LandingView.as_view(), name="landing"),
    # User detail page
    path("user/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    # Checks on conditional fields
    path("check_requires/", check_requires, name="check_requires"),
]
