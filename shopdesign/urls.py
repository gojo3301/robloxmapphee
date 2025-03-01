from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    auth_view, home, user_logout,  # ✅ แก้จาก `auth_View` เป็น `auth_view`
    add_to_cart, cart_view, remove_from_cart, cart_count,
    checkout, process_order, payment_status, plot_all_graphs
)
from .admin_views import (
    admin_dashboard, add_product, delete_product, update_stock,
    admin_check_orders, update_order_status
)

urlpatterns = [
    # ✅ หน้า Home และ Authentication
    path("", home, name="home"),
    path("signup/", auth_view, name="authView"),  # ✅ แก้จาก `auth_View` เป็น `auth_view`
    path("logout/", user_logout, name="user_logout"),
    path("accounts/", include("django.contrib.auth.urls")),

    # ✅ Custom Admin Panel
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/add/", add_product, name="add_product"),
    path("admin-dashboard/delete/<int:product_id>/", delete_product, name="delete_product"),
    path("admin-dashboard/update-stock/<int:product_id>/<str:action>/", update_stock, name="update_stock"),

    # ✅ ตรวจสอบคำสั่งซื้อ
    path("admin-dashboard/orders/", admin_check_orders, name="admin_check_orders"),
    path("admin-dashboard/orders/<int:order_id>/<str:action>/", update_order_status, name="update_order_status"),

    # ✅ ตะกร้าสินค้า
    path("cart/", cart_view, name="cart_view"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path("cart/count/", cart_count, name="cart_count"),

    # ✅ หน้าชำระเงิน
    path("checkout/", checkout, name="checkout"),
    path("order/process/", process_order, name="process_order"),
    path("payment-status/", payment_status, name="payment_status"),

    path('all-graphs/', plot_all_graphs, name='all_graphs'),
]

# ✅ เสริมการแสดงผลรูปภาพ (Media Files)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
