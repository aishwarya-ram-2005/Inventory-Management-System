from django.contrib import admin
from .models import Category, Supplier, Product, StockTransaction, Batch, Alert

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "quantity", "reorder_level", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("sku", "name")

admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(StockTransaction)
admin.site.register(Batch)
admin.site.register(Alert)
