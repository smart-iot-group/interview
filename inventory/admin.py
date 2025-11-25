from django.contrib import admin
from .models import Category, Product, Location, ProductLocation

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Location)
admin.site.register(ProductLocation)
