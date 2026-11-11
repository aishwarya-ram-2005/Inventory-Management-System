from django import forms
from .models import Product, Category, Supplier, StockTransaction, Batch

class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"

class ProductForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ["sku", "name", "category", "supplier", "description", "purchase_price",
                  "selling_price", "quantity", "reorder_level", "image_url", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

class CategoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

class SupplierForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_person", "email", "phone", "address"]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}

class StockTransactionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ["product", "transaction_type", "quantity", "reference", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2})}

class BatchForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Batch
        fields = ["product", "batch_code", "quantity", "manufactured_on", "expiry_date"]
        widgets = {
            "manufactured_on": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }
