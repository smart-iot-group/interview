# Inventory Management System

A simple web-based tool to keep track of stock levels in a warehouse. Built with Django.

## Features

- **Items & Locations**: Manage inventory items and multiple storage locations.
- **Stock Tracking**: View current stock per item and location.
- **Stock History**: Record and view stock changes (Incoming, Outgoing, Internal Moves).
- **Validation**: Prevents invalid operations like negative stock or incomplete transfers.

## Setup & Running Locally

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### 1. Setup Environment
Clone the repository and checkout the feature branch (if applicable):
```bash
git checkout feature/inventory-implementation
```

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Database Setup
Run migrations to set up the database schema:
```bash
python manage.py migrate
```

(Optional) Create a superuser to access the Admin interface:
```bash
python manage.py createsuperuser
```

### 3. Run the Server
Start the development server:
```bash
python manage.py runserver
```

Access the application at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Usage

- **Dashboard**: The home page lists all items and their total stock.
- **Record Change**: Click "Record Change" to log incoming deliveries, outgoing shipments, or moves between locations.
- **Item Details**: Click on an item name to see stock breakdown by location and recent history.
- **Admin**: Go to `/admin/` to manage Categories, Items, and Locations directly.

## Domain Model

- **Item**: Products stored in the warehouse.
- **Location**: Physical places where items are kept (e.g., "Main Warehouse", "Shelf A").
- **Stock**: The current quantity of an *Item* at a specific *Location*.
- **StockChange**: An immutable record of a stock movement (IN, OUT, or MOVE).

## Notes
- Stock levels are updated transactionally when a `StockChange` is recorded.
- Validation ensures you cannot move or ship more stock than is available at a source location.