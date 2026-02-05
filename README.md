# Inventory Management System - Async Flask REST API

A "God-tier" Inventory Management System built with modern Python technologies, following a modular monolithic architecture.

## 🚀 Features

- **Async Core**: Fully asynchronous implementation using Flask 3+, SQLAlchemy 2.0 (Async), and `aiomysql`.
- **Authentication**: Secure JWT authentication (Flask-JWT-Extended) with Role-Based Access Control (RBAC).
- **Validation**: Strict input/output validation using **Pydantic v2**.
- **Documentation**: Auto-generated **OpenAPI/Swagger** documentation.
- **Caching**: High-performance caching with **Redis**.
- **Infrastructure**: Containerized with **Docker** and **Docker Compose**.
- **Modules**:
    - **Catalog**: Products, Categories, Brands, Suppliers.
    - **Inventory**: Warehouses, Stock Tracking, Inventory Transactions.
    - **Operations**: Sales Orders, Purchase Orders, Customers.

## 🛠️ Tech Stack

- **Framework**: Flask 3.x (Async)
- **ORM**: SQLAlchemy 2.0 + AsyncMySQL
- **Database**: MySQL 8.0
- **Cache**: Redis
- **Validation**: Pydantic v2
- **Testing**: Pytest + Pytest-Asyncio + Fakeredis
- **Deployment**: Docker, Docker Compose

## ⚡ Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)

### Running with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd inventory-management
   ```

2. **Start services**
   ```bash
   docker-compose up --build
   ```

3. **Access the API**
   - **API Docs**: [http://localhost:5000/api/docs](http://localhost:5000/api/docs)
   - **Health Check**: [http://localhost:5000/api/ping](http://localhost:5000/api/ping)

### Local Development Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Configure Environment**
   Create a `.env` file:
   ```env
   FLASK_APP=run.py
   FLASK_DEBUG=1
   SECRET_KEY=dev-secret
   JWT_SECRET_KEY=dev-jwt-secret
   DATABASE_URL=mysql+aiomysql://root:password@localhost/inventory_db
   REDIS_URL=redis://localhost:6379/0
   ```

4. **Initialize Database**
   ```bash
   # Ensure MySQL is running
   flask db upgrade
   # Or rely on auto-creation in run.py context (for dev)
   ```

5. **Run Server**
   ```bash
   flask run --debug
   ```

## 🧪 Testing

Run the full async test suite:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=app
```

## 📚 API Architecture

### Modular Monolith
The application is structured into domain-specific modules under `app/modules/`. Each module contains:
- `models.py`: SQLAlchemy 2.0 Async Models
- `schemas.py`: Pydantic V2 Schemas
- `services.py`: Business logic (Async)
- `api.py`: Route handlers (Flask-RESTX + `@async_route`)

### Async Patterns
All database and I/O operations use `await`.
- **Database**: `await db.session.execute(select(Model))`
- **Caching**: `await redis_client.get(key)`

## 🔒 Security

- **JWT Auth**: Access and Refresh tokens.
- **RBAC**: `@require_role('admin')` decorators.
- **Security Headers**: OWASP headers applied via middleware.
- **Input Validation**: Strict Pydantic validation prevents injection and malformed data.

## 🐳 Deployment

The `Dockerfile` provides a multi-stage build for optimized production images.
`docker-compose.yml` orchestrates the API, MySQL, and Redis services.

---
**Author**: Jules (AI Software Engineer)
