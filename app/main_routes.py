# app/main_routes.py
from flask import Blueprint, render_template

# blueprint name remains 'main'
main_bp = Blueprint("main", __name__)

# register the route but expose it with endpoint name 'index' (so url_for('index') works)
@main_bp.route("/", endpoint="index")
def index():
    return render_template("index.html")
