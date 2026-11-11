from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product, StockTransaction, Alert

@transaction.atomic
def record_stock_movement(*, product_id, movement_type, quantity, user, reference="", notes=""):
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")
    product = Product.objects.select_for_update().get(pk=product_id)
    if movement_type == StockTransaction.STOCK_OUT and quantity > product.quantity:
        raise ValidationError(f"Not enough stock. Available quantity: {product.quantity}.")
    if movement_type == StockTransaction.STOCK_IN:
        product.quantity += quantity
    elif movement_type == StockTransaction.STOCK_OUT:
        product.quantity -= quantity
    else:
        raise ValidationError("Choose a valid stock movement.")
    product.save(update_fields=["quantity", "updated_at"])
    movement = StockTransaction.objects.create(
        product=product, transaction_type=movement_type, quantity=quantity,
        reference=reference, notes=notes, created_by=user
    )
    if product.quantity <= product.reorder_level:
        Alert.objects.get_or_create(
            product=product, alert_type=Alert.LOW_STOCK, is_resolved=False,
            defaults={"message": f"{product.name} has only {product.quantity} unit(s) remaining."}
        )
    else:
        Alert.objects.filter(product=product, alert_type=Alert.LOW_STOCK, is_resolved=False).update(is_resolved=True)
    return movement
