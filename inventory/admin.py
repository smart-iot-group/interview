from django.contrib import admin
from .models import Category, Item, Location, Stock, StockChange

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'get_total_stock')
    search_fields = ('name', 'sku')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('item', 'location', 'quantity', 'updated_at')
    list_filter = ('location', 'item')

@admin.register(StockChange)
class StockChangeAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'change_type', 'item', 'quantity', 'source_location', 'dest_location')
    list_filter = ('change_type', 'timestamp')
    ordering = ('-timestamp',)