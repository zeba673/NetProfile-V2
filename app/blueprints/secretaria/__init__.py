from flask import Blueprint
secretaria_bp = Blueprint('secretaria', __name__)
from app.blueprints.secretaria import routes  # noqa: F401, E402
