# KioskKeeper – Offline Inventory Management

A lightweight web application for small kiosk/shop owners to manage inventory, track stock levels, and receive low-stock alerts. Works fully offline with SQLite.

## Features

- **Product Management** – Add, edit, delete products with categories (Airtime, Electricity Tokens, Milk, Bread, Others)
- **Inventory Tracking** – Real-time stock updates with full transaction history
- **Low Stock Alerts** – Automatic flags when quantity drops below reorder level
- **Dashboard** – Summary cards showing total products, low stock count, and total stock value
- **Sales Simulation** – Record sales and restocks with automatic inventory updates
- **Search & Filter** – Search by name, filter by category
- **Reports** – Daily stock reports, low stock reports, CSV export
- **Dark Mode** – Toggle with persistent preference
- **Offline-First** – SQLite database, no internet required
- **PWA Support** – Installable app with service worker caching

## Quick Start

### Prerequisites

- Python 3.8+

### Installation

```bash
# Navigate to the project directory
cd kioskkeeper

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python app.py
```

Open your browser to **http://localhost:5000**

## Project Structure

```
kioskkeeper/
├── app.py              # Flask application + API routes
├── models.py           # SQLAlchemy models (Product, Transaction)
├── requirements.txt    # Python dependencies
├── instance/
│   └── kiosk.db        # SQLite database (auto-created)
├── templates/
│   ├── base.html       # Base layout with navigation
│   ├── dashboard.html  # Dashboard page
│   ├── products.html   # Product management page
│   ├── transactions.html # Transaction history page
│   └── reports.html    # Reports and CSV export page
└── static/
    ├── css/
    │   └── style.css   # Responsive styles + dark mode
    ├── js/
    │   └── app.js      # Shared JavaScript utilities
    ├── icons/          # PWA icons
    ├── manifest.json   # PWA manifest
    └── sw.js           # Service worker
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List products (supports `?search=` and `?category=`) |
| POST | `/api/products` | Create a new product |
| GET | `/api/products/<id>` | Get a single product |
| PUT | `/api/products/<id>` | Update a product |
| DELETE | `/api/products/<id>` | Delete a product |
| POST | `/api/transactions` | Record a sale or restock |
| GET | `/api/transactions` | List transactions (supports filters) |
| GET | `/api/dashboard` | Dashboard summary data |
| GET | `/api/reports/low-stock` | Low stock items |
| GET | `/api/reports/daily?date=YYYY-MM-DD` | Daily report |
| GET | `/api/reports/export/csv?type=products` | Export CSV |

## Database Schema

**products**: id, name, category, quantity, unit_price, reorder_level

**transactions**: id, product_id, type (sale/restock), quantity, date
