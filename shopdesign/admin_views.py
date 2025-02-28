from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import Product
from .forms import ProductForm

# เช็คว่าเป็น Admin หรือไม่
def is_admin(user):
    return user.is_staff  # ✅ ตรวจสอบว่าเป็น staff หรือ admin

# ✅ ฟังก์ชันแสดงหน้า Admin Dashboard
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    products = Product.objects.all()
    return render(request, "admin_dashboard.html", {"products": products})

# ✅ ฟังก์ชันเพิ่มสินค้า
@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse("admin_dashboard"))  # ✅ ใช้ reverse()
    else:
        form = ProductForm()
    return render(request, "add_product.html", {"form": form})

# ✅ ฟังก์ชันลบสินค้า
@login_required
@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # ✅ ใช้ get_object_or_404 ป้องกัน error
    product.delete()
    return redirect(reverse("admin_dashboard"))  # ✅ ใช้ reverse()
