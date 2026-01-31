# Inventory module - transactions and adjustments

from flask import Blueprint

inventory_bp = Blueprint('inventory', __name__)

from app.modules.inventory import routes  # noqa: F401, E402
