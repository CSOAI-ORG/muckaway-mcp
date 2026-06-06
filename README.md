# 🗑️ MuckAway MCP Server

**Model Context Protocol server for waste management, skip hire, grab lorry booking, and aquaculture water quality monitoring.**

[![PyPI](https://img.shields.io/pypi/v/muckaway-mcp)](https://pypi.org/project/muckaway-mcp/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🎯 What This Is

MuckAway MCP is the **first** production MCP server for the **waste management and aquaculture** verticals. While the MCP ecosystem has 9,400+ servers, **zero** exist for:

- Waste classification (EWC codes)
- Skip hire quoting
- Grab lorry booking
- Waste Transfer Notes (WTN)
- DEFRA compliance checking
- Aquaculture water quality monitoring

This server fills that gap — providing AI agents with real-world tools for waste management, construction logistics, and fish farm operations.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           MuckAway MCP Server               │
│                                             │
│  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Waste Mgmt │  │  Aquaculture        │  │
│  │  Tools      │  │  Tools              │  │
│  │             │  │                     │  │
│  │ • EWC lookup│  │ • Water quality     │  │
│  │ • Skip quote│  │   monitor           │  │
│  │ • Grab book │  │                     │  │
│  │ • WTN gen   │  │                     │  │
│  │ • DEFRA chk │  │                     │  │
│  └─────────────┘  └─────────────────────┘  │
│                                             │
│  Connected to: meok.ai Sovereign Temple     │
│  Swarm: SOV3 (PBFT-MoE council)             │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Installation

```bash
pip install muckaway-mcp
```

Or install from source:

```bash
git clone https://github.com/CSOAI-ORG/muckaway-mcp.git
cd muckaway-mcp
pip install -e ".[dev]"
```

---

## 🚀 Usage

### Running the Server

```bash
# Via the CLI entry point
muckaway-mcp

# Or directly
python -m muckaway_mcp.server
```

The server runs as a stdio-based MCP server compatible with Claude, Claude Code, and any MCP client.

### Connecting to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "muckaway": {
      "command": "muckaway-mcp",
      "env": {}
    }
  }
}
```

---

## 📋 Available Tools

### Waste Management

| Tool | Description | Example |
|------|-------------|---------|
| `waste_classification_lookup` | Look up EWC waste code classification | `"17 01 01"` → Concrete, non-hazardous, £45/tonne |
| `skip_hire_quote` | Generate skip hire quote by postcode, waste type, size | CM8 1XY, mixed construction, 8-yard → £290/week |
| `grab_lorry_booking` | Check availability and price for grab lorry | 50m³ soil → 4 loads, £510, available in 3 days |
| `waste_transfer_note_generator` | Generate a Waste Transfer Note document | Site, waste type, carrier, destination |
| `defra_compliance_check` | Check waste disposal compliance with DEFRA | Hazardous waste + landfill → non-compliant |

### Aquaculture

| Tool | Description | Thresholds |
|------|-------------|------------|
| `water_quality_monitor` | Monitor pH, ammonia, nitrite, temperature | pH 6.5-8.5, ammonia <0.02mg/L, nitrite <0.1mg/L |

---

## 💡 Example Interactions

**"What is waste code 17 01 01?"**
```
→ EWC 17 01 01: Concrete (non-hazardous)
  Disposal: Crushing/recycling or inert landfill
  Typical cost: £45 per tonne
```

**"How much for an 8-yard skip in CM8 for mixed construction waste?"**
```
→ Base price: £290/week
  Hazardous surcharge: £0
  Permit surcharge: £30
  Total: £320/week
  Max 4 tonnes | 3.6m x 1.8m x 1.1m
```

**"I need a grab lorry for 50m³ of soil in CM8"**
```
→ 4 loads required (16m³ per lorry)
  Estimated cost: £510
  Available from: 2026-06-09
  Requires: 3.5m width, 4.0m height clearance
```

**"Is it compliant to put asbestos in a skip?"**
```
→ NO — Asbestos is hazardous waste
  Required: Hazardous consignment note
  Required: Licensed hazardous carrier
  Required: Permitted hazardous landfill
```

**"My pond water is pH 8.8, ammonia 0.05, nitrite 0.15, temp 22°C"**
```
→ OVERALL: WARNING
  pH: WARNING (optimal: 6.5-8.5)
  Ammonia: CRITICAL (optimal: <0.02)
  Nitrite: WARNING (optimal: <0.1)
  Temperature: OPTIMAL
  
  Action: Stop feeding. 50% water change. Check biofilter.
  Fish health risk: MODERATE — action needed within 24h
```

---

## 🏢 Real-World Context

This MCP server is built by **MEOK AI LTD** and powers **muckaway.ai** — a waste management platform covering:

- **Skip hire** (4yd to 40yd)
- **Grab lorry booking** (16m³ capacity)
- **Waste classification** (full EWC database)
- **DEFRA compliance** (11 regulatory frameworks)
- **Real-world testing** at IOK Farm, Essex

---

## 🧪 Testing

```bash
pytest
```

With coverage:

```bash
pytest --cov=muckaway_mcp --cov-report=term-missing
```

---

## 📦 Publishing

```bash
# Build
python -m build

# Publish to PyPI
python -m twine upload dist/*
```

---

## 🔗 Related Projects

| Project | Domain | Description |
|---------|--------|-------------|
| **meok.ai** | meok.ai | AI OS — 38 MCPs, consciousness framework |
| **muckaway.ai** | muckaway.ai | Waste management platform |
| **planthire.ai** | planthire.ai | Plant & equipment hire |
| **grabhire.ai** | grabhire.ai | Haulage & logistics |
| **fishkeeper.ai** | fishkeeper.ai | Aquaculture monitoring |
| **councilof.ai** | councilof.ai | AI governance & compliance |

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

*Built with care by MEOK AI LTD | Part of the SOV3 Swarm*
