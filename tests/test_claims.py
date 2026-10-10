"""remit-mcp must not make unverifiable superlatives or unsourced statistics, and must not state the remittance total for the wrong year."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEXT = (ROOT / "src" / "remit_mcp" / "server.py").read_text(encoding="utf-8") + (ROOT / "README.md").read_text(encoding="utf-8")


def test_no_first_in_africa_claim_and_no_unsourced_intermediary_statistic():
    assert "First in Africa" not in TEXT and "35% of corridor fees" not in TEXT


def test_the_2024_remittance_total_is_not_the_2023_figure():
    assert "USD 4.2B in remittances in 2024" not in TEXT and "4.2B" not in TEXT
    assert "4.94" in TEXT and "Central Bank of Kenya" in TEXT


def test_synthetic_prices_are_not_attributed_to_the_world_bank():
    assert "Kenya corridors: 4.1" not in TEXT and "synthetic" in TEXT.lower()


def test_the_papss_context_says_what_the_server_does_not_model():
    assert "PAPSS" in TEXT and "does not model" in TEXT


def test_tool_outputs_and_instructions_do_not_claim_the_synthetic_data_comes_from_the_world_bank():
    assert "Data: World Bank RPW database + public exchange rate APIs" not in TEXT
    assert '"source": "World Bank Remittance Prices Worldwide' not in TEXT
    assert "NOT World Bank data" in TEXT
