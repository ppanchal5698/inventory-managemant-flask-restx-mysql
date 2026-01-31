# Products module

from flask import Blueprint

products_bp = Blueprint('products', __name__)

from app.modules.products import routes  # noqa: F401, E402
