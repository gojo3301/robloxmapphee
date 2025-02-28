from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="ชื่อสินค้า")
    description = models.TextField(verbose_name="รายละเอียดสินค้า", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคา")
    image = models.ImageField(upload_to='products/', verbose_name="รูปสินค้า")

    def __str__(self):
        return self.name