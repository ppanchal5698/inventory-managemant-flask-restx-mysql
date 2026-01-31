# Warehouses module

from flask import Blueprint

warehouses_bp = Blueprint('warehouses', __name__)

from app.modules.warehouses import routes  # noqa: F401, E402
