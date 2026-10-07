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
* **Token-Efficient Context Reuse & Search Ceilings**:
  * Reuses evidence already present in conversation history, eliminating duplicate MCP round-trips.
  * Strict L1~L4 search depth ceilings and sufficiency stop checks to prevent over-searching and token drain.
  * Hourglass communication model: Bottom-Line-Up-Front (BLUF) + accessible analogies before dense registers.

---

## How It Works

1. **Intent Leveling & Depth Ceiling**: Routes developer inquiries directly to the optimal tool layer and strictly caps search depth for conceptual/architectural queries.
2. **Sufficiency Stop**: Terminates further queries immediately once core claims and evidence are validated.
3. **Context Reuse**: Reuses loaded topic archives across follow-up questions to save tokens.
4. **Deep Fallback**: Drills down into 1,180 official datasheet chapters (`search_raw_sources` ➔ `read_raw_source_file`) only for L4-level error debugging.
5. **Hourglass Output**: Leads with clear conclusions and practical analogies, backed by exact facts, with on-demand drill-down invitations.

---

## References & Rules

* [SKILL.md](./SKILL.md) — Master instructions and tool selection matrix
* [mcp.md](./mcp.md) — MCP setup and tool schema reference
* [rules/search-efficiency.md](./rules/search-efficiency.md) — Search efficiency, sufficiency stop & accessible communication
* [rules/hardware-safety.md](./rules/hardware-safety.md) — Hardware wiring & debugging guardrails
* [rules/generational.md](./rules/generational.md) — Generational isolation & model transparency
* [rules/system-baseline.md](./rules/system-baseline.md) — Operating system & software stack baseline
* [evals/evals.json](./evals/evals.json) — Automated regression test suite
