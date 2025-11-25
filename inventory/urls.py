from django.urls import path
from . import views

urlpatterns = [
    path("", views.ItemListView.as_view(), name="item-list"),
    path("item/add/", views.ItemCreateView.as_view(), name="item-add"),
    path("item/<int:pk>/", views.ItemDetailView.as_view(), name="item-detail"),
    path(
        "stock-change/add/",
        views.StockChangeCreateView.as_view(),
        name="stock-change-add",
    ),
]
