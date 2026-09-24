"""
Flask backend for the Data Center Site Value Estimator.

Serves a single-page frontend (static/index.html) and a JSON API at /api/estimate.
Live commodity pricing (Metals.Dev) and optional land AVM (RentCast) are read from
environment variables and fail gracefully when absent.
"""

import os
from flask import Flask, request, jsonify, send_from_directory

from estimator import estimate_site, ValidationError
from metals_client import get_metal_prices
from land_value import get_rentcast_value

app = Flask(__name__, static_folder="static", static_url_path="")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/estimate", methods=["POST"])
def api_estimate():
    payload = request.get_json(silent=True) or {}

    lat = payload.get("lat")
    lng = payload.get("lng")
    sqft = payload.get("sqft")
    region = payload.get("region", "national")

    # --- Live copper/aluminum prices (graceful on missing key/network) ---
    metals = get_metal_prices()
    copper_price = metals.price("copper") if metals.ok else None
    aluminum_price = metals.price("aluminum") if metals.ok else None

    try:
        est = estimate_site(
            lat=lat,
            lng=lng,
            sqft=sqft,
            region=region,
            copper_price_usd_per_tonne=copper_price,
            copper_price_source=metals.source if metals.ok else metals.message,
            aluminum_price_usd_per_tonne=aluminum_price,
            aluminum_price_source=metals.source if metals.ok else metals.message,
        )
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    result = est.to_dict()

    # Metals status block so the UI can honestly show live-vs-unavailable.
    result["metals_status"] = {
        "ok": metals.ok,
        "source": metals.source,
        "message": metals.message,
    }

    # --- Optional RentCast secondary land data point ---
    rc = get_rentcast_value(est.lat, est.lng)
    result["rentcast"] = {
        "ok": rc.ok,
        "value_usd": rc.value_usd,
        "source": rc.source,
        "message": rc.message,
    }

    return jsonify(result)


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "metals_key_configured": bool(os.environ.get("METALS_DEV_API_KEY", "").strip()),
        "rentcast_key_configured": bool(os.environ.get("RENTCAST_API_KEY", "").strip()),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
