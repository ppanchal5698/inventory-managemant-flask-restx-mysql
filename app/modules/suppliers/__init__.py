# Suppliers module

from flask import Blueprint

suppliers_bp = Blueprint('suppliers', __name__)

from app.modules.suppliers import routes  # noqa: F401, E402
