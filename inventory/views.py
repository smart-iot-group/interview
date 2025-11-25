from django.shortcuts import render
from .models import Product, Location

# Create your views here.

def get_products(request):
    # Logic to retrieve products from the database
    products = Product.objects.all()
    return render(request, 'all_products.html', {'products': products})

def get_product(request, pk=None):
    if pk:
        product = Product.objects.get(pk=pk)
    else:
        product = ""

    return render(request, 'product.html', {'product': product})
