from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
from .models import Product, Order
from .forms import ProductForm

# ✅ ตรวจสอบว่าเป็น Admin
def is_admin(user):
    return user.is_staff  

# ✅ แสดงหน้า Admin Dashboard
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    products = Product.objects.all()
    return render(request, "admin_dashboard.html", {"products": products})

# ✅ เพิ่มสินค้า
@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ เพิ่มสินค้าสำเร็จ!")
            return redirect(reverse("admin_dashboard"))  
    else:
        form = ProductForm()
    return render(request, "add_product.html", {"form": form})

# ✅ ลบสินค้า
@login_required
@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)  
    product.delete()
    messages.success(request, "🗑️ ลบสินค้าสำเร็จ!")
    return redirect(reverse("admin_dashboard"))  

# ✅ เพิ่ม/ลดจำนวนสินค้า (สามารถกำหนดจำนวนที่เพิ่ม/ลดได้)
@login_required
@user_passes_test(is_admin)
def update_stock(request, product_id, action, amount=1):
    product = get_object_or_404(Product, id=product_id)
    
    amount = int(amount)  # ✅ แปลงค่าจำนวนที่รับมาเป็นตัวเลข

    if action == "increase":
        product.stock += amount  # ✅ เพิ่มจำนวนสินค้าตามค่าที่ระบุ
        messages.success(request, f"✅ เพิ่ม {amount} ชิ้นให้ {product.name} สำเร็จ!")
    elif action == "decrease":
        if product.stock >= amount:
            product.stock -= amount  # ✅ ลดจำนวนสินค้าตามค่าที่ระบุ
            messages.warning(request, f"⚠️ ลด {amount} ชิ้นจาก {product.name} สำเร็จ!")
        else:
            messages.error(request, f"❌ ไม่สามารถลดสินค้าได้ เพราะมีเพียง {product.stock} ชิ้น!")
    
    product.save()
    return redirect(reverse("admin_dashboard"))

# ✅ แสดงรายการสั่งซื้อที่รอตรวจสอบ
@login_required
@user_passes_test(is_admin)
def admin_check_orders(request):
    orders = Order.objects.filter(status="waiting_payment")
    return render(request, "admin_check_orders.html", {"orders": orders})

# ✅ อนุมัติหรือปฏิเสธคำสั่งซื้อ
@login_required
@user_passes_test(is_admin)
def update_order_status(request, order_id, action):
    order = get_object_or_404(Order, id=order_id)

    if action == "approve":
        order.status = "completed"  # ✅ อนุมัติสลิป
        messages.success(request, f"✅ คำสั่งซื้อ #{order.id} ได้รับการอนุมัติแล้ว!")
    elif action == "reject":
        order.status = "rejected"  # ❌ ปฏิเสธสลิป
        messages.error(request, f"❌ คำสั่งซื้อ #{order.id} ถูกปฏิเสธ!")

    order.save()
    return redirect(reverse("admin_check_orders"))
