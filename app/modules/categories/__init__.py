# Categories module

from flask import Blueprint

categories_bp = Blueprint('categories', __name__)

from app.modules.categories import routes  # noqa: F401, E402
