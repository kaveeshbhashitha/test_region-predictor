# dashboards/routes.py

from flask import Blueprint, render_template
from data.db import get_region_statistics
from .map_config import REGION_IFRAMES

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/map")
def dashboard():
    stats = get_region_statistics()

    for r in stats:
        r["map_url"] = REGION_IFRAMES.get(r["region"])

    return render_template("map.html", regions=stats)
