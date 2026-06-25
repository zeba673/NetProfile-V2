from flask import Blueprint
abogado_bp = Blueprint('abogado', __name__)
from app.blueprints.abogado import routes  # noqa: F401, E402
