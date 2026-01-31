# Brands module

from flask import Blueprint

brands_bp = Blueprint('brands', __name__)

from app.modules.brands import routes  # noqa: F401, E402
