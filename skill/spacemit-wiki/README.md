# Spacemit Wiki Skill

Give your AI assistant deep knowledge of Spacemit RISC-V chips, boards, drivers, and edge AI deployment.

When installed, your AI assistant knows how to navigate chip specifications, configure peripheral pin muxing, troubleshoot kernel boot hangs, and deploy edge LLMs using the official knowledge base.

For example, you can ask your AI assistant to:
* *"What is the pinout mapping for the 26-pin header on Muse Pi?"*
* *"How do I configure CAN-FD on the K3 Pico via the RT24 real-time core?"*
* *"Why does my custom Debian rootfs hang at kernel boot on the K1?"*
* *"What are the exact Strap pin resistor requirements for eMMC boot on K1 vs K3?"*
* *"How can I deploy a 30B MoE model on the K3 using FP8 quantization?"*

---

## Install

### Quick Setup

Add the official MCP server to your editor (`.cursor/mcp.json` or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "spacemit-wiki": {
      "url": "https://mcp.yao1302.xyz/sse"
    }
  }
}
```

Then copy [`SKILL.md`](./SKILL.md) to your workspace's skill directory (or append it to your `.cursorrules`).

*(Detailed tool reference & multi-client config paths: [mcp.md](./mcp.md))*

---

## What's Included

* **Progressive Disclosure (线-面-点)**: Seamless navigation from boarding guides (`get_developer_journey`), unchunked topic archives (`read_knowledge_atom`), to exact hardware facts (`get_evidence_fact`).
* **Critical Engineering Guardrails**:
  * Strict generational isolation between K1 (2.0 TOPS / X60) and K3 (60 TOPS / X100 + A100).
  * Standardized Bianbu OS & Linux 6.1/6.6 BSP baseline (blocks incompatible Raspberry Pi commands).
  * Mandatory MoE architecture disclosure for 30B-scale models (Active 3B tokens).
  * Hardware safety rules for JTAG pinout reversal, Strap resistor isolation, and unpowered peripheral domains.
* **Token-Efficient Context Reuse**: Reuses evidence already present in conversation history, eliminating duplicate MCP round-trips.

---

## How It Works

1. **Intent Routing**: Routes developer inquiries directly to the optimal tool layer.
2. **Context Reuse**: Reuses loaded topic archives across follow-up questions to save tokens.
3. **Deep Fallback**: Automatically drills down into 1,052 official datasheet chapters (`search_raw_sources` ➔ `read_raw_source_file`) when topic archives lack obscure details.
4. **Structured Output**: Formats pin muxing, thermal impedance, and register maps into clean Markdown tables.

---

## References & Rules

* [SKILL.md](./SKILL.md) — Master instructions and tool selection matrix
* [mcp.md](./mcp.md) — MCP setup and tool schema reference
* [rules/hardware-safety.md](./rules/hardware-safety.md) — Hardware wiring & debugging guardrails
* [rules/generational.md](./rules/generational.md) — Generational isolation & model transparency
* [rules/system-baseline.md](./rules/system-baseline.md) — Operating system & software stack baseline
* [evals/evals.json](./evals/evals.json) — Automated regression test suite
