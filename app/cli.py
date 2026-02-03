# Custom CLI commands

import click
from flask.cli import with_appcontext

from app.extensions import db


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database tables."""
    db.create_all()
    click.echo('Database initialized.')


@click.command('drop-db')
@with_appcontext
def drop_db_command():
    """Drop all database tables."""
    if click.confirm('Are you sure you want to drop all tables?'):
        # Get all table names from metadata
        tables = list(db.metadata.tables.keys())
        
        if not tables:
            click.echo('No tables to drop.')
            return
        
        # Drop all tables in a single connection with FK checks disabled
        with db.engine.connect() as conn:
            conn.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
            for table in tables:
                try:
                    conn.execute(db.text(f'DROP TABLE IF EXISTS `{table}`'))
                except Exception as e:
                    click.echo(f'Warning: Could not drop {table}: {e}')
            conn.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
            conn.commit()
        
        click.echo(f'Dropped {len(tables)} tables.')


@click.command('reset-db')
@with_appcontext
def reset_db_command():
    """Drop all tables and reinitialize the database."""
    if click.confirm('Are you sure you want to reset the database? This will delete ALL data!'):
        # Get all table names from metadata
        tables = list(db.metadata.tables.keys())
        
        # Drop all tables
        if tables:
            with db.engine.connect() as conn:
                conn.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
                for table in tables:
                    try:
                        conn.execute(db.text(f'DROP TABLE IF EXISTS `{table}`'))
                    except Exception:
                        pass
                conn.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
                conn.commit()
            click.echo(f'Dropped {len(tables)} tables.')
        
        # Recreate tables
        db.create_all()
        click.echo('Database reset and reinitialized.')


@click.command('seed-db')
@with_appcontext
def seed_db_command():
    """Seed the database with sample data."""
    from app.modules.auth.models import User
    from app.modules.categories.models import Category
    from app.modules.warehouses.models import Warehouse
    from app.modules.brands.models import Brand
    from app.modules.suppliers.models import Supplier
    from app.modules.customers.models import Customer
    
    created = []
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            first_name='System',
            last_name='Administrator',
            email='admin@example.com',
            phone='+1234567890',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        created.append('admin user')
    
    # Create sample categories if not exists
    electronics = Category.query.filter_by(category_name='Electronics').first()
    if not electronics:
        electronics = Category(
            category_name='Electronics',
            description='Electronic devices and components'
        )
        db.session.add(electronics)
        created.append('Electronics category')
        db.session.flush()  # Get the ID
    
    # Create subcategory
    if not Category.query.filter_by(category_name='Computers').first():
        computers = Category(
            category_name='Computers',
            description='Desktop and laptop computers',
            parent_category_id=electronics.category_id if electronics else None
        )
        db.session.add(computers)
        created.append('Computers subcategory')
    
    # Create sample warehouse if not exists
    if not Warehouse.query.filter_by(warehouse_name='Main Warehouse').first():
        warehouse = Warehouse(
            warehouse_name='Main Warehouse',
            location='Building A',
            address='100 Industrial Park',
            city='New York',
            state='NY',
            country='USA',
            postal_code='10001',
            manager_name='John Manager',
            phone='+1234567890',
            capacity=10000
        )
        db.session.add(warehouse)
        created.append('Main Warehouse')
    
    # Create sample brand if not exists
    if not Brand.query.filter_by(brand_name='Generic').first():
        brand = Brand(
            brand_name='Generic',
            manufacturer_name='Various Manufacturers',
            description='Generic/unbranded products'
        )
        db.session.add(brand)
        created.append('Generic brand')
    
    # Create sample supplier if not exists
    if not Supplier.query.filter_by(supplier_name='Tech Supplies Co.').first():
        supplier = Supplier(
            supplier_name='Tech Supplies Co.',
            contact_person='John Smith',
            email='john@techsupplies.com',
            phone='+1234567890',
            address='123 Tech Street',
            city='New York',
            state='NY',
            country='USA',
            postal_code='10001',
            tax_id='TAX-123456',
            payment_terms='Net 30'
        )
        db.session.add(supplier)
        created.append('Tech Supplies Co. supplier')
    
    # Create sample customer if not exists
    if not Customer.query.filter_by(customer_name='ACME Corporation').first():
        customer = Customer(
            customer_name='ACME Corporation',
            contact_person='Jane Doe',
            email='jane@acme.com',
            phone='+0987654321',
            address='456 Business Ave',
            city='Los Angeles',
            state='CA',
            country='USA',
            postal_code='90001',
            tax_id='CUST-TAX-789',
            credit_limit=50000.00
        )
        db.session.add(customer)
        created.append('ACME Corporation customer')
    
    db.session.commit()
    
    if created:
        click.echo(f'Created: {", ".join(created)}')
        click.echo('Admin user: admin / admin123')
    else:
        click.echo('Database already seeded. No changes made.')


@click.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin_command(username, email, password):
    """Create an admin user.
    
    Usage: flask create-admin <username> <email> <password>
    """
    from app.modules.auth.models import User
    
    if User.query.filter_by(username=username).first():
        click.echo(f'Error: Username {username} already exists.')
        return
    
    if User.query.filter_by(email=email).first():
        click.echo(f'Error: Email {email} already exists.')
        return
    
    user = User(
        username=username,
        first_name='Admin',
        last_name='User',
        email=email,
        role='admin'
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    click.echo(f'Admin user {username} created successfully.')


@click.command('show-routes')
@with_appcontext
def show_routes_command():
    """Display all registered API routes."""
    from flask import current_app
    
    rules = sorted(current_app.url_map.iter_rules(), key=lambda r: r.rule)
    
    click.echo('\n=== Registered Routes ===\n')
    for rule in rules:
        if rule.endpoint != 'static':
            methods = ', '.join(sorted(m for m in rule.methods if m not in ('HEAD', 'OPTIONS')))
            click.echo(f'{methods:20} {rule.rule}')
    click.echo('')


def register_cli_commands(app):
    """Register CLI commands with the app."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(drop_db_command)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(seed_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(show_routes_command)
