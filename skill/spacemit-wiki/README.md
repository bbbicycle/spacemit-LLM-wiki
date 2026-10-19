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

Follow the shared [installation guide](https://github.com/bbbicycle/spacemit-LLM-wiki/blob/main/INSTALL.md), or ask an AI assistant with local file and configuration access to follow it for you. The [installation manifest](https://github.com/bbbicycle/spacemit-LLM-wiki/blob/main/install/manifest.json) lists the exact files; download them from one resolved commit without cloning the repository.

| Mode | Install | Requirements |
| --- | --- | --- |
| **Cloud (default)** | Complete Skill + remote MCP connection at `https://mcp.yao1302.xyz/sse` | Client supports Skill and remote SSE; network access |
| **Local** | Complete Skill + `mcp/server.py` + `mcp/data/wiki_graph.json` | Client supports Skill and stdio; Python 3.9+ |

Copy the entire `spacemit-wiki/` directory into your assistant's recognized skill directory, preserving `SKILL.md`, `mcp.md`, `rules/` and `evals/`. Copying only `SKILL.md` leaves its relative references unresolved. Configure MCP using that client's supported format and merge existing settings. A remote MCP connection does not install the Skill automatically.

Neither mode needs Sources, Worker code, or index rebuilding. Local refined knowledge is bundled; original source reads may still use GitHub. Verify both Skill discovery and a real MCP query; report any reload or manual setup still needed.

Detailed tool reference: [mcp.md](./mcp.md).

---

## What's Included

* **Direct Intent Routing**: Choose boarding guides (`get_developer_journey`), topic archives (`read_knowledge_atom`) or hardware facts (`get_evidence_fact`) directly, without reading every layer.
* **Critical Engineering Guardrails**:
  * Checks chip generation, board revision and source before applying specifications.
  * Checks the installed OS, kernel, SDK and GPIO tool version before proposing commands.
  * Distinguishes Dense/MoE, total parameters, active parameters and measured performance conditions.
  * Hardware safety rules for JTAG pinout reversal, Strap resistor isolation, and unpowered peripheral domains.
* **Token-Efficient Context Reuse & Search Ceilings**:
  * Reuses evidence already present in conversation history, eliminating duplicate MCP round-trips.
  * Defaults to refined knowledge and bounded reads; missing, conflicting or stale evidence can trigger targeted upstream verification.
  * States conclusions, applicable conditions and sources, with analogies only where useful.

---

## How It Works

1. **Intent Routing**: Routes inquiries directly to the tool that provides the needed evidence.
2. **Sufficiency Stop**: Terminates further queries immediately once core claims and evidence are validated.
3. **Context Reuse**: Reuses loaded topic archives across follow-up questions to save tokens.
4. **Targeted Fallback**: Locates official source files (`search_raw_sources` ➔ `read_raw_source_file`) when refined evidence is missing, conflicting, stale or explicitly needs verification. Explicit line ranges of about 100–200 lines are recommended; the server does not enforce this as a hard budget.
5. **Evidence-Based Output**: Gives conclusions and conditions with citations, preserving review, withdrawal and expiry notices.

---

## References & Rules

* [SKILL.md](./SKILL.md) — Master instructions and tool selection matrix
* [mcp.md](./mcp.md) — MCP setup and tool schema reference
* [rules/search-efficiency.md](./rules/search-efficiency.md) — Search efficiency, sufficiency stop & accessible communication
* [rules/hardware-safety.md](./rules/hardware-safety.md) — Hardware wiring & debugging guardrails
* [rules/generational.md](./rules/generational.md) — Generational isolation & model transparency
* [rules/system-baseline.md](./rules/system-baseline.md) — Operating system & software stack baseline
* [evals/evals.json](./evals/evals.json) — Example evaluation checklist; not a passed regression report
