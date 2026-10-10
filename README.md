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
- **World Bank Remittance Prices Worldwide** is the database to check real corridor costs against (SDG 10.c target: 3% by 2030). This server's corridor prices are **synthetic** and are not World Bank figures.
- **Central Bank of Kenya**: Kenya received USD 4.94 billion in remittances in calendar 2024 (USD 4.18 billion in 2023), reported by Business Daily; a record USD 5.08 billion in FY2024/25; the CBK's own release puts 2024 at Ksh 666.7 billion, about 4% of GDP. (An earlier version of this README said USD 4.2 billion for 2024, which was the 2023 level.)

## Context: PAPSS and Pesalink (2026), not modelled here
In February 2026 Kenya's Pesalink instant-payment network linked to the Pan-African Payment and Settlement System (PAPSS), so that PAPSS participants can send into Kenyan banks and mobile-money wallets in local currency (source: PAPSS and Pesalink announcements, 26 Feb 2026). This server compares US, UK and Canada corridors only; it does not model intra-African or PAPSS routes.

## DEMO Note
Current data is synthetic, representative of World Bank RPW Kenya corridor patterns.
Real implementation queries: remittanceprices.worldbank.org API + live FX feeds.

---
*© 2026 Gabriel Mahia / AI Kung Fu LLC · MIT License*

## Part of the East Africa Coordination Stack

This MCP server is part of the Kenya coordination infrastructure.
Connect it to [`africa-coord-bus`](https://github.com/gabrielmahia/africa-coord-bus) —
the coordination event bus that routes signals between domains automatically.

```bash
pip install africa-coord-bus
```

All servers: [pypi.org/user/gmahia](https://pypi.org/user/gmahia/)
Live demo: [coord-cascade-demo](https://github.com/gabrielmahia/coord-cascade-demo)

## IP & Collaboration

MIT licensed. Feedback via GitHub Issues only — pull requests are not accepted. Demo data is labeled DEMO and is not suitable for operational decisions. Full policy: [docs/architecture/IP_POLICY.md](docs/architecture/IP_POLICY.md). Security reports: see [SECURITY.md](SECURITY.md).

<!-- interconnect:v1 -->
## Part of the East Africa coordination stack

- **Install & run:** `pip install reli-cli && reli list` — the MCP servers on the [official MCP Registry](https://registry.modelcontextprotocol.io) under `io.github.gabrielmahia`
- **Evaluate any model on Swahili agent tasks:** [kipimo](https://github.com/gabrielmahia/kipimo) · [dataset](https://huggingface.co/datasets/gmahia/kipimo) · [leaderboard](https://huggingface.co/spaces/gmahia/kipimo-leaderboard)
- **Coordinate across servers:** [africa-coord-bus](https://pypi.org/project/africa-coord-bus/) — offline-first event bus with a built-in Kenya routing table
- **Datasets:** [huggingface.co/gmahia](https://huggingface.co/gmahia) · **Docs hub:** [nairobi-stack](https://github.com/gabrielmahia/nairobi-stack)

Model-agnostic by design: closed APIs, open-weight models, and small distilled models are all first-class citizens.
<!-- /interconnect:v1 -->
