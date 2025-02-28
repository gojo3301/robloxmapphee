from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import authView, home, user_logout  # Import ฟังก์ชันจาก views.py
from .admin_views import admin_dashboard, add_product, delete_product  # ✅ Import จาก admin_views.py

urlpatterns = [
    path("", home, name="home"),
    path("signup/", authView, name="authView"),
    path("logout/", user_logout, name="user_logout"),
    path("accounts/", include("django.contrib.auth.urls")),  # ใช้ระบบ Authentication ของ Django
    path("admin/", admin.site.urls),  # Django Admin Panel
    
    # ✅ Custom Admin Panel
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/add/", add_product, name="add_product"),
    path("admin-dashboard/delete/<int:product_id>/", delete_product, name="delete_product"),
]

# ✅ เสริมการแสดงผลรูปภาพ (Media Files)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
