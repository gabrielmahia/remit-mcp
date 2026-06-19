# 💸 remit-mcp

[![remit-mcp Glama score](https://glama.ai/mcp/servers/gabrielmahia/remit-mcp/badges/score.svg)](https://glama.ai/mcp/servers/gabrielmahia/remit-mcp)


**First MCP server for African diaspora remittance optimization.**

```bash
pip install remit-mcp
remit-mcp
```

## Tools
| Tool | What it does |
|------|-------------|
| `compare_remittance_corridors` | Compare all providers for US→KE, UK→KE, CA→KE corridors |
| `estimate_savings` | Calculate annual savings by switching providers |
| `list_corridors` | List all supported corridors |

## Research Basis
- **World Bank Remittance Prices Worldwide** — Global database of corridor costs. SDG target: reduce to 3% by 2030. Current global average: 6.3%. Kenya corridors: 4.1–9.1%.
- **World Bank Migration & Development Brief 2025** — Kenya received USD 4.2B in remittances in 2024. Top-10 African recipient.
- **"Democratizing AI in Africa"** arXiv:2408.17216 — AI tools for financial inclusion in resource-constrained settings.
- **IrokoBench** arXiv:2406.03368 — Swahili AI capability benchmark; multilingual financial AI for Africa.

## DEMO Note
Current data is synthetic, representative of World Bank RPW Kenya corridor patterns.
Real implementation queries: remittanceprices.worldbank.org API + live FX feeds.

---
*© 2026 Gabriel Mahia / AI Kung Fu LLC · MIT License*
