from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Item, Location, Stock, StockChange, Category

class StockManagementTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.item = Item.objects.create(name="Laptop", sku="LPT001", category=self.category)
        self.warehouse = Location.objects.create(name="Main Warehouse")
        self.store = Location.objects.create(name="Retail Store")
        self.client = Client()

    def test_incoming_delivery(self):
        """Test receiving stock increases quantity."""
        StockChange.objects.create(
            item=self.item,
            change_type='IN',
            dest_location=self.warehouse,
            quantity=10
        )
        
        stock = Stock.objects.get(item=self.item, location=self.warehouse)
        self.assertEqual(stock.quantity, 10)
        self.assertEqual(self.item.get_total_stock(), 10)

    def test_outgoing_shipment(self):
        """Test shipping stock decreases quantity."""
        # Setup initial stock
        Stock.objects.create(item=self.item, location=self.warehouse, quantity=20)
        
        StockChange.objects.create(
            item=self.item,
            change_type='OUT',
            source_location=self.warehouse,
            quantity=5
        )
        
        stock = Stock.objects.get(item=self.item, location=self.warehouse)
        self.assertEqual(stock.quantity, 15)

    def test_internal_move(self):
        """Test moving stock transfers quantity."""
        Stock.objects.create(item=self.item, location=self.warehouse, quantity=20)
        
        StockChange.objects.create(
            item=self.item,
            change_type='MOVE',
            source_location=self.warehouse,
            dest_location=self.store,
            quantity=5
        )
        
        wh_stock = Stock.objects.get(item=self.item, location=self.warehouse)
        st_stock = Stock.objects.get(item=self.item, location=self.store)
        
        self.assertEqual(wh_stock.quantity, 15)
        self.assertEqual(st_stock.quantity, 5)

    def test_insufficient_stock_validation(self):
        """Test that you cannot move/ship more stock than available."""
        Stock.objects.create(item=self.item, location=self.warehouse, quantity=5)
        
        with self.assertRaises(ValidationError):
            change = StockChange(
                item=self.item,
                change_type='OUT',
                source_location=self.warehouse,
                quantity=10
            )
            change.save() # Should trigger validation in save method

    def test_invalid_location_combinations(self):
        """Test validation of location requirements for change types."""
        # Incoming requires dest
        with self.assertRaises(ValidationError):
            c = StockChange(item=self.item, change_type='IN', quantity=1)
            c.clean()
            
        # Outgoing requires source
        with self.assertRaises(ValidationError):
            c = StockChange(item=self.item, change_type='OUT', quantity=1)
            c.clean()
            
        # Move requires both
        with self.assertRaises(ValidationError):
            c = StockChange(item=self.item, change_type='MOVE', source_location=self.warehouse, quantity=1)
            c.clean()

    def test_negative_quantity(self):
        with self.assertRaises(ValidationError):
            c = StockChange(item=self.item, change_type='IN', dest_location=self.warehouse, quantity=0)
            c.clean()

    def test_create_item_view(self):
        """Test creating a new item via the view."""
        response = self.client.post(reverse('item-add'), {
            'name': 'New Widget',
            'sku': 'WIDGET001',
            'category': self.category.id,
            'description': 'A shiny new widget',
            'price': '19.99'
        })
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.assertTrue(Item.objects.filter(sku='WIDGET001').exists())
