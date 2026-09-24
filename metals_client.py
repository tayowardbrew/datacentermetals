"""
Metals.Dev API client for live industrial-metal spot prices.

Free tier (no credit card) covers copper, aluminum, lead, nickel, zinc, returned
in USD per metric tonne by default. Docs: https://metals.dev/docs
Endpoint: https://api.metals.dev/v1/latest?api_key=<KEY>&currency=USD&unit=mt

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


class MetalsResult:
    """Outcome of a live-price fetch attempt."""

    def __init__(self, ok, prices=None, source=None, message=None):
        self.ok = ok
        # prices: dict like {"copper": 9100.0, "aluminum": 2400.0} in USD/tonne
        self.prices = prices or {}
        self.source = source or "Metals.Dev API"
        self.message = message

    def price(self, metal):
        return self.prices.get(metal)


def get_metal_prices(timeout=10):
    """
    Fetch latest copper/aluminum prices in USD per metric tonne.

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
    prices = {}
    for m in ("copper", "aluminum"):
        val = metals.get(m)
        if isinstance(val, (int, float)):
            prices[m] = float(val)

    if not prices:
        return MetalsResult(
            ok=False,
            source="Metals.Dev API",
            message="Metals.Dev response did not include copper/aluminum prices.",
        )

    ts = data.get("timestamps", {}).get("metal", "latest")
    return MetalsResult(
        ok=True,
        prices=prices,
        source=f"Metals.Dev API ({ts})",
    )
