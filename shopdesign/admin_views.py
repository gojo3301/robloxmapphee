from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
from .models import Product, Order
from .forms import ProductForm
from django.db.models import Sum, Count
import urllib, base64
import matplotlib.pyplot as plt
from .models import Order, OrderItem, Product
import io

def generate_graph(request):
    # 1. Total Sales of Products (All Battery Types)
    sales_data = (
        OrderItem.objects
        .values("product__name")
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")
    )

    product_names = [item["product__name"] for item in sales_data]
    total_sold = [item["total_sold"] for item in sales_data]
    
    plt.figure(figsize=(8, 5))
    plt.bar(product_names, total_sold)
    plt.xlabel("Product")
    plt.ylabel("Total Sales")
    plt.title("Total Sales of Products (All Battery Types)")
    plt.xticks(rotation=45, ha="right")
    sales_chart = save_plot_to_base64()
    
    # 2. Order Status Distribution
    order_status_data = (
        Order.objects.values("status")
        .annotate(total=Count("id"))
    )
    status_labels = [item["status"] for item in order_status_data]
    order_counts = [item["total"] for item in order_status_data]
    
    plt.figure(figsize=(6, 6))
    plt.pie(order_counts, labels=status_labels, autopct="%1.1f%%", startangle=140)
    plt.title("Order Status Distribution")
    order_status_chart = save_plot_to_base64()
    
    # 3. Inventory of Each Battery Type
    battery_stock_data = (
        Product.objects.values("battery_type")
        .annotate(total_stock=Sum("stock"))
    )
    battery_labels = [item["battery_type"] for item in battery_stock_data]
    battery_stocks = [item["total_stock"] for item in battery_stock_data]
    
    plt.figure(figsize=(8, 5))
    plt.bar(battery_labels, battery_stocks, color=['blue', 'green', 'red'])
    plt.xlabel("Battery Type")
    plt.ylabel("Stock Quantity")
    plt.title("Inventory of Each Battery Type")
    battery_stock_chart = save_plot_to_base64()
    
    # 4. Monthly Revenue
    monthly_revenue_data = (
        Order.objects
        .filter(status="completed")
        .values("created_at__year", "created_at__month")
        .annotate(total_revenue=Sum("items__product__price"))
        .order_by("created_at__year", "created_at__month")
    )
    months = [f"{item['created_at__year']}-{item['created_at__month']:02d}" for item in monthly_revenue_data]
    revenues = [item["total_revenue"] for item in monthly_revenue_data]
    
    plt.figure(figsize=(8, 5))
    plt.plot(months, revenues, marker='o', linestyle='-')
    plt.xlabel("Month")
    plt.ylabel("Total Revenue (THB)")
    plt.title("Monthly Revenue")
    plt.xticks(rotation=45)
    revenue_chart = save_plot_to_base64()
    
    return {
        "sales_chart": sales_chart,
        "order_status_chart": order_status_chart,
        "battery_stock_chart": battery_stock_chart,
        "revenue_chart": revenue_chart,
    }

def save_plot_to_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def analytics_view(request):
    charts = generate_graph(request)
    return render(request, "all_graphs.html", charts)


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

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_product(request, product_id):
    """ ✅ Admin แก้ไขสินค้า """
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ อัปเดตสินค้า {product.name} สำเร็จ!")
            return redirect("admin_dashboard")
    else:
        form = ProductForm(instance=product)

    return render(request, "edit_product.html", {"form": form, "product": product})