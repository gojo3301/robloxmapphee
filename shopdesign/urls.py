from django.urls import path, include

from .views import authView, home, user_logout

urlpatterns = [
    path("", home, name="home"),
    path("signup/", authView, name="authView"),
    path('logout/', user_logout, name='user_logout'),
    path("accounts/", include("django.contrib.auth.urls")),
]