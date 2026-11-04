"""The live tools: parsing, provenance, validation and failure behaviour, with the network mocked (CI never depends on the services)."""
import requests

from remit_mcp import server


def test_exchange_rate_converts_and_names_its_source(monkeypatch):
    monkeypatch.setattr(server, "_get_json", lambda url, params=None, timeout=15.0: {"result": "success", "rates": {"KES": 129.5}, "time_last_update_utc": "Tue, 03 Nov 2026 00:02:31 +0000"})
    r = server.live_exchange_rate("usd", 100)
    assert r["base_currency"] == "USD" and r["kes_per_unit"] == 129.5 and r["kes_at_reference_rate"] == 12950.0
    assert r["source"].startswith("LIVE") and "exchangerate-api.com" in r["attribution"] and r["rates_last_updated"]


def test_exchange_rate_failures_and_bad_input_never_give_a_rate(monkeypatch):
    def boom(url, params=None, timeout=15.0):
        raise requests.ConnectionError("down")
    monkeypatch.setattr(server, "_get_json", boom)
    assert "error" in server.live_exchange_rate("USD") and "kes_per_unit" not in server.live_exchange_rate("USD")
    monkeypatch.setattr(server, "_get_json", lambda url, params=None, timeout=15.0: {"result": "error", "error-type": "unsupported-code"})
    assert "kes_per_unit" not in server.live_exchange_rate("XYZ")
    assert "error" in server.live_exchange_rate("US") and "error" in server.live_exchange_rate("USD", -5)


def test_remittance_inflows_merge_both_series_newest_first(monkeypatch):
    data = {"BX.TRF.PWKR.CD.DT": [{"date": "2025", "value": 5.1e9}, {"date": "2024", "value": 4.9e9}], "BX.TRF.PWKR.DT.GD.ZS": [{"date": "2025", "value": 3.764}, {"date": "2024", "value": 3.9}]}
    monkeypatch.setattr(server, "_get_json", lambda url, params=None, timeout=15.0: [{}, data[url.rsplit("/", 1)[1]]])
    r = server.kenya_remittance_inflows(2)
    assert r["rows"] == [{"year": "2025", "usd": 5.1e9, "pct_gdp": 3.76}, {"year": "2024", "usd": 4.9e9, "pct_gdp": 3.9}]
    assert "CC BY 4.0" in r["licence"] and "Central Bank of Kenya" in r["note"]


def test_remittance_inflows_failures_and_bad_input_never_give_figures(monkeypatch):
    def boom(url, params=None, timeout=15.0):
        raise requests.Timeout("slow")
    monkeypatch.setattr(server, "_get_json", boom)
    assert "error" in server.kenya_remittance_inflows() and "rows" not in server.kenya_remittance_inflows()
    assert "error" in server.kenya_remittance_inflows(0) and "error" in server.kenya_remittance_inflows(50)
