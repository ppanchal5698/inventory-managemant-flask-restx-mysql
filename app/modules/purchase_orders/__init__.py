# Purchase Orders module

from flask import Blueprint

purchase_orders_bp = Blueprint('purchase_orders', __name__)

from app.modules.purchase_orders import routes  # noqa: F401, E402
