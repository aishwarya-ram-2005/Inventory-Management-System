import csv
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum, F, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Product, Category, Supplier, StockTransaction, Batch, Alert
from .forms import ProductForm, CategoryForm, SupplierForm, StockTransactionForm, BatchForm
from .services import record_stock_movement

@login_required
def dashboard(request):
    products = Product.objects.filter(is_active=True)
    low_stock = products.filter(quantity__gt=0, quantity__lte=F("reorder_level")).count()
    out_of_stock = products.filter(quantity=0).count()
    total_value = sum((p.inventory_value for p in products), Decimal("0.00"))
    near_expiry = Batch.objects.filter(expiry_date__gte=timezone.localdate(),
        expiry_date__lte=timezone.localdate() + timedelta(days=30)).select_related("product")
    recent = StockTransaction.objects.select_related("product", "created_by")[:7]
    category_data = list(products.values("category__name").annotate(total=Sum("quantity")).order_by("category__name"))
    context = {
        "product_count": products.count(), "low_stock": low_stock, "out_of_stock": out_of_stock,
        "total_value": total_value, "recent": recent, "near_expiry": near_expiry[:5],
        "active_alerts": Alert.objects.filter(is_resolved=False).count(),
        "category_labels": [x["category__name"] for x in category_data],
        "category_values": [x["total"] or 0 for x in category_data],
    }
    return render(request, "inventory/dashboard.html", context)

@login_required
def product_list(request):
    qs = Product.objects.select_related("category", "supplier")
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    status = request.GET.get("status", "")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(description__icontains=q))
    if category:
        qs = qs.filter(category_id=category)
    if status == "low":
        qs = qs.filter(quantity__gt=0, quantity__lte=F("reorder_level"))
    elif status == "out":
        qs = qs.filter(quantity=0)
    elif status == "available":
        qs = qs.filter(quantity__gt=F("reorder_level"))
    return render(request, "inventory/product_list.html", {"products": qs, "categories": Category.objects.all(),
        "q": q, "selected_category": category, "status": status})

@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        product = form.save()
        if product.quantity:
            StockTransaction.objects.create(product=product, transaction_type="IN", quantity=product.quantity,
                reference="Opening stock", notes="Initial quantity entered during product creation.", created_by=request.user)
        messages.success(request, "Product added successfully.")
        return redirect("product_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Add product", "back_url": "product_list"})

@login_required
def product_edit(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Product details updated.")
        return redirect("product_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Edit product", "back_url": "product_list"})

@login_required
@require_POST
def product_delete(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    if obj.transactions.exists():
        messages.error(request, "This product has stock history and cannot be deleted. Mark it inactive instead.")
    else:
        obj.delete()
        messages.success(request, "Product deleted.")
    return redirect("product_list")

@login_required
def category_list(request):
    return render(request, "inventory/category_list.html", {"categories": Category.objects.annotate(product_count=Count("products"))})

@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "Category created."); return redirect("category_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Add category", "back_url": "category_list"})

@login_required
def category_edit(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "Category updated."); return redirect("category_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Edit category", "back_url": "category_list"})

@login_required
def supplier_list(request):
    return render(request, "inventory/supplier_list.html", {"suppliers": Supplier.objects.annotate(product_count=Count("products"))})

@login_required
def supplier_create(request):
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "Supplier created."); return redirect("supplier_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Add supplier", "back_url": "supplier_list"})

@login_required
def supplier_edit(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "Supplier updated."); return redirect("supplier_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Edit supplier", "back_url": "supplier_list"})

@login_required
def transaction_list(request):
    tx = StockTransaction.objects.select_related("product", "created_by")
    kind = request.GET.get("type", "")
    if kind in ("IN", "OUT"):
        tx = tx.filter(transaction_type=kind)
    return render(request, "inventory/transaction_list.html", {"transactions": tx[:250], "selected_type": kind})

@login_required
def transaction_create(request):
    form = StockTransactionForm(request.POST or None)
    if form.is_valid():
        data = form.cleaned_data
        try:
            record_stock_movement(product_id=data["product"].pk, movement_type=data["transaction_type"],
                quantity=data["quantity"], user=request.user, reference=data["reference"], notes=data["notes"])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Stock movement recorded and product quantity updated.")
            return redirect("transaction_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Record stock movement", "back_url": "transaction_list"})

@login_required
def batch_list(request):
    batches = Batch.objects.select_related("product")
    return render(request, "inventory/batch_list.html", {"batches": batches})

@login_required
def batch_create(request):
    form = BatchForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "Batch details saved."); return redirect("batch_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Add batch / expiry details", "back_url": "batch_list"})

@login_required
def alert_list(request):
    alerts = Alert.objects.select_related("product")
    # Refresh low-stock alerts so dashboard remains accurate if product quantities are edited.
    for product in Product.objects.filter(is_active=True):
        if product.quantity <= product.reorder_level:
            Alert.objects.get_or_create(product=product, alert_type=Alert.LOW_STOCK, is_resolved=False,
                defaults={"message": f"{product.name} has only {product.quantity} unit(s) remaining."})
        else:
            Alert.objects.filter(product=product, alert_type=Alert.LOW_STOCK, is_resolved=False).update(is_resolved=True)
    today = timezone.localdate()
    expiring_batches = Batch.objects.filter(
        expiry_date__gte=today, expiry_date__lte=today + timedelta(days=30)
    ).select_related("product")
    for batch in expiring_batches:
        message = f"Batch {batch.batch_code} of {batch.product.name} expires on {batch.expiry_date}."
        Alert.objects.get_or_create(product=batch.product, alert_type=Alert.EXPIRY,
            message=message, is_resolved=False)
    return render(request, "inventory/alert_list.html", {"alerts": Alert.objects.select_related("product")})

@login_required
@require_POST
def alert_resolve(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    alert.is_resolved = True
    alert.save(update_fields=["is_resolved"])
    messages.success(request, "Alert marked as resolved.")
    return redirect("alert_list")

@login_required
def reports(request):
    products = Product.objects.select_related("category")
    tx = StockTransaction.objects.select_related("product")
    return render(request, "inventory/reports.html", {
        "products": products, "transactions": tx[:100],
        "total_units": products.aggregate(v=Sum("quantity"))["v"] or 0,
        "total_value": sum((p.inventory_value for p in products), Decimal("0.00")),
        "low_count": products.filter(quantity__lte=F("reorder_level")).count(),
    })

@login_required
def export_products_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="smartstock_inventory.csv"'
    writer = csv.writer(response)
    writer.writerow(["SKU", "Product", "Category", "Supplier", "Quantity", "Reorder level", "Purchase price", "Selling price", "Stock status"])
    for p in Product.objects.select_related("category", "supplier"):
        writer.writerow([p.sku, p.name, p.category.name, p.supplier.name if p.supplier else "",
            p.quantity, p.reorder_level, p.purchase_price, p.selling_price, p.stock_status])
    return response

@login_required
def export_products_pdf(request):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="smartstock_inventory.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    rows = [["SKU", "Product", "Category", "Qty", "Reorder", "Purchase price", "Status"]]
    for p in Product.objects.select_related("category"):
        rows.append([p.sku, p.name, p.category.name, str(p.quantity), str(p.reorder_level), str(p.purchase_price), p.stock_status])
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#172554")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#dbe3ef")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f3f6fb")]),
        ("FONTSIZE", (0,0), (-1,-1), 8), ("PADDING", (0,0), (-1,-1), 7),
    ]))
    doc.build([Paragraph("SmartStock Inventory Report", styles["Title"]), Spacer(1, 14), table])
    return response
