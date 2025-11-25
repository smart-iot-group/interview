from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Sum
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Item, StockChange
from .forms import StockChangeForm, ItemForm

class ItemListView(ListView):
    model = Item
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        return Item.objects.annotate(total_stock=Sum('stocks__quantity')).order_by('name')

class ItemDetailView(DetailView):
    model = Item
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stocks'] = self.object.stocks.select_related('location').all()
        context['recent_changes'] = self.object.stock_changes.select_related('source_location', 'dest_location').order_by('-timestamp')[:10]
        return context

class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('item-list')

    def form_valid(self, form):
        messages.success(self.request, "Item created successfully.")
        return super().form_valid(form)

class StockChangeCreateView(CreateView):
    model = StockChange
    form_class = StockChangeForm
    template_name = 'inventory/stock_change_form.html'
    success_url = reverse_lazy('item-list')

    def form_valid(self, form):
        messages.success(self.request, "Stock change recorded successfully.")
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        item_id = self.request.GET.get('item_id')
        if item_id:
            initial['item'] = item_id
        return initial
