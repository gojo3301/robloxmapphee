from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from .models import Product, Order, OrderItem
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import matplotlib.pyplot as plt
from collections import Counter
from django.shortcuts import render
from .models import Order, OrderItem, Product
import io
import urllib, base64

@login_required
def home(request):
    """ ✅ หน้า Home - ถ้าเป็นแอดมิน ให้ Redirect ไปที่ /admin-dashboard/ """
    if request.user.is_staff:
        return redirect(reverse("admin_dashboard"))

    query = request.GET.get("search")
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    return render(request, "home.html", {"products": products, "search_query": query})

def auth_view(request):
    """ ✅ ฟังก์ชันสมัครสมาชิก """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # ✅ ล็อกอินอัตโนมัติหลังสมัครสมาชิก
            return redirect("home")  # ✅ ไปที่หน้าหลักหลังจากสมัคร
    else:
        form = UserCreationForm()
    
    return render(request, "registration/signup.html", {"form": form})

@login_required 
def user_logout(request):
    """ ✅ ออกจากระบบ """
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)

@login_required
def add_to_cart(request, product_id):
    """ ✅ เพิ่มสินค้าเข้าตะกร้า และลด stock """
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        # ตรวจสอบว่าสินค้ายังมีใน stock หรือไม่
        if product.stock <= 0:
            return JsonResponse({"success": False, "error": "สินค้าหมด"}, status=400)

        order, created = Order.objects.get_or_create(user=request.user, is_completed=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

        if not created:
            order_item.quantity += 1
            order_item.save()

        # ✅ ลด stock ลง 1 หลังจากเพิ่มลงตะกร้า
        product.stock -= 1
        product.save()

        return JsonResponse({"success": True, "new_stock": product.stock})

    return JsonResponse({"success": False}, status=400)

@login_required
def cart_view(request):
    """ ✅ แสดงสินค้าทั้งหมดในตะกร้า """
    order = Order.objects.filter(user=request.user, is_completed=False).first()
    items = order.items.all() if order else []
    total_price = sum(item.product.price * item.quantity for item in items) if items else 0

    return render(request, "cart.html", {"items": items, "total_price": total_price})

@login_required
def remove_from_cart(request, item_id):
    """ ✅ ลบสินค้าออกจากตะกร้า และคืนจำนวน stock """
    if request.method == "POST":
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
        order = item.order
        product = item.product  # ✅ ดึงสินค้าออกมา

        # ✅ คืน stock กลับเข้าไป
        product.stock += item.quantity
        product.save()

        # ✅ ลบสินค้าออกจากตะกร้า
        item.delete()

        # ✅ คำนวณราคารวมใหม่หลังจากลบสินค้า
        total_price = sum(i.product.price * i.quantity for i in order.items.all())

        # ✅ ถ้าตะกร้าว่าง ให้ลบ Order ทิ้ง และตั้งราคารวมเป็น 0
        if not order.items.exists():
            order.delete()
            total_price = 0  

        return JsonResponse({"success": True, "total_price": total_price, "new_stock": product.stock})  

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
        messages.error(request, "❌ ไม่มีสินค้าในตะกร้า!")
        return redirect(reverse("cart_view"))

    cart_items = order.items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, "checkout.html", {"cart_items": cart_items, "total_price": total_price})

@login_required
def process_order(request):
    """ ✅ อัปโหลดสลิป และยืนยันคำสั่งซื้อ """
    if request.method == "POST":
        order = get_object_or_404(Order, user=request.user, is_completed=False)

        if not order.items.exists():
            messages.error(request, "❌ ไม่มีสินค้าในตะกร้า!")
            return redirect(reverse("cart_view"))

        payment_slip = request.FILES.get("payment_slip")
        if not payment_slip:
            messages.error(request, "❌ กรุณาอัปโหลดสลิปการชำระเงิน!")
            return redirect(reverse("checkout"))

        order.payment_slip = payment_slip
        order.status = "waiting_payment"
        order.is_completed = True
        order.save()

        messages.success(request, "📤 ส่งหลักฐานการชำระเงินเรียบร้อย!")

        # ✅ สร้างคำสั่งซื้อใหม่ให้ผู้ใช้สามารถสั่งซื้อต่อไป
        Order.objects.create(user=request.user, is_completed=False)

        return redirect(reverse("payment_status"))

    return redirect(reverse("home"))

@login_required
def payment_status(request):
    """ ✅ แสดงประวัติคำสั่งซื้อ """
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "payment_status.html", {"orders": orders})

# ✅ Admin ตรวจสอบคำสั่งซื้อ
@login_required
@user_passes_test(lambda u: u.is_staff)  # ✅ ป้องกัน User ทั่วไปเข้าถึง
def admin_check_orders(request):
    """ ✅ แสดงรายการสั่งซื้อที่ต้องตรวจสอบ """
    orders = Order.objects.filter(status="waiting_payment")
    return render(request, "admin_check_orders.html", {"orders": orders})

@login_required
@user_passes_test(lambda u: u.is_staff)  # ✅ ป้องกัน User ทั่วไปเข้าถึง
def update_order_status(request, order_id, action):
    """ ✅ Admin อนุมัติหรือปฏิเสธสลิป """
    order = get_object_or_404(Order, id=order_id)

    if request.user == order.user:
        messages.error(request, "❌ คุณไม่สามารถอนุมัติคำสั่งซื้อของตัวเองได้!")
        return redirect(reverse("admin_check_orders"))

    if not order.payment_slip:
        messages.error(request, "❌ ไม่สามารถอนุมัติคำสั่งซื้อที่ไม่มีสลิปได้!")
        return redirect(reverse("admin_check_orders"))

    if action == "approve":
        order.status = "completed"
        messages.success(request, f"✅ คำสั่งซื้อ #{order.id} อนุมัติแล้ว!")
    elif action == "reject":
        order.status = "rejected"
        messages.error(request, f"❌ คำสั่งซื้อ #{order.id} ถูกปฏิเสธ!")

    order.save()
    return redirect(reverse("admin_check_orders"))

# ฟังก์ชันสำหรับการ plot ทั้งหมด
def plot_all_graphs(request):
    # 1. ยอดขายรวมตามวัน
    completed_orders = Order.objects.filter(status='completed')
    order_dates = [order.created_at.date() for order in completed_orders]
    order_counts = Counter(order_dates)
    dates = list(order_counts.keys())
    counts = list(order_counts.values())
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(dates, counts, color='blue')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Number of Completed Orders')
    ax1.set_title('Completed Orders by Date')
    buffer1 = io.BytesIO()
    plt.savefig(buffer1, format='png')
    buffer1.seek(0)
    image_data1 = buffer1.getvalue()
    graph_url1 = base64.b64encode(image_data1).decode('utf-8')

    # 2. สินค้าที่ขายดีที่สุด
    product_sales = {}
    for order in completed_orders:
        for item in order.items.all():
            product = item.product
            total_price = item.quantity * product.price
            if product in product_sales:
                product_sales[product] += total_price
            else:
                product_sales[product] = total_price
    products = list(product_sales.keys())
    sales = list(product_sales.values())
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.barh(products, sales, color='green')
    ax2.set_xlabel('Total Sales (Baht)')
    ax2.set_ylabel('Product')
    ax2.set_title('Top Selling Products')
    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png')
    buffer2.seek(0)
    image_data2 = buffer2.getvalue()
    graph_url2 = base64.b64encode(image_data2).decode('utf-8')

    # 3. จำนวนคำสั่งซื้อตามสถานะ
    status_counts = Counter(order.status for order in completed_orders)
    statuses = list(status_counts.keys())
    counts_status = list(status_counts.values())
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.bar(statuses, counts_status, color='purple')
    ax3.set_xlabel('Order Status')
    ax3.set_ylabel('Number of Orders')
    ax3.set_title('Orders by Status')
    buffer3 = io.BytesIO()
    plt.savefig(buffer3, format='png')
    buffer3.seek(0)
    image_data3 = buffer3.getvalue()
    graph_url3 = base64.b64encode(image_data3).decode('utf-8')

    # 4. ยอดขายรวมตามสินค้า
    product_sales = {}
    for order in completed_orders:
        for item in order.items.all():
            product = item.product
            total_price = item.quantity * product.price
            if product in product_sales:
                product_sales[product] += total_price
            else:
                product_sales[product] = total_price
    products = list(product_sales.keys())
    sales = list(product_sales.values())
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    ax4.barh(products, sales, color='orange')
    ax4.set_xlabel('Total Sales (Baht)')
    ax4.set_ylabel('Product')
    ax4.set_title('Sales by Product')
    buffer4 = io.BytesIO()
    plt.savefig(buffer4, format='png')
    buffer4.seek(0)
    image_data4 = buffer4.getvalue()
    graph_url4 = base64.b64encode(image_data4).decode('utf-8')

    # ส่งข้อมูลทั้งหมดไปที่ template
    return render(request, 'all_graphs.html', {
        'graph_url1': graph_url1,
        'graph_url2': graph_url2,
        'graph_url3': graph_url3,
        'graph_url4': graph_url4,
    })
