from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Item(models.Model):
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_total_stock(self):
        return self.stocks.aggregate(total=models.Sum('quantity'))['total'] or 0

class Stock(models.Model):
    item = models.ForeignKey(Item, related_name='stocks', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name='stocks', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('item', 'location')

    def __str__(self):
        return f"{self.item.name} @ {self.location.name}: {self.quantity}"

class StockChange(models.Model):
    CHANGE_TYPES = [
        ('IN', 'Incoming Delivery'),
        ('OUT', 'Outgoing Shipment'),
        ('MOVE', 'Internal Move'),
    ]

    item = models.ForeignKey(Item, related_name='stock_changes', on_delete=models.CASCADE)
    source_location = models.ForeignKey(Location, related_name='outgoing_changes', on_delete=models.SET_NULL, null=True, blank=True)
    dest_location = models.ForeignKey(Location, related_name='incoming_changes', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    change_type = models.CharField(max_length=10, choices=CHANGE_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def clean(self):
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        
        if self.change_type == 'IN':
            if not self.dest_location:
                raise ValidationError("Incoming deliveries require a destination location.")
            if self.source_location:
                 raise ValidationError("Incoming deliveries cannot have a source location.")
        
        if self.change_type == 'OUT':
            if not self.source_location:
                raise ValidationError("Outgoing shipments require a source location.")
            if self.dest_location:
                raise ValidationError("Outgoing shipments cannot have a destination location.")
                
        if self.change_type == 'MOVE':
            if not self.source_location or not self.dest_location:
                raise ValidationError("Moves require both source and destination locations.")
            if self.source_location == self.dest_location:
                raise ValidationError("Source and destination locations must be different.")

    def save(self, *args, **kwargs):
        self.clean()
        
        with transaction.atomic():
            # We need to save the StockChange instance first or last? 
            # Usually validation happens before. The logic modifies Stock.
            # If this is a new record (no pk), we update stock.
            
            is_new = self.pk is None
            
            # If it's an edit, we might need to revert previous stock change? 
            # For simplicity in this exercise, let's assume StockChanges are immutable-ish or we only handle creation logic here.
            # If we allow editing, it gets complex. I'll assume creation only for the stock update logic.
            
            if is_new:
                if self.source_location:
                    # Lock the stock row for update
                    source_stock, created = Stock.objects.select_for_update().get_or_create(item=self.item, location=self.source_location)
                    if source_stock.quantity < self.quantity:
                        raise ValidationError(f"Not enough stock at {self.source_location.name}. Available: {source_stock.quantity}")
                    source_stock.quantity -= self.quantity
                    source_stock.save()

                if self.dest_location:
                    dest_stock, created = Stock.objects.select_for_update().get_or_create(item=self.item, location=self.dest_location)
                    dest_stock.quantity += self.quantity
                    dest_stock.save()

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_change_type_display()} - {self.item.name} ({self.quantity})"