"""
Optional RentCast AVM lookup, keyed on lat/long.

This is a SECONDARY enhancement. The regional-average land proxy in estimator.py
always works standalone; RentCast is only attempted if RENTCAST_API_KEY is set,
and it fails gracefully otherwise.

RentCast: base https://api.rentcast.io/v1, auth via the X-Api-Key header,
value estimate at /avm/value which accepts latitude/longitude query params.
Docs: https://developers.rentcast.io/reference/value-estimate

NOTE: RentCast automatic subject-property lookup officially requires an ADDRESS;
a raw lat/long may return no comparables for an undeveloped parcel. That
uncertainty is exactly why the regional proxy remains the primary approach and
this is optional. If RentCast returns a value it is surfaced as a secondary,
address-based data point — not as the headline land value.
"""

import os
import json
import urllib.request
import urllib.error
import urllib.parse

RENTCAST_AVM_URL = "https://api.rentcast.io/v1/avm/value"
ENV_KEY = "RENTCAST_API_KEY"


class LandValueResult:
    def __init__(self, ok, value_usd=None, source=None, message=None):
        self.ok = ok
        self.value_usd = value_usd
        self.source = source or "RentCast AVM"
        self.message = message


def get_rentcast_value(lat, lng, timeout=10):
    """
    Attempt a RentCast AVM value estimate for the given coordinates.

    Returns a LandValueResult. Never raises for expected failures (missing key,
    network error, no coverage) — those come back as ok=False with a message.
    """
    api_key = os.environ.get(ENV_KEY, "").strip()
    if not api_key:
        return LandValueResult(
            ok=False,
            source="RentCast AVM (no key configured)",
            message=(
                f"No API key configured. Set {ENV_KEY} to enable the optional "
                "RentCast lookup. The regional-average land proxy is used instead."
            ),
        )

    query = urllib.parse.urlencode({"latitude": lat, "longitude": lng})
    url = f"{RENTCAST_AVM_URL}?{query}"

    try:
        req = urllib.request.Request(
            url,
            headers={
                "X-Api-Key": api_key,
                "Accept": "application/json",
                "User-Agent": "dc-site-estimator/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return LandValueResult(
            ok=False,
            source="RentCast AVM",
            message=(
                f"RentCast returned HTTP {e.code} (often means no coverage for a "
                "raw coordinate). Falling back to the regional proxy."
            ),
        )
    except (urllib.error.URLError, TimeoutError) as e:
        return LandValueResult(
            ok=False,
            source="RentCast AVM",
            message=f"Could not reach RentCast ({e}). Using the regional proxy.",
        )
    except json.JSONDecodeError:
        return LandValueResult(
            ok=False,
            source="RentCast AVM",
            message="RentCast returned an unparseable response.",
        )

    value = data.get("price") or data.get("value")
    if not isinstance(value, (int, float)):
        return LandValueResult(
            ok=False,
            source="RentCast AVM",
            message="RentCast returned no value estimate for this coordinate.",
        )

    return LandValueResult(
        ok=True,
        value_usd=float(value),
        source="RentCast AVM (address-matched)",
    )
