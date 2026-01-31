# Stock module

from flask import Blueprint

stock_bp = Blueprint('stock', __name__)

from app.modules.stock import routes  # noqa: F401, E402
