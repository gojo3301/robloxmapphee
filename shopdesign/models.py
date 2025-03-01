from django.db import models
from django.contrib.auth.models import User 

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="ชื่อสินค้า")
    description = models.TextField(verbose_name="รายละเอียดสินค้า", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคา")
    image = models.ImageField(upload_to='products/', verbose_name="รูปสินค้า")

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "รอยืนยัน"),
        ("waiting_payment", "รอแอดมินตรวจสอบ"),
        ("completed", "สำเร็จ"),
        ("canceled", "ยกเลิก"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)  # คำสั่งซื้อเสร็จสมบูรณ์หรือไม่
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")  # ✅ เพิ่มสถานะ
    payment_slip = models.ImageField(upload_to='payment_slips/', blank=True, null=True)  # ✅ เพิ่มสลิปโอนเงิน

    def __str__(self):
        return f"Order {self.id} - {self.status} by {self.user.username if self.user else 'Guest'}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"