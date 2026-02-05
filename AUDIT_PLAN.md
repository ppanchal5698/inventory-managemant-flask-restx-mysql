# Comprehensive Audit & Upgrade Plan

## 1. Audit Findings

### Summary
The application is a functional modular monolith using Flask-RESTX and SQLAlchemy. While logical and structured, it relies on legacy synchronous patterns (`db.Model`, `Query.get()`) and lacks modern operational best practices (Async, Docker, CI/CD).

### Detailed Findings Table

| Issue/Category | Files Affected | Severity | Proposed Fix | Tests Needed |
|----------------|----------------|----------|--------------|--------------|
| **Legacy ORM** | All Models (`app/modules/*/models.py`) | High | Migrate to SQLAlchemy 2.0 `DeclarativeBase`. Replace `Query.get` with `db.session.get`. Use `select()` syntax. | Unit tests for all CRUD operations. |
| **Sync I/O** | All Services (`app/modules/*/services.py`) | High | Rewrite all I/O bound functions to `async def`. Use `await db.session.execute()`. Use `aiomysql` driver. | Async test runner (`pytest-asyncio`). |
| **Auth Security** | `app/modules/auth/*` | High | Replace `Flask-Login` (Session) with `Flask-JWT-Extended`. Implement access/refresh tokens and revocation (Redis). | Auth flow tests (Login, Refresh, Protected Route). |
| **Validation** | `app/modules/*/schemas.py` | Medium | Replace `Marshmallow` with `Pydantic v2`. Enforce strict typing and auto-generate OpenAPI specs. | Input validation tests (Edge cases, invalid types). |
| **N+1 Queries** | `SalesOrder.to_dict`, `Product.total_stock` | Medium | Use `options(selectinload(...))` for relationships. Remove `lazy='dynamic'` where eager loading is better. | Performance tests (Query count check). |
| **Type Safety** | All (`mypy` errors) | Low | Fix 23+ mypy errors. Add missing type hints. Remove implicit Optionals. | Mypy strict run. |
| **Hardcoded Secrets** | `app/config.py` | Critical | Remove default fallbacks for `SECRET_KEY`. Enforce environment variables in Production. | Env var injection tests. |
| **Missing CI/CD** | Root | High | Add GitHub Actions workflow for Linting, Testing, and Docker Build. | CI execution check. |
| **Missing Docker** | Root | High | Add `Dockerfile` (multi-stage) and `docker-compose.yml`. | Container startup check. |
| **API Docs** | `app/extensions.py` | Low | Ensure Swagger UI works with JWT (add `Authorizations` config). | Manual UI verification. |

## 2. Upgrade Strategy ("God-Tier")

### Phase 1: Infrastructure & Foundation
- **Goal**: specific, reproducible, modern runtime.
- **Actions**:
    -   Containerize with Docker/Compose (App, MySQL 8, Redis).
    -   Setup CI/CD pipeline.
    -   Install Async dependencies (`flask[async]`, `sqlalchemy[asyncio]`).
    -   Configure `AsyncSession` factory.

### Phase 2: Core Refactor (Auth & Base)
- **Goal**: Secure, async, strongly typed core.
- **Actions**:
    -   Rewrite `BaseModel` for SA 2.0.
    -   Refactor `Auth` module to JWT + Async.
    -   Replace Marshmallow with Pydantic for Auth.

### Phase 3: Module Migration (Iterative)
- **Goal**: Migrate business logic without regression.
- **Order**:
    1.  Catalog (Products, Categories, Brands)
    2.  Inventory (Warehouses, Stock)
    3.  Operations (Orders, Customers)
- **Actions per Module**:
    -   Update Model (SA 2.0).
    -   Update Schema (Pydantic).
    -   Update Service (Async).
    -   Update Controller (Async Routes).
    -   Update Tests.

### Phase 4: Optimization & Hardening
- **Goal**: Performance and Security.
- **Actions**:
    -   Optimize SQL queries (Indexes, Eager Loading).
    -   Add Rate Limiting (Redis).
    -   Add Health Checks (`/ping`).
    -   Ensure 90% Test Coverage.

## 3. Technology Stack Target

-   **Framework**: Flask 3.x (Async)
-   **API**: Flask-RESTX (Modified for Pydantic/Async if possible, or manual wrapping) *Note: Flask-RESTX has limited Async support. We may need to use `asgiref` wrappers or careful structuring.*
-   **Database**: MySQL 8.0 (via `aiomysql`)
-   **ORM**: SQLAlchemy 2.0 (Async)
-   **Validation**: Pydantic v2
-   **Auth**: JWT (Flask-JWT-Extended)
-   **Cache**: Redis
-   **Testing**: Pytest + Pytest-Asyncio
