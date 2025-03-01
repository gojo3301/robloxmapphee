from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    authView, home, user_logout, 
    add_to_cart, cart_view, remove_from_cart, cart_count,
)

from .admin_views import admin_dashboard, add_product, delete_product


urlpatterns = [
    # ✅ หน้า Home และ Authentication
    path("", home, name="home"),
    path("signup/", authView, name="authView"),
    path("logout/", user_logout, name="user_logout"),
    path("accounts/", include("django.contrib.auth.urls")),  # ใช้ระบบ Authentication ของ Django

    # ✅ Django Admin Panel
    path("admin/", admin.site.urls),  

    # ✅ Custom Admin Panel
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/add/", add_product, name="add_product"),
    path("admin-dashboard/delete/<int:product_id>/", delete_product, name="delete_product"),

    # ✅ ตะกร้าสินค้า
    path("cart/", cart_view, name="cart_view"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path("cart/count/", cart_count, name="cart_count"),


]

# ✅ เสริมการแสดงผลรูปภาพ (Media Files)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
