# Inventory Management System - Flask REST API

A comprehensive inventory management system built with Flask, Flask-RESTX, and MySQL. This application follows a modular monolithic architecture pattern for better organization and maintainability.

## Features

- **User Authentication** - Secure login/logout with role-based access control (admin, manager, staff, viewer)
- **Product Management** - Full CRUD operations for products with categories, brands, and SKU support
- **Inventory Tracking** - Real-time stock levels, reorder alerts, and inventory movements
- **Warehouse Management** - Multi-warehouse support with stock transfers
- **Purchase Orders** - Create and manage purchase orders from suppliers
- **Sales Orders** - Process customer orders with inventory deduction
- **Supplier Management** - Track suppliers and their products
- **Customer Management** - Maintain customer database and order history
- **API Documentation** - Auto-generated Swagger UI documentation

## Tech Stack

- **Backend**: Python 3.13+, Flask 3.0+
- **API Framework**: Flask-RESTX (Swagger/OpenAPI)
- **Database**: MySQL/MariaDB
- **ORM**: Flask-SQLAlchemy
- **Migrations**: Flask-Migrate
- **Caching**: Flask-Caching
- **Authentication**: Flask-Login
- **Serialization**: Marshmallow

## Project Structure

```
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration settings
│   ├── extensions.py        # Flask extensions
│   ├── middleware.py        # Request middleware
│   ├── cli.py               # CLI commands
│   ├── core/                # Core utilities
│   │   ├── cache.py
│   │   ├── database.py
│   │   └── utils.py
│   └── modules/             # Feature modules
│       ├── auth/            # Authentication
│       ├── brands/          # Brand management
│       ├── categories/      # Category management
│       ├── customers/       # Customer management
│       ├── inventory/       # Inventory tracking
│       ├── products/        # Product management
│       ├── purchase_orders/ # Purchase orders
│       ├── sales_orders/    # Sales orders
│       ├── stock/           # Stock management
│       ├── suppliers/       # Supplier management
│       └── warehouses/      # Warehouse management
├── db/
│   └── schema.sql           # Database schema
├── tests/                   # Test suite
├── postman/                 # Postman collection
├── pyproject.toml           # Project dependencies
└── run.py                   # Application entry point
```

## Installation

### Prerequisites

- Python 3.13 or higher
- MySQL/MariaDB database server
- pip or uv package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ppanchal5698/inventory-managemant-flask-restx-mysql.git
   cd inventory-managemant-flask-restx-mysql
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   # Or for development
   pip install -e ".[dev]"
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=mysql+pymysql://username:password@localhost/inventory_db
   ```

5. **Initialize the database**
   ```bash
   # Create the database in MySQL first
   mysql -u root -p -e "CREATE DATABASE inventory_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   
   # Run the schema
   mysql -u root -p inventory_db < db/schema.sql
   
   # Or use Flask CLI
   flask init-db
   ```

6. **Run the application**
   ```bash
   flask run
   # Or
   python run.py
   ```

## API Documentation

Once the application is running, access the Swagger UI documentation at:
- **Swagger UI**: http://localhost:5000/api/docs
- **API Base URL**: http://localhost:5000/api/v1

### API Endpoints

| Module | Endpoint | Description |
|--------|----------|-------------|
| Auth | `/api/v1/auth` | User authentication |
| Categories | `/api/v1/categories` | Category management |
| Brands | `/api/v1/brands` | Brand management |
| Suppliers | `/api/v1/suppliers` | Supplier management |
| Products | `/api/v1/products` | Product management |
| Warehouses | `/api/v1/warehouses` | Warehouse management |
| Stock | `/api/v1/stock` | Stock levels |
| Customers | `/api/v1/customers` | Customer management |
| Purchase Orders | `/api/v1/purchase-orders` | Purchase orders |
| Sales Orders | `/api/v1/sales-orders` | Sales orders |
| Inventory | `/api/v1/inventory` | Inventory movements |

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api/test_auth_api.py
```

## Postman Collection

Import the Postman collection from `postman/Inventory_Management_API.postman_collection.json` to test the API endpoints.

## Configuration

The application supports multiple configuration environments:

- `development` - Debug mode enabled, verbose logging
- `testing` - In-memory database for tests
- `production` - Optimized settings for production

Configure via the `FLASK_ENV` environment variable.

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Author

**Parth Panchal** - [GitHub](https://github.com/ppanchal5698)
