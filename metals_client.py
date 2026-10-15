"""
Metals.Dev API client for live industrial-metal spot prices.

One call to /v1/latest returns every metal Metals.Dev supports: base metals
(copper, aluminum, lead, nickel, zinc) and precious metals (gold, silver,
platinum, palladium). Docs: https://metals.dev/docs , symbols: https://metals.dev/symbols
Endpoint: https://api.metals.dev/v1/latest?api_key=<KEY>&currency=USD&unit=mt

With unit=mt every metal (precious included) is quoted in USD per metric tonne;
we still read the response's own "unit" field and normalise defensively, because
precious metals default to troy ounces if the unit is ever ignored.

Metals.Dev does NOT carry tin, cobalt, lithium, gallium or steel. Those are priced
from dated static benchmarks in metals_mix.py (labelled STATIC everywhere), rather
than adding a second, unrelated price provider. See SOURCES.md entry 14.

The API key is read from the METALS_DEV_API_KEY environment variable. If it is
missing, this module returns a clear "no API key configured" result rather than
raising, so the rest of the app degrades gracefully.
"""

import os
import json
import urllib.request
import urllib.error
import urllib.parse

METALS_DEV_LATEST_URL = "https://api.metals.dev/v1/latest"
ENV_KEY = "METALS_DEV_API_KEY"

# Metals we read from the single /v1/latest call (all on Metals.Dev's symbol list).
# zinc / platinum / palladium are available too but are not modelled (no citable
# per-MW data-center intensity was found; see SOURCES.md entry 14).
LIVE_METALS = ("copper", "aluminum", "nickel", "lead", "silver", "gold")

# Multipliers to convert a quoted price into USD per metric tonne.
TROY_OZ_PER_TONNE = 32_150.7466
_UNIT_TO_PER_TONNE = {"mt": 1.0, "kg": 1_000.0, "g": 1_000_000.0, "toz": TROY_OZ_PER_TONNE}


class MetalsResult:
    """Outcome of a live-price fetch attempt."""

    def __init__(self, ok, prices=None, source=None, message=None):
        self.ok = ok
        # prices: dict like {"copper": 9100.0, "gold": 1.2e8, ...} in USD/tonne
        self.prices = prices or {}
        self.source = source or "Metals.Dev API"
        self.message = message

    def price(self, metal):
        return self.prices.get(metal)


def get_metal_prices(timeout=10):
    """
    Fetch latest prices for every LIVE_METALS entry, in USD per metric tonne.

    Returns a MetalsResult. Never raises for the expected failure modes
    (missing key, network error, bad response) — those come back as
    ok=False with a human-readable message.
    """
    api_key = os.environ.get(ENV_KEY, "").strip()
    if not api_key:
        return MetalsResult(
            ok=False,
            source="Metals.Dev API (no key configured)",
            message=(
                f"No API key configured. Set the {ENV_KEY} environment variable "
                "to enable live commodity pricing. See README / .env.example."
            ),
        )

    params = f"?api_key={urllib.parse.quote(api_key)}&currency=USD&unit=mt"
    url = METALS_DEV_LATEST_URL + params

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "dc-site-estimator/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
    except urllib.error.HTTPError as e:
        return MetalsResult(
            ok=False,
            source="Metals.Dev API",
            message=f"Metals.Dev returned HTTP {e.code}. Check the API key and quota.",
        )
    except (urllib.error.URLError, TimeoutError) as e:
        return MetalsResult(
            ok=False,
            source="Metals.Dev API",
            message=f"Could not reach Metals.Dev ({e}). Live pricing unavailable.",
        )
    except json.JSONDecodeError:
        return MetalsResult(
            ok=False,
            source="Metals.Dev API",
            message="Metals.Dev returned an unparseable response.",
        )

    if data.get("status") != "success":
        return MetalsResult(
            ok=False,
            source="Metals.Dev API",
            message=f"Metals.Dev reported: {data.get('status', 'unknown error')}.",
        )

    metals = data.get("metals", {})
    factor = _UNIT_TO_PER_TONNE.get(str(data.get("unit", "mt")).lower(), 1.0)
    prices = {}
    for m in LIVE_METALS:
        val = metals.get(m)
        if isinstance(val, (int, float)) and val > 0:
            prices[m] = float(val) * factor

    if not prices:
        return MetalsResult(
            ok=False,
            source="Metals.Dev API",
            message="Metals.Dev response did not include any of the expected metal prices.",
        )

    ts = data.get("timestamps", {}).get("metal", "latest")
    return MetalsResult(
        ok=True,
        prices=prices,
        source=f"Metals.Dev API ({ts})",
    )
