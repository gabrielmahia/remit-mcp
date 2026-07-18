# 💸 remit-mcp
<!-- mcp-name: io.github.gabrielmahia/remit-mcp -->

[![remit-mcp Glama score](https://glama.ai/mcp/servers/gabrielmahia/remit-mcp/badges/score.svg)](https://glama.ai/mcp/servers/gabrielmahia/remit-mcp)
[![smithery badge](https://smithery.ai/badge/@gabrielmahia/remit-mcp)](https://smithery.ai/server/@gabrielmahia/remit-mcp)


---
**Compatible with `claude-sonnet-5`** (released 2026-06-30) — Anthropic's most agentic
Sonnet yet. Runs multi-step tool chains end-to-end without stopping short.
Install: `pip install remit-mcp` · Use with any MCP client.

---


Remittance corridor fees to East Africa often run well above the UN SDG 10.c target of 3% by 2030 — but comparing corridors requires checking each provider manually.

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

## Part of the East Africa Coordination Stack

This MCP server is one of 32 tools in the Kenya coordination infrastructure.
Connect it to [`africa-coord-bus`](https://github.com/gabrielmahia/africa-coord-bus) —
the coordination event bus that routes signals between domains automatically.

```bash
pip install africa-coord-bus
```

All 32 servers: [pypi.org/user/gmahia](https://pypi.org/user/gmahia/)
Live demo: [coord-cascade-demo](https://github.com/gabrielmahia/coord-cascade-demo)

## IP & Collaboration

MIT licensed. Feedback via GitHub Issues only — pull requests are not accepted. Demo data is labeled DEMO and is not suitable for operational decisions. Full policy: [docs/architecture/IP_POLICY.md](docs/architecture/IP_POLICY.md). Security reports: see [SECURITY.md](SECURITY.md).

<!-- interconnect:v1 -->
## Part of the East Africa coordination stack

- **Install & run:** `pip install reli-cli && reli list` — 33 MCP servers on the [official MCP Registry](https://registry.modelcontextprotocol.io) under `io.github.gabrielmahia`
- **Evaluate any model on Swahili agent tasks:** [kipimo](https://github.com/gabrielmahia/kipimo) · [dataset](https://huggingface.co/datasets/gmahia/kipimo) · [leaderboard](https://huggingface.co/spaces/gmahia/kipimo-leaderboard)
- **Coordinate across servers:** [africa-coord-bus](https://pypi.org/project/africa-coord-bus/) — offline-first event bus with a built-in Kenya routing table
- **Datasets:** [huggingface.co/gmahia](https://huggingface.co/gmahia) · **Docs hub:** [nairobi-stack](https://github.com/gabrielmahia/nairobi-stack)

Model-agnostic by design: closed APIs, open-weight models, and small distilled models are all first-class citizens.
<!-- /interconnect:v1 -->
