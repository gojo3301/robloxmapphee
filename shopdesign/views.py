from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from django.conf import settings
from .models import Product

@login_required
def home(request):
    # ถ้าผู้ใช้เป็น Admin ให้ Redirect ไปที่ /admin-dashboard/
    if request.user.is_staff:
        return redirect(reverse("admin_dashboard"))  # ✅ ใช้ reverse() เพื่อความปลอดภัย

    query = request.GET.get("search")  # รับค่าการค้นหาจาก URL
    if query:
        products = Product.objects.filter(name__icontains=query)  # ค้นหาตามชื่อสินค้า
    else:
        products = Product.objects.all()  # แสดงสินค้าทั้งหมดถ้าไม่มีการค้นหา

    return render(request, "home.html", {"products": products, "search_query": query})

@login_required 
def user_logout(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)  # ✅ ป้องกัน ImportError โดยใช้ settings

def authView(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(settings.LOGIN_URL)  # ✅ ใช้ reverse() แทน "shopdesign:login"
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
