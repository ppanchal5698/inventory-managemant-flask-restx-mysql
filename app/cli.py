# Custom CLI commands

import click
from flask.cli import with_appcontext

from app.extensions import db


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    db.create_all()
    click.echo('Database initialized.')


@click.command('drop-db')
@with_appcontext
def drop_db_command():
    """Drop all database tables."""
    if click.confirm('Are you sure you want to drop all tables?'):
        db.drop_all()
        click.echo('Database tables dropped.')


@click.command('seed-db')
@with_appcontext
def seed_db_command():
    """Seed the database with sample data."""
    from app.modules.auth.models import User
    from app.modules.categories.models import Category
    from app.modules.warehouses.models import Warehouse
    from app.modules.brands.models import Brand
    
    created = []
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            first_name='System',
            last_name='Administrator',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        created.append('admin user')
    
    # Create sample categories if not exists
    if not Category.query.filter_by(category_name='Electronics').first():
        electronics = Category(category_name='Electronics', description='Electronic devices and components')
        db.session.add(electronics)
        created.append('Electronics category')
    
    # Create sample warehouse if not exists
    if not Warehouse.query.filter_by(warehouse_name='Main Warehouse').first():
        warehouse = Warehouse(
            warehouse_name='Main Warehouse',
            location='Building A',
            city='New York',
            country='USA'
        )
        db.session.add(warehouse)
        created.append('Main Warehouse')
    
    # Create sample brand if not exists
    if not Brand.query.filter_by(brand_name='Generic').first():
        brand = Brand(brand_name='Generic', manufacturer_name='Various')
        db.session.add(brand)
        created.append('Generic brand')
    
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
    """Create an admin user."""
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


def register_cli_commands(app):
    """Register CLI commands with the app."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(drop_db_command)
    app.cli.add_command(seed_db_command)
    app.cli.add_command(create_admin_command)
