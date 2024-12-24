from django.urls import path
from . import views

urlpatterns = [
    path('', views.Homepage ,name='Home'),
    path('plot/', views.plot_view, name='plot'),
]