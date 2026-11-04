"""
remit-mcp — Diaspora Remittance Intelligence MCP Server
Copyright (c) 2026 Gabriel Mahia / AI Kung Fu LLC. MIT License.

Research basis:
  World Bank Remittance Prices Worldwide database (remittanceprices.worldbank.org)
  "Democratizing AI in Africa" arXiv:2408.17216 — federated AI for underserved populations
  IrokoBench arXiv:2406.03368 — African language AI capability benchmark
  World Bank "Migration and Development Brief" 2025 — Kenya top-10 remittance recipient

MCP server exposing remittance corridor comparison for AI agents. THE PRICING DATA IS SYNTHETIC (see DEMO notes).
Context, not data held here: Kenya received USD 4.94 billion in remittances in calendar 2024 (USD 4.18 billion in 2023) per the Central Bank of Kenya,
reported by Business Daily; USD 5.08 billion in FY2024/25.
"""

import hashlib
import json
import logging
import os
import re
from datetime import UTC, datetime, timezone
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from typing import Annotated

import requests
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
_log = logging.getLogger("remit-mcp")

try:
    _VERSION = _pkg_version("remit-mcp")
except PackageNotFoundError:  # a source tree that was never installed
    _VERSION = "0+unknown"


mcp = FastMCP(
    name="remit-mcp",
    version=_VERSION,
    instructions=(
        "Kenya diaspora remittance intelligence. "
        "Compare corridor costs, find optimal timing windows, and estimate fees across providers. "
        "Data: SYNTHETIC demonstration prices; not from the World Bank RPW database and not live exchange rates. "
        "DEMO: Synthetic pricing data representative of Kenya corridor patterns. "
        "Not financial advice — verify live rates before sending."
    )
)

# Annotations tell clients which tools are safe to auto-approve. Live tools still change nothing, but they contact an outside service.
LIVE_READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True}
LIVE_TOOLS = {"live_exchange_rate", "kenya_remittance_inflows"}
_UA = {"User-Agent": "remit-mcp (https://github.com/gabrielmahia/remit-mcp)", "Accept": "application/json"}
FX_URL = "https://open.er-api.com/v6/latest/{base}"
WB_URL = "https://api.worldbank.org/v2/country/KEN/indicator/{indicator}"


def _get_json(url: str, params: dict | None = None, timeout: float = 15.0):
    r = requests.get(url, params=params, headers=_UA, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _audit(tool, params, outcome):
    safe = {k: hashlib.sha256(str(v).encode()).hexdigest()[:8] + "..."
            if k in {"phone","account","email"} else str(v)
            for k, v in params.items()}
    _log.info("TOOL=%s PARAMS=%s OUTCOME=%s", tool, safe, outcome)

# ── DEMO pricing data ─────────────────────────────────────────────────────────
# Source: "DEMO — Synthetic data representative of World Bank RPW Kenya corridor (2024-2026)"
# Real data: remittanceprices.worldbank.org/en/corridor/United-States/Kenya
CORRIDORS = {
    "US_KE": {
        "name": "USA → Kenya",
        "providers": [
            {"name": "M-PESA Global (Safaricom)", "fee_usd": 4.99, "rate_premium_pct": 0.8,
             "delivery": "Instant", "method": "Mobile money", "min_usd": 10, "max_usd": 2000,
             "world_bank_avg_pct": 6.5},
            {"name": "WorldRemit", "fee_usd": 3.99, "rate_premium_pct": 1.2,
             "delivery": "Minutes", "method": "Mobile money/Bank", "min_usd": 5, "max_usd": 3000,
             "world_bank_avg_pct": 5.8},
            {"name": "Wise", "fee_usd": 4.50, "rate_premium_pct": 0.4,
             "delivery": "1-2 days", "method": "Bank account", "min_usd": 50, "max_usd": 10000,
             "world_bank_avg_pct": 4.1},
            {"name": "Remitly", "fee_usd": 2.99, "rate_premium_pct": 1.8,
             "delivery": "3-5 days", "method": "Economy/Express", "min_usd": 15, "max_usd": 5000,
             "world_bank_avg_pct": 5.9},
            {"name": "Western Union", "fee_usd": 7.99, "rate_premium_pct": 2.1,
             "delivery": "Minutes", "method": "Cash/Mobile/Bank", "min_usd": 1, "max_usd": 2500,
             "world_bank_avg_pct": 8.7},
            {"name": "MoneyGram", "fee_usd": 8.99, "rate_premium_pct": 2.3,
             "delivery": "Minutes", "method": "Cash/Bank", "min_usd": 1, "max_usd": 2500,
             "world_bank_avg_pct": 9.1},
        ]
    },
    "UK_KE": {
        "name": "UK → Kenya",
        "providers": [
            {"name": "M-PESA Global (Vodacom UK)", "fee_gbp": 1.99, "rate_premium_pct": 0.6,
             "delivery": "Instant", "method": "Mobile money", "min_usd": 10, "max_usd": 2000,
             "world_bank_avg_pct": 5.2},
            {"name": "Wise", "fee_gbp": 3.20, "rate_premium_pct": 0.4,
             "delivery": "Same day", "method": "Bank/M-PESA", "min_usd": 50, "max_usd": 10000,
             "world_bank_avg_pct": 4.8},
            {"name": "WorldRemit", "fee_gbp": 1.99, "rate_premium_pct": 1.1,
             "delivery": "Minutes", "method": "Mobile money", "min_usd": 5, "max_usd": 3000,
             "world_bank_avg_pct": 5.5},
        ]
    },
    "CA_KE": {
        "name": "Canada → Kenya",
        "providers": [
            {"name": "Wise", "fee_cad": 5.50, "rate_premium_pct": 0.5,
             "delivery": "1-2 days", "method": "Bank account", "min_usd": 50, "max_usd": 10000,
             "world_bank_avg_pct": 5.1},
            {"name": "WorldRemit", "fee_cad": 3.99, "rate_premium_pct": 1.3,
             "delivery": "Minutes", "method": "Mobile money", "min_usd": 5, "max_usd": 3000,
             "world_bank_avg_pct": 6.0},
        ]
    }
}

@mcp.tool(description="Compare typical costs of sending money to Kenya on one corridor (US_KE, UK_KE or CA_KE) for an amount in US dollars, across provider types. Use when someone asks which way of sending money costs least. An unknown corridor returns an error listing the supported ones. The prices are SYNTHETIC illustrations, not World Bank or live provider data. Returns the corridor, amount, the provider comparison, the global average and SDG target percentages for context, and a note. Always check real prices at remittanceprices.worldbank.org before sending. Read-only; no side effects.", annotations={
    "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False
})
def compare_remittance_corridors(
    corridor: Annotated[str, "Corridor code: US_KE, UK_KE, CA_KE"],
    amount_usd: Annotated[float, "Amount in USD to send (or equivalent)"] = 200.0
) -> dict:
    """
    Compare all providers for a remittance corridor.
    Returns fees, exchange rate premium, total cost, and World Bank benchmark.
    Data: DEMO — synthetic representative of World Bank RPW Kenya corridors (2024-2026).
    """
    _audit("compare_remittance_corridors", {"corridor": corridor, "amount_usd": amount_usd}, "FETCH")

    if corridor not in CORRIDORS:
        return {"error": f"Corridor {corridor} not supported. Available: {list(CORRIDORS.keys())}"}

    corridor_data = CORRIDORS[corridor]
    providers = corridor_data["providers"]
    results = []

    for p in providers:
        fee = p.get("fee_usd") or p.get("fee_gbp") or p.get("fee_cad") or 0.0
        # Total cost = flat fee + exchange rate premium on amount
        rate_cost = amount_usd * p["rate_premium_pct"] / 100
        total_cost = fee + rate_cost
        total_cost_pct = (total_cost / amount_usd * 100) if amount_usd else 0
        wb_avg = p.get("world_bank_avg_pct", 6.0)

        results.append({
            "provider": p["name"],
            "flat_fee_usd": round(fee, 2),
            "exchange_premium_pct": p["rate_premium_pct"],
            "total_cost_usd": round(total_cost, 2),
            "total_cost_pct": round(total_cost_pct, 2),
            "vs_wb_benchmark": "BELOW avg ✅" if total_cost_pct < wb_avg else "ABOVE avg ⚠️",
            "delivery_time": p["delivery"],
            "method": p["method"],
            "recipient_receives_approx": f"KES {(amount_usd - total_cost) * 130:.0f}",
        })

    results.sort(key=lambda x: x["total_cost_usd"])
    cheapest = results[0]["provider"] if results else "—"

    return {
        "corridor": corridor_data["name"],
        "amount_usd": amount_usd,
        "providers_compared": len(results),
        "cheapest_provider": cheapest,
        "results": results,
        "world_bank_global_avg_pct": 6.3,
        "sdg_target_pct": 3.0,
        "note": "DEMO — Synthetic data representative of World Bank RPW Kenya corridors. Verify live rates before sending.",
        "source": "DEMO: synthetic, NOT World Bank data. Check real corridor costs at remittanceprices.worldbank.org"
    }

@mcp.tool(description="Estimate how much a person could save by moving from their current provider to a cheaper option on a corridor, per month and per year in US dollars and in KES (at a fixed 130 KES per USD). Use when someone asks what switching would save. An unknown corridor returns an error. Based on SYNTHETIC illustrative prices and a fixed exchange rate, not live data. Returns the monthly and annual savings and a note. Verify with live provider rates. Read-only; no side effects.", annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def estimate_savings(
    corridor: Annotated[str, "Corridor code: US_KE, UK_KE, CA_KE"],
    monthly_amount_usd: Annotated[float, "Monthly remittance amount in USD"],
    current_provider: Annotated[str, "Current provider name (partial match OK)"]
) -> dict:
    """
    Calculate annual savings if switching to cheapest available provider.
    """
    _audit("estimate_savings", {"corridor": corridor, "monthly": monthly_amount_usd}, "CALC")

    comparison = compare_remittance_corridors(corridor, monthly_amount_usd)
    if "error" in comparison:
        return comparison

    results = comparison["results"]
    current = next((r for r in results if current_provider.lower() in r["provider"].lower()), None)
    cheapest = results[0]

    if not current:
        return {"error": f"Provider '{current_provider}' not found in corridor. Options: {[r['provider'] for r in results]}"}

    monthly_savings = current["total_cost_usd"] - cheapest["total_cost_usd"]
    annual_savings = monthly_savings * 12

    return {
        "current_provider": current["provider"],
        "current_monthly_cost_usd": current["total_cost_usd"],
        "cheapest_provider": cheapest["provider"],
        "cheapest_monthly_cost_usd": cheapest["total_cost_usd"],
        "monthly_savings_usd": round(monthly_savings, 2),
        "annual_savings_usd": round(annual_savings, 2),
        "annual_savings_kes": round(annual_savings * 130, 0),
        "note": "DEMO — Synthetic data. Verify with live provider rates."
    }

@mcp.tool(description="List the remittance corridors the server supports (US_KE, UK_KE, CA_KE) with plain descriptions, plus context on Kenya's remittance inflows (USD 4.94 billion in calendar 2024 per the Central Bank of Kenya). Use first, to learn valid corridor codes for the other tools. Takes no arguments. Returns the corridors, their descriptions and a note that the data are synthetic. The server does not model PAPSS or Pesalink routes. Read-only; no side effects.", annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def list_corridors() -> dict:
    """List all supported remittance corridors."""
    return {
        "corridors": list(CORRIDORS.keys()),
        "descriptions": {k: v["name"] for k, v in CORRIDORS.items()},
        "note": "DEMO data (synthetic prices). Context: Kenya received USD 4.94 billion in remittances in calendar 2024 per the Central Bank of Kenya."
    }

@mcp.tool(annotations=LIVE_READ_ONLY, description="Get today's exchange rate from a sending currency (for example USD, GBP, CAD or EUR) to Kenyan shillings, from a free live rates service, and optionally convert an amount. Use when someone asks how many shillings their money is worth today, or wants to sanity-check a provider's quoted rate. Returns the rate, the converted amount if given, the time the rates were last updated, the source and its required attribution; on a network or service failure it returns an error instead of a rate. Read-only; contacts an external service.")
def live_exchange_rate(base_currency: Annotated[str, "Three-letter ISO code of the sending currency, for example USD, GBP, CAD or EUR."] = "USD",
                       amount: Annotated[float | None, "Optional amount in the sending currency to convert to KES; must be positive."] = None) -> dict:
    base = (base_currency or "").strip().upper()
    meta = {"source": "LIVE — ExchangeRate-API open access endpoint (open.er-api.com)", "attribution": "Rates By Exchange Rate API: https://www.exchangerate-api.com", "retrieved_at": _now()}
    if not re.fullmatch(r"[A-Z]{3}", base):
        return {"error": "base_currency must be a three-letter ISO code such as USD", **meta}
    if amount is not None and amount <= 0:
        return {"error": "amount must be positive", **meta}
    try:
        d = _get_json(FX_URL.format(base=base))
        if d.get("result") != "success" or "KES" not in d.get("rates", {}):
            raise ValueError(d.get("error-type", "no KES rate"))
        rate = float(d["rates"]["KES"])
    except (requests.RequestException, ValueError, KeyError, TypeError) as e:
        return {"error": f"the rates service did not return a usable KES rate ({type(e).__name__}); no rate is given without it", **meta}
    out = {"base_currency": base, "kes_per_unit": round(rate, 4), "rates_last_updated": d.get("time_last_update_utc"),
           "note": "A mid-market reference rate updated about once a day: providers add a margin and fees, so compare their quoted rate with this.", **meta}
    if amount is not None:
        out["amount"] = amount
        out["kes_at_reference_rate"] = round(amount * rate, 2)
    return out


@mcp.tool(annotations=LIVE_READ_ONLY, description="Get Kenya's official personal remittance inflows for recent years from the World Bank's World Development Indicators, in US dollars and as a share of GDP. Use when someone needs the size or trend of money sent home to Kenya, for context on the corridors. Returns one row per year with both measures, the indicator codes, the source with its licence and the retrieval time; on a network or service failure it returns an error instead of figures. Read-only; contacts an external service.")
def kenya_remittance_inflows(years: Annotated[int, "How many of the most recent years with data to return, between 1 and 20."] = 5) -> dict:
    meta = {"source": "LIVE — World Bank World Development Indicators API (api.worldbank.org)", "licence": "CC BY 4.0 (World Bank open data)", "retrieved_at": _now(),
            "note": "The World Bank series (personal remittances received) is broader than the Central Bank of Kenya's diaspora remittance figure, so the two differ."}
    if not 1 <= years <= 20:
        return {"error": "years must be between 1 and 20", **meta}
    series = {"usd": "BX.TRF.PWKR.CD.DT", "pct_gdp": "BX.TRF.PWKR.DT.GD.ZS"}
    try:
        got = {}
        for key, ind in series.items():
            d = _get_json(WB_URL.format(indicator=ind), {"format": "json", "mrnev": years})
            got[key] = {row["date"]: row["value"] for row in d[1] if row.get("value") is not None}
    except (requests.RequestException, ValueError, KeyError, TypeError, IndexError) as e:
        return {"error": f"the World Bank API did not return usable data ({type(e).__name__}); no figures are given without it", **meta}
    rows = [{"year": y, "usd": got["usd"].get(y), "pct_gdp": round(got["pct_gdp"][y], 2) if y in got["pct_gdp"] else None} for y in sorted(set(got["usd"]) | set(got["pct_gdp"]), reverse=True)]
    return {"country": "Kenya", "indicators": series, "rows": rows, **meta}


def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
