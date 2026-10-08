"""
Free geocoding via OpenStreetMap Nominatim (no API key).

Two jobs:
  (a) forward search  -> used by the UI's "search an area/street" box above the map.
  (b) reverse lookup  -> used server-side to auto-detect the US state / county /
      metro of a drawn parcel's centroid, so the land comparable can be chosen
      granularly instead of via a manual region dropdown.

Nominatim usage policy (https://operations.osmfoundation.org/policies/nominatim/)
requires: an identifying User-Agent, no more than 1 request/second, and no heavy
bulk use. We honour this by:
  - sending a descriptive User-Agent + a contact referer,
  - proxying through the Flask backend (so the client never hammers Nominatim
    directly on every keystroke — the frontend debounces and requires >=3 chars,
    and the backend applies a hard >=1s-between-calls throttle as a backstop),
  - limiting result counts.

Everything degrades gracefully: on any network/parse error we return a clear
ok=False result rather than raising, so the app never crashes on a geocode miss.
"""

import json
import threading
import time
import urllib.request
import urllib.error
import urllib.parse

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"

# Identifies this app to Nominatim per their policy. Not a secret.
USER_AGENT = "dc-site-estimator/2.0 (data-center site value estimator; contact ali.fazeli01@gmail.com)"

# Minimum seconds between outbound Nominatim calls (policy: max 1 req/sec). This is
# a process-wide backstop on top of the client-side debounce.
_MIN_INTERVAL_S = 1.0
_rate_lock = threading.Lock()
_last_call_ts = [0.0]


def _throttle():
    """Block if needed so outbound calls never exceed ~1/sec (Nominatim policy)."""
    with _rate_lock:
        now = time.monotonic()
        wait = _MIN_INTERVAL_S - (now - _last_call_ts[0])
        if wait > 0:
            time.sleep(wait)
        _last_call_ts[0] = time.monotonic()


def _get_json(url, timeout):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": "https://localhost/dc-site-estimator",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


class GeocodeResult:
    """Outcome of a forward-search call: a list of candidate places."""

    def __init__(self, ok, results=None, source=None, message=None):
        self.ok = ok
        # results: list of {display_name, lat, lng, type, importance}
        self.results = results or []
        self.source = source or "OpenStreetMap Nominatim"
        self.message = message

    def to_dict(self):
        return {
            "ok": self.ok,
            "results": self.results,
            "source": self.source,
            "message": self.message,
        }


class ReverseResult:
    """Outcome of a reverse lookup: the administrative place of a coordinate."""

    def __init__(self, ok, country_code=None, state=None, state_code=None,
                 county=None, city=None, display_name=None, source=None,
                 message=None):
        self.ok = ok
        self.country_code = country_code      # e.g. "us"
        self.state = state                    # e.g. "Virginia"
        self.state_code = state_code          # e.g. "VA" (USPS, when derivable)
        self.county = county                  # e.g. "Loudoun County"
        self.city = city                      # town / city / village, if any
        self.display_name = display_name
        self.source = source or "OpenStreetMap Nominatim"
        self.message = message

    def to_dict(self):
        return {
            "ok": self.ok,
            "country_code": self.country_code,
            "state": self.state,
            "state_code": self.state_code,
            "county": self.county,
            "city": self.city,
            "display_name": self.display_name,
            "source": self.source,
            "message": self.message,
        }


def search_places(query, limit=5, timeout=10):
    """
    Forward geocode a free-text query to candidate places.

    Returns a GeocodeResult. Never raises for expected failures.
    """
    query = (query or "").strip()
    if len(query) < 3:
        return GeocodeResult(
            ok=False, message="Enter at least 3 characters to search."
        )

    params = urllib.parse.urlencode({
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": max(1, min(int(limit), 10)),
    })
    url = f"{NOMINATIM_SEARCH_URL}?{params}"

    _throttle()
    try:
        data = _get_json(url, timeout)
    except urllib.error.HTTPError as e:
        return GeocodeResult(
            ok=False,
            message=f"Geocoder returned HTTP {e.code}. Try again shortly.",
        )
    except (urllib.error.URLError, TimeoutError) as e:
        return GeocodeResult(
            ok=False, message=f"Could not reach the geocoder ({e})."
        )
    except json.JSONDecodeError:
        return GeocodeResult(ok=False, message="Geocoder returned a bad response.")

    if not isinstance(data, list):
        return GeocodeResult(ok=False, message="Geocoder returned no results.")

    results = []
    for item in data:
        try:
            lat = float(item.get("lat"))
            lng = float(item.get("lon"))
        except (TypeError, ValueError):
            continue
        results.append({
            "display_name": item.get("display_name", ""),
            "lat": lat,
            "lng": lng,
            "type": item.get("type", ""),
            "category": item.get("category", item.get("class", "")),
            "importance": item.get("importance", 0),
        })

    if not results:
        return GeocodeResult(
            ok=True, results=[], message="No matching places found."
        )
    return GeocodeResult(ok=True, results=results)


# USPS two-letter codes keyed on lowercase full state name, so a reverse lookup
# can be mapped to the land-price table's state keys deterministically. Nominatim
# does not reliably return the postal abbreviation, so we derive it ourselves.
_US_STATE_ABBR = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "district of columbia": "DC", "florida": "FL", "georgia": "GA", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI",
    "south carolina": "SC", "south dakota": "SD", "tennessee": "TN", "texas": "TX",
    "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}


def state_abbr(state_name):
    """Map a full US state name to its USPS code, or None."""
    if not state_name:
        return None
    return _US_STATE_ABBR.get(state_name.strip().lower())


def reverse_geocode(lat, lng, timeout=10):
    """
    Reverse geocode a coordinate to its administrative place (country/state/county).

    Returns a ReverseResult. Never raises for expected failures.
    """
    try:
        lat = float(lat)
        lng = float(lng)
    except (TypeError, ValueError):
        return ReverseResult(ok=False, message="Invalid coordinate for reverse lookup.")

    params = urllib.parse.urlencode({
        "lat": lat,
        "lon": lng,
        "format": "jsonv2",
        "addressdetails": 1,
        "zoom": 10,  # county/city level is enough; avoids over-specific house detail
    })
    url = f"{NOMINATIM_REVERSE_URL}?{params}"

    _throttle()
    try:
        data = _get_json(url, timeout)
    except urllib.error.HTTPError as e:
        return ReverseResult(
            ok=False, message=f"Reverse geocoder returned HTTP {e.code}."
        )
    except (urllib.error.URLError, TimeoutError) as e:
        return ReverseResult(
            ok=False, message=f"Could not reach the reverse geocoder ({e})."
        )
    except json.JSONDecodeError:
        return ReverseResult(ok=False, message="Reverse geocoder returned a bad response.")

    addr = (data or {}).get("address", {})
    if not addr:
        return ReverseResult(
            ok=False, message="No address details for this coordinate."
        )

    state = addr.get("state")
    county = addr.get("county")
    city = (
        addr.get("city")
        or addr.get("town")
        or addr.get("village")
        or addr.get("municipality")
    )
    cc = (addr.get("country_code") or "").lower() or None

    return ReverseResult(
        ok=True,
        country_code=cc,
        state=state,
        state_code=state_abbr(state) if cc == "us" else None,
        county=county,
        city=city,
        display_name=data.get("display_name"),
    )
