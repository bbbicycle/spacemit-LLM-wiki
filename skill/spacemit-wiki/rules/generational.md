# Generational Isolation & Model Transparency Rules

SpacemiT 芯片代际参数严格隔离与端侧大模型真实算力边界披露准则。严禁产生代际混淆与脱离嵌入式硬件物理边界的过度承诺。

---

## 1. K1 vs K3 芯片代际绝对隔离

**Incorrect:**
```text
# 错误回答范例：使用泛称将 K3 的算力套在 SpacemiT 或 K1 身上
“进迭时空芯片集成了高达 60 TOPS 的 AI 算力，在 Muse Pi 开发板上可以流畅运行 30B 级别大模型。”
# 问题：Muse Pi 基于 K1 芯片（仅 2.0 TOPS / 最大 16GB LPDDR4x），根本不可能达到 60 TOPS 或运行 30B 模型！
```

**Correct:**
```text
# 正确回答范例：明确代际物理归属与规格边界
“进迭时空当前主要包含两代产品：
• K1 芯片（应用于 Muse Pi）：集成 8 核 X60 CPU，通用 AI 算力为 2.0 TOPS，最大支持 16GB LPDDR4x，适合部署 0.5B~1B 端侧小模型（如 Qwen2.5-0.5B，推理速度 > 10 Tokens/s）；
• K3 芯片（应用于 K3 Pico / CoM260）：集成 8 计算核 X100 + 8 智算核 A100，融合 AI 算力达 60 TOPS，采用双通道 64-bit LPDDR5 统一内存架构，支持 30B 级别的 MoE 大模型推理。”
```

---

## 2. 30B 大模型必须真实披露 MoE 架构

**Incorrect:**
```text
# 错误回答范例：隐瞒稀疏激活特性，宣称可流畅运行 30B Dense 全参数模型
“K3 芯片具备强大的端侧推理能力，支持流畅运行 300 亿 (30B) 全参数主流大模型，如 LLaMA-3-30B。”
# 问题：受 32GB 内存与 60 TOPS 算力上限限制，不可能在单芯片端侧流畅运行 30B 全参数稠密模型！
```

**Correct:**
```text
# 正确回答范例：明确标注 MoE (Mixture of Experts) 架构及单 Token 实际激活参数
“K3 芯片在端侧流畅运行的 30B 级别大模型，是指采用 MoE (Mixture of Experts) 稀疏架构的模型（如官方评测的 Qwen3-30B-A3B）：
• 参数总规模：总权重规模约为 30B；
• 实际激活参数：每个 Token 推理时仅激活约 3B (Active 3B) 核心参数；
• 实测性能：首词延迟约 0.9s，生成速度达 15 ~ 18 Tokens/s。
若需运行超大规模的 30B+ Dense 全参数模型，需通过 RV2768 集群服务器或端云协同方案部署。”
```
