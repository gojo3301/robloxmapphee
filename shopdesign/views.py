from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from .models import Product, Order, OrderItem
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def home(request):
    """ หน้า Home - ถ้าเป็นแอดมิน ให้ Redirect ไปที่ /admin-dashboard/ """
    if request.user.is_staff:
        return redirect(reverse("admin_dashboard"))

    query = request.GET.get("search")
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()

    return render(request, "home.html", {"products": products, "search_query": query})

@login_required 
def user_logout(request):
    """ ออกจากระบบ """
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)

def authView(request):
    """ สมัครสมาชิก """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(settings.LOGIN_URL)
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def add_to_cart(request, product_id):
    """ ✅ เพิ่มสินค้าเข้าตะกร้า """
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        order, created = Order.objects.get_or_create(user=request.user, is_completed=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

        if not created:
            order_item.quantity += 1
            order_item.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)

@login_required
def cart_view(request):
    """ ✅ แสดงสินค้าทั้งหมดในตะกร้า + คำนวณราคารวม """
    order = Order.objects.filter(user=request.user, is_completed=False).first()
    items = order.items.all() if order else []

    # ✅ คำนวณราคารวมของแต่ละรายการ
    for item in items:
        item.total_price = item.product.price * item.quantity  # ✅ คำนวณราคาแต่ละชิ้น

    total_price = sum(item.total_price for item in items)  # ✅ คำนวณราคารวมทั้งหมด

    return render(request, "cart.html", {"items": items, "total_price": total_price})



@login_required
def remove_from_cart(request, item_id):
    """ ✅ ลบสินค้าออกจากตะกร้า + คำนวณราคารวมใหม่ """
    if request.method == "POST":
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
        order = item.order
        item.delete()

        # ✅ คำนวณราคารวมใหม่หลังจากลบสินค้า
        total_price = sum(i.product.price * i.quantity for i in order.items.all())

        # ✅ ถ้าตะกร้าว่าง ให้ลบ Order ทิ้ง และตั้งราคารวมเป็น 0
        if not order.items.exists():
            order.delete()
            total_price = 0  

        return JsonResponse({"success": True, "total_price": total_price})  # ✅ ส่ง total_price กลับไปอัปเดต

    return JsonResponse({"success": False}, status=400)



@login_required
def cart_count(request):
    """ ✅ คืนค่าจำนวนสินค้าที่อยู่ในตะกร้า """
    order = Order.objects.filter(user=request.user, is_completed=False).first()
    count = order.items.count() if order else 0
    return JsonResponse({"count": count})

@login_required
def checkout(request):
    """ ✅ แสดงสินค้าที่มีในตะกร้า และเตรียมข้อมูลสำหรับชำระเงิน """
    order = Order.objects.filter(user=request.user, is_completed=False).first()

    if not order or not order.items.exists():
        return render(request, "checkout.html", {"cart_items": [], "total_price": 0})  # ✅ ส่งตะกร้าว่างไปยัง checkout.html

    cart_items = order.items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, "checkout.html", {"cart_items": cart_items, "total_price": total_price})


@login_required
def process_order(request):
    """ ✅ ยืนยันคำสั่งซื้อ และทำให้คำสั่งซื้อนี้เป็นคำสั่งซื้อที่เสร็จสมบูรณ์ """
    if request.method == "POST":
        order, created = Order.objects.get_or_create(user=request.user, is_completed=False)
        
        if not order.items.exists():
            return redirect("cart_view")  # ✅ ถ้าตะกร้าว่างให้กลับไปที่ตะกร้า

        # ✅ ดึงไฟล์สลิปจาก Form
        payment_slip = request.FILES.get("payment_slip")
        if payment_slip:
            order.payment_slip = payment_slip
            order.status = "waiting_payment"  # ✅ เปลี่ยนสถานะเป็น "รอแอดมินตรวจสอบ"

        # ✅ ปิดคำสั่งซื้อแทนการลบสินค้าออก
        order.is_completed = True
        order.save()

        # ✅ สร้างคำสั่งซื้อใหม่เพื่อใช้เป็นตะกร้าครั้งต่อไป
        Order.objects.create(user=request.user, is_completed=False)

        return redirect("payment_status")  # ✅ ไปที่หน้าประวัติการสั่งซื้อ

    return redirect("home")  # ✅ ถ้าไม่ใช่ POST ให้กลับไปหน้าหลัก

@login_required
def payment_status(request):
    """ ✅ แสดงประวัติการสั่งซื้อทั้งหมดของผู้ใช้ """
    orders = Order.objects.filter(user=request.user).order_by("-created_at")  # ✅ เรียงจากรายการใหม่สุด

    return render(request, "payment_status.html", {"orders": orders})