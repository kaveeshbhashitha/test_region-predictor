from flask import Blueprint, render_template
from data.db import get_region_statistics
from .region_mapper import REGION_CODE_TO_NAME
from .map_config import REGION_IFRAMES

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/map")
def dashboard():
    regions = get_region_statistics()

    for r in regions:
        region_code = r["region"]                # DIM, KAN, etc.
        region_key = REGION_CODE_TO_NAME.get(region_code)

        r["map_url"] = REGION_IFRAMES.get(region_key)
        r["display_name"] = region_key.title() if region_key else region_code

    return render_template("map.html", regions=regions)
