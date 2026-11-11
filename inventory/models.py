from django.conf import settings
from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=25, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return self.name

class Product(models.Model):
    sku = models.CharField("SKU / Product code", max_length=40, unique=True)
    name = models.CharField(max_length=180)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    description = models.TextField(blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return f"{self.name} ({self.sku})"
    @property
    def stock_status(self):
        if self.quantity == 0:
            return "Out of stock"
        if self.quantity <= self.reorder_level:
            return "Low stock"
        return "In stock"
    @property
    def inventory_value(self):
        return self.quantity * self.purchase_price

class StockTransaction(models.Model):
    STOCK_IN = "IN"
    STOCK_OUT = "OUT"
    TYPES = [(STOCK_IN, "Stock In"), (STOCK_OUT, "Stock Out")]
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="transactions")
    transaction_type = models.CharField(max_length=3, choices=TYPES)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.get_transaction_type_display()} · {self.product.sku} · {self.quantity}"

class Batch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="batches")
    batch_code = models.CharField(max_length=80)
    quantity = models.PositiveIntegerField(default=0)
    manufactured_on = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["expiry_date", "batch_code"]
        unique_together = ("product", "batch_code")
    def __str__(self):
        return f"{self.product.name} · {self.batch_code}"
    @property
    def is_expired(self):
        return bool(self.expiry_date and self.expiry_date < timezone.localdate())
    @property
    def is_near_expiry(self):
        if not self.expiry_date:
            return False
        days = (self.expiry_date - timezone.localdate()).days
        return 0 <= days <= 30

class Alert(models.Model):
    LOW_STOCK = "LOW_STOCK"
    EXPIRY = "EXPIRY"
    TYPES = [(LOW_STOCK, "Low stock"), (EXPIRY, "Expiry")]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="alerts")
    alert_type = models.CharField(max_length=20, choices=TYPES)
    message = models.CharField(max_length=255)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return self.message
