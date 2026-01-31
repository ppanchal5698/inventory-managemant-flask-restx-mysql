# Customers module

from flask import Blueprint

customers_bp = Blueprint('customers', __name__)

from app.modules.customers import routes  # noqa: F401, E402
