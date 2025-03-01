from django.db import models
from django.contrib.auth.models import User 

class Product(models.Model):
    BATTERY_TYPES = [
        ("mf", "ไม่เติมน้ำกลั่น"), 
        ("hybrid", "ไฮบริด"), 
        ("wet", "เติมน้ำกลั่น"),
    ]

    name = models.CharField(max_length=255, verbose_name="ชื่อสินค้า")
    description = models.TextField(verbose_name="รายละเอียดสินค้า", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคา")
    image = models.ImageField(upload_to='products/', verbose_name="รูปสินค้า")
    stock = models.PositiveBigIntegerField(default=0, verbose_name="จำนวนสินค้า")
    battery_type = models.CharField(max_length=10, choices=BATTERY_TYPES, verbose_name="ประเภทแบตเตอรี่", default="mf")

    def __str__(self):
        return f"{self.name} - {self.get_battery_type_display()} ({self.stock} ชื้น)"

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "รอยืนยัน"),
        ("waiting_payment", "รอแอดมินตรวจสอบ"),
        ("approved", "สลิปถูกต้อง"),
        ("rejected", "สลิปไม่ถูกต้อง"),
        ("completed", "สำเร็จ"),
        ("rejected", "ถูกปฏิเสธ"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_slip = models.ImageField(upload_to='payment_slips/', blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_orders")

    @property
    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} ({self.get_status_display()})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
