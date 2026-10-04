---
type: evidence
title: "K3 关键器件经认证厂商列表 (AVL) 规格"
status: needs_review
created: 2026-10-04
updated: 2026-10-04
aliases: [K3关键器件AVL, K3物料清单, k3_material_avl_specs]
domain: chip_product_specs
target_audience: [硬件采购, 硬件电路工程师, 系统架构师]
---

# K3 关键器件经认证厂商列表 (AVL) 规格

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放经进迭时空官方压测验证通过的 K3 芯片 LPDDR5、UFS 闪存及 eMMC 存储元器件选型表。
> **目标读者**：`硬件采购 / 硬件电路工程师 / 系统架构师` | **技术领域**：`chip_product_specs`

**AVL (Approved Vendor List)** 包含了进迭时空官方经验证、可量产的 K3 平台兼容器件，用以辅助客户进行高速存储与内存芯片选型，规避信号完整性与高速读写稳定性隐患，并保障供应链可交付性。

## 1. 涵盖的核心高速存储器件类别
*   **高速内存颗粒**：LPDDR5（支持高达 5500 Mbps / 6400 Mbps 高速通道，要求严格遵循眼图与 PCB 阻抗规范）
*   **高速闪存介质**：UFS（通用闪存存储，提供高吞吐系统盘支持）
*   **标准嵌入式存储**：eMMC 5.1（支持工业级与车规级选型）

## 2. 官方 AVL 下载通道
官方定期维护并发布最新验证的 xlsm 格式 AVL 表格：

*   **官方发布资源**：[K3 关键器件 AVL 表格下载](https://cdn-resource.spacemit.com/file/chip/K3/K3_Key_Parts_AVL.xlsm)
*   **硬件验证建议**：在进行 K3 核心板或主板 Layout 前，建议对比最新 AVL 清单中的已验证封装引脚与推荐阻抗匹配网络，若选型不在 AVL 列表内，需提前进行信号质量压测与高低温环境温箱筛选。
