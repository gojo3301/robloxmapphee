from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "image", "stock", "battery_type"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "battery_type", "image"]
        labels = {
            "name": "ชื่อสินค้า",
            "description": "รายละเอียดสินค้า",
            "price": "ราคา",
            "stock": "จำนวนสินค้า",
            "battery_type": "ประเภทแบตเตอรี่",
            "image": "รูปสินค้า"
        }
