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
from land_prices import lookup_land_comp, lookup_land_comp_for_place
from geocode import search_places, reverse_geocode, state_abbr
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


@app.route("/api/geocode", methods=["GET"])
def api_geocode():
    """Forward-geocode a free-text area/street query for the search box."""
    q = request.args.get("q", "")
    res = search_places(q, limit=6)
    status = 200 if res.ok else (400 if "3 characters" in (res.message or "") else 200)
    return jsonify(res.to_dict()), status


@app.route("/api/detect-location", methods=["POST"])
def api_detect_location():
    """
    Reverse-geocode a drawn parcel's centroid and return the auto-detected
    land comparable (state / county-metro where available) for the user to
    confirm or override. This is the 'confirm, don't force a dropdown' step.
    """
    payload = request.get_json(silent=True) or {}
    lat = payload.get("lat")
    lng = payload.get("lng")

    # Explicit place (the UI's State + County fields, edited by the user): resolve
    # the comparable directly at state / county level, no geocoding needed.
    state = (payload.get("state") or "").strip()
    if state:
        if not state_abbr(state):
            return jsonify({"error": f"Unknown US state: {state}"}), 400
        comp = lookup_land_comp_for_place(
            state_code=state_abbr(state),
            county=(payload.get("county") or "").strip() or None,
        )
        return jsonify({
            "lat": lat,
            "lng": lng,
            "reverse": {"ok": True, "country_code": "us",
                        "state": comp["detected"]["state"],
                        "state_code": comp["detected"]["state_code"],
                        "county": comp["detected"]["county"],
                        "display_name": comp["place"], "source": "user-entered"},
            "land_comp": comp,
        })

    polygon = payload.get("polygon")
    if polygon is not None:
        try:
            pts = parse_polygon(polygon)
            lat, lng = polygon_centroid(pts)
        except GeometryError as e:
            return jsonify({"error": str(e)}), 400

    rev = reverse_geocode(lat, lng)
    comp = lookup_land_comp(rev)
    return jsonify({
        "lat": lat,
        "lng": lng,
        "reverse": rev.to_dict(),
        "land_comp": comp,
    })


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

    # --- Granular land comparable ---------------------------------------------
    # The UI confirms/overrides an auto-detected comp. It passes back a
    # `land_comp` block (the one it showed the user, possibly edited). If absent,
    # we reverse-geocode here as a fallback so a direct API call still works.
    # Resolution order: confirmed comp from the UI -> explicit state/county in the
    # payload -> reverse-geocode the coordinates.
    land_comp = payload.get("land_comp")
    state = (payload.get("state") or "").strip()
    if land_comp is None and state:
        if not state_abbr(state):
            return jsonify({"error": f"Unknown US state: {state}"}), 400
        land_comp = lookup_land_comp_for_place(
            state_code=state_abbr(state),
            county=(payload.get("county") or "").strip() or None,
        )
    if land_comp is None and lat is not None and lng is not None:
        rev = reverse_geocode(lat, lng)
        land_comp = lookup_land_comp(rev)
    # A user-entered $/acre override carries no place; attach the state/county the
    # UI shows so the parcel is still described at state + county level.
    if isinstance(land_comp, dict) and not land_comp.get("place") and state_abbr(state):
        ref = lookup_land_comp_for_place(
            state_code=state_abbr(state),
            county=(payload.get("county") or "").strip() or None,
        )
        land_comp = {**land_comp, "detected": ref["detected"], "place": ref["place"],
                     "state_context": ref["state_context"]}
    per_acre_override = None
    if isinstance(land_comp, dict):
        v = land_comp.get("usd_per_acre")
        if isinstance(v, (int, float)) and v > 0:
            per_acre_override = float(v)

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
            land_price_per_acre_override=per_acre_override,
            land_comp_label=(land_comp or {}).get("label") if isinstance(land_comp, dict) else None,
            land_comp_source=(land_comp or {}).get("source") if isinstance(land_comp, dict) else None,
        )
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    result = est.to_dict()
    result["land_comp"] = land_comp
    # State + county description of the parcel (replaces the old directional
    # region bucket). Comes from the comparable's detected place.
    if isinstance(land_comp, dict):
        det = land_comp.get("detected") or {}
        result["location"] = {
            "place": land_comp.get("place"),
            "state": det.get("state"),
            "state_code": det.get("state_code"),
            "county": det.get("county"),
            "city": det.get("city"),
            "country_code": det.get("country_code"),
            "state_context": land_comp.get("state_context"),
        }
    else:
        result["location"] = None

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
        "geocoder": "OpenStreetMap Nominatim (free, no key)",
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
