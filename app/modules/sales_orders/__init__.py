# Sales Orders module

from flask import Blueprint

sales_orders_bp = Blueprint('sales_orders', __name__)

from app.modules.sales_orders import routes  # noqa: F401, E402
