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
from geometry import (
    parse_polygon,
    geodesic_area_sq_ft,
    polygon_centroid,
    GeometryError,
)

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

    # Draw-to-select: if a polygon is supplied it is the PRIMARY input. We recompute
    # its enclosed area (geodesic, server-side) rather than trusting a browser number,
    # and derive the lat/lng from its centroid. A manual lat/lng/sqft remains valid
    # as a fallback when no polygon is drawn.
    polygon = payload.get("polygon")
    polygon_area_sqft = None
    if polygon is not None:
        try:
            pts = parse_polygon(polygon)
            polygon_area_sqft = geodesic_area_sq_ft(pts)
            clat, clng = polygon_centroid(pts)
        except GeometryError as e:
            return jsonify({"error": str(e)}), 400
        sqft = polygon_area_sqft
        lat, lng = clat, clng

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

    # Tell the UI whether the footprint came from a drawn polygon (geodesic area)
    # or a manual sq ft entry, so it can label the source honestly.
    result["area_source"] = (
        "drawn_polygon" if polygon_area_sqft is not None else "manual"
    )

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
