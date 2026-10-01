"""
Geodesic polygon-area calculation for the draw-to-select feature.

When the user draws a polygon or rectangle on the Leaflet map, we need its real
enclosed ground area in square feet to feed the existing estimate pipeline. A naive
planar (lat/lng-as-xy) area is wrong at scale because a degree of longitude shrinks
toward the poles. We therefore use the standard spherical-excess formula on a sphere
of the WGS84 mean radius.

This is the same approach Leaflet.GeometryUtil (L.GeometryUtil.geodesicArea) uses,
so a polygon area computed in the browser and one computed here agree. We recompute
server-side (rather than trusting a browser-sent number) so the figure that enters
the estimate is deterministic and testable.

Reference for the formula: the spherical polygon area via the sum over edges of
    (lng[i+1] - lng[i]) * (2 + sin(lat[i]) + sin(lat[i+1]))
scaled by R^2 / 2. See L.GeometryUtil.geodesicArea and the OpenLayers / Google Maps
spherical geometry implementations, which all use this identity.
"""

import math

# WGS84 equatorial (semi-major) radius in metres. This is the exact constant
# Leaflet's L.GeometryUtil.geodesicArea uses, so the browser and server agree. On a
# true-sphere area calc it slightly overstates area versus the authalic mean radius
# (~6371008 m), but the residual vs the WGS84 ellipsoid stays under ~1% everywhere
# (verified), which is well within the tolerance this tool needs.
EARTH_RADIUS_M = 6378137.0

SQ_METRES_PER_SQ_FOOT = 0.09290304  # exact: 0.3048 m per foot, squared


class GeometryError(ValueError):
    """Raised for an invalid or degenerate polygon."""


def geodesic_area_sq_m(latlngs):
    """
    Area in square metres enclosed by a polygon given as a list of (lat, lng)
    vertices in decimal degrees. The ring may be open (first != last) or closed
    (first == last); both are handled. Winding direction does not matter — the
    absolute value is returned.

    Mirrors L.GeometryUtil.geodesicArea so browser and server agree.
    """
    pts = list(latlngs)
    # Drop an explicit closing vertex if present; the summation closes the ring.
    if len(pts) >= 2 and pts[0] == pts[-1]:
        pts = pts[:-1]

    if len(pts) < 3:
        raise GeometryError(
            "A polygon needs at least 3 distinct vertices to enclose an area."
        )

    area = 0.0
    n = len(pts)
    for i in range(n):
        lat1, lng1 = pts[i]
        lat2, lng2 = pts[(i + 1) % n]
        area += math.radians(lng2 - lng1) * (
            2.0 + math.sin(math.radians(lat1)) + math.sin(math.radians(lat2))
        )

    area = area * EARTH_RADIUS_M * EARTH_RADIUS_M / 2.0
    return abs(area)


def geodesic_area_sq_ft(latlngs):
    """Enclosed polygon area in square feet (see geodesic_area_sq_m)."""
    return geodesic_area_sq_m(latlngs) / SQ_METRES_PER_SQ_FOOT


def polygon_centroid(latlngs):
    """
    Simple average-of-vertices centroid (lat, lng) for a polygon, used only to
    recentre the map / place a marker. Good enough for the modest footprints this
    tool deals with; not a true area-weighted centroid.
    """
    pts = list(latlngs)
    if len(pts) >= 2 and pts[0] == pts[-1]:
        pts = pts[:-1]
    if not pts:
        raise GeometryError("Cannot take the centroid of an empty polygon.")
    lat = sum(p[0] for p in pts) / len(pts)
    lng = sum(p[1] for p in pts) / len(pts)
    return lat, lng


def parse_polygon(raw):
    """
    Coerce a loosely-typed polygon payload (list of [lat, lng] pairs, as JSON
    delivers it) into a validated list of (float, float) tuples. Raises
    GeometryError on anything malformed so the API can return a clean 400.
    """
    if not isinstance(raw, (list, tuple)):
        raise GeometryError("Polygon must be a list of [lat, lng] points.")

    pts = []
    for i, pair in enumerate(raw):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise GeometryError(
                f"Polygon point {i} must be a [lat, lng] pair."
            )
        try:
            lat = float(pair[0])
            lng = float(pair[1])
        except (TypeError, ValueError):
            raise GeometryError(f"Polygon point {i} has non-numeric coordinates.")
        if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lng <= 180.0):
            raise GeometryError(f"Polygon point {i} is out of coordinate range.")
        pts.append((lat, lng))

    # Deduplicate a trailing closing vertex before the >=3 check.
    check = pts[:-1] if len(pts) >= 2 and pts[0] == pts[-1] else pts
    if len(check) < 3:
        raise GeometryError(
            "A polygon needs at least 3 distinct vertices to enclose an area."
        )
    return pts
