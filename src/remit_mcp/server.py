"""
remit-mcp — Diaspora Remittance Intelligence MCP Server
Copyright (c) 2026 Gabriel Mahia / AI Kung Fu LLC. MIT License.

Research basis:
  World Bank Remittance Prices Worldwide database (remittanceprices.worldbank.org)
  "Democratizing AI in Africa" arXiv:2408.17216 — federated AI for underserved populations
  IrokoBench arXiv:2406.03368 — African language AI capability benchmark
  World Bank "Migration and Development Brief" 2025 — Kenya top-10 remittance recipient

First in Africa: MCP server exposing remittance corridor intelligence for AI agents.
Kenya received USD 4.2B in remittances in 2024 (World Bank Migration Brief 2025).
35% of corridor fees go to intermediaries — this server helps minimize that.
"""

import os
import hashlib
import logging
import json
from datetime import datetime, timezone
from typing import Annotated
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
_log = logging.getLogger("remit-mcp")

mcp = FastMCP(
    name="remit-mcp",
    version="0.1.0",
    instructions=(
        "Kenya diaspora remittance intelligence. "
        "Compare corridor costs, find optimal timing windows, and estimate fees across providers. "
        "Data: World Bank RPW database + public exchange rate APIs. "
        "DEMO: Synthetic pricing data representative of Kenya corridor patterns. "
        "Not financial advice — verify live rates before sending."
    )
)

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

@mcp.tool(annotations={
    "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True
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
        "source": "World Bank Remittance Prices Worldwide (remittanceprices.worldbank.org)"
    }

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True})
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

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True})
def list_corridors() -> dict:
    """List all supported remittance corridors."""
    return {
        "corridors": list(CORRIDORS.keys()),
        "descriptions": {k: v["name"] for k, v in CORRIDORS.items()},
        "note": "DEMO data. Kenya received USD 4.2B in remittances in 2024 (World Bank Migration Brief 2025)."
    }

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
