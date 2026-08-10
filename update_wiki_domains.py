#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spacemit LLM Wiki - 全量 Markdown 元数据与 6 大领域 (Domain) 映射升级脚本
支持添加 domain, target_audience 以及工程师导读框。
"""

import os

DOMAINS_MAP = {
    # 模块 1: 芯片选型与产品物理规格 (chip_product_specs)
    "k1_thermal_specs.md": ("chip_product_specs", ["硬件工程师", "热设计工程师"], "存放 K1 芯片 TDP 功耗、工作结温及极简被动散热规格。"),
    "k3_thermal_specs.md": ("chip_product_specs", ["热设计工程师", "系统工程师"], "存放 K3 芯片热阻参数、极限结温与散热设计上限数据。"),
    "k1_material_avl_specs.md": ("chip_product_specs", ["硬件采购", "硬件电路工程师"], "存放经官方压测验证通过的 LPDDR4/4X 及闪存 AVL 器件选型表。"),
    "k1_k3_display_specs.md": ("chip_product_specs", ["显示驱动工程师", "硬件工程师"], "存放 K1/K3 HDMI/DSI 显示分辨率极限、硬解码能力与接口规格。"),
    "k1_k3_camera_specs.md": ("chip_product_specs", ["ISP图像工程师", "硬件工程师"], "存放 K1/K3 MIPI CSI RX 通道组合及 ISP 并发硬加速处理限制。"),
    "k1_k3_network_specs.md": ("chip_product_specs", ["网络驱动工程师", "硬件工程师"], "存放双路 GMAC 百兆 PHY 兼容限值、SDIO 无线模组电气参数。"),
    "k1_k3_pcie_usb_specs.md": ("chip_product_specs", ["高速接口工程师", "硬件工程师"], "存放 PCIe 2.1/3.0 通道拆分、USB OTG 复用及 SATA 免驱芯片规格。"),
    "muse_pi_vs_pi_pro_specs.md": ("chip_product_specs", ["系统选型工程师", "硬件工程师"], "存放 Muse Pi 与 Muse Pi Pro 板级物理尺寸、电源与外设参数对比。"),
    "k3_pico_specs.md": ("chip_product_specs", ["硬件工程师", "产品架构师"], "存放 K3 Pico-ITX 迷你主板处理器、存储、光口与外设物理规格。"),
    "k3_com260_specs.md": ("chip_product_specs", ["核心板选型工程师", "硬件工程师"], "存放 K3 CoM260 核心板与参考载板金手指引脚及物理规格。"),

    # 模块 2: 硬件电路设计与 PCB 避坑 (hardware_schematic_design)
    "k1_strap_pins_config.md": ("hardware_schematic_design", ["硬件电路工程师", "驱动工程师"], "详细标注 K1 芯片 Strap Pins 原理图上下拉阻值与 JTAG 路由复用要点。"),
    "k3_strap_pins_config.md": ("hardware_schematic_design", ["硬件电路工程师", "驱动工程师"], "详细标注 K3 芯片 Strap 管脚配置阻值与启动介质引脚选择。"),
    "p1_pmic_specs.md": ("hardware_schematic_design", ["电源工程师", "硬件电路工程师"], "存放 P1 PMIC 芯片各电轨输出电压电流限制、引脚封装及布局指导。"),
    "p1s_pmic_specs.md": ("hardware_schematic_design", ["电源工程师", "硬件电路工程师"], "存放 P1S PMIC 精简引脚定义、各电源轨参数及远端反馈走线。"),
    "K1启动模式与Strap管脚配置专题档案.md": ("hardware_schematic_design", ["硬件电路工程师", "嵌入式驱动"], "指导 K1 芯片上电采样阻值计算、JTAG/UART 物理复用与防挂死布局。"),
    "K3启动模式与Strap管脚配置专题档案.md": ("hardware_schematic_design", ["硬件电路工程师", "嵌入式驱动"], "指导 K3 芯片 Strap Pins 硬件上下拉设计与物理启动介质配置。"),
    "SpacemiT生态板卡与PMIC电源配合专题档案.md": ("hardware_schematic_design", ["电源电路工程师", "PCB Layout"], "详解 K1/P1 与 K3/P1S 动态反馈 DVFS 调压、SW/FB 布线与闹钟开机避坑。"),
    "K1_K3显示系统与多媒体输出专题档案.md": ("hardware_schematic_design", ["硬件电路工程师", "显示驱动"], "指导 HDMI/DSI 静电防护、电平转换电路以及背光控制走线避坑。"),
    "K1_K3摄像系统与图像处理专题档案.md": ("hardware_schematic_design", ["PCB Layout", "ISP 调试"], "指导 MIPI CSI 100Ω 差分走线等长、三摄/四摄 Lane 拆分与 DTS 通道绑定。"),
    "K1_K3网络通信与千兆网口专题档案.md": ("hardware_schematic_design", ["硬件电路工程师", "网口驱动"], "指导双 GMAC 千兆网口电路、百兆 PHY 兼容避坑与无线 SDIO 联调。"),
    "K1_K3高速外设接口专题档案.md": ("hardware_schematic_design", ["硬件电路工程师", "PCB Layout"], "指导 PCIe 拆分红线、USB OTG 切换与免驱 SATA 桥接芯片配置。"),
    "Muse_Pi_板级硬件设计专题.md": ("hardware_schematic_design", ["硬件电路工程师", "嵌入式工程师"], "详解 Muse Pi/Pro 12V PD 供电电路、Strap 拨码与 UART 调试复用设计。"),
    "K3_Pico_板级硬件设计专题.md": ("hardware_schematic_design", ["硬件电路工程师", "系统工程师"], "详解 K3 Pico 双电源输入优先级、M.2 动态带宽复用与 RT24 直出。"),
    "K3_COM260_板级硬件设计专题.md": ("hardware_schematic_design", ["硬件电路工程师", "核心板开发"], "详解 CoM260 核心板排针引脚复用、CSI 多路复用与 DSI 屏线热插拔避坑。"),

    # 模块 3: BSP、 Bootloader 与内核驱动 (bsp_kernel_drivers)
    "buildroot_bsp_specs.md": ("bsp_kernel_drivers", ["BSP 工程师", "系统构建工程师"], "存放 Buildroot SDK 软件栈组件、Repo 分支映射与 defconfig 矩阵。"),
    "buildroot_compilation_parameters.md": ("bsp_kernel_drivers", ["BSP 工程师", "CI/CD 工程师"], "存放 repo 源码同步、第三方 dl 包离线镜像与 Makefile 快捷构建命令。"),
    "esos_rcpu_firmware_specs.md": ("bsp_kernel_drivers", ["实时固件工程师", "BSP 驱动"], "记录 RCPU esos.elf 固件职责、HDMI Audio 转发与内核引导硬依赖红线。"),
    "Buildroot_嵌入式系统定制与内核编译专题档案.md": ("bsp_kernel_drivers", ["BSP 工程师", "驱动工程师"], "详解 SDK 目录架构、Docker/宿主机编译、linux-menuconfig 与 esos.elf 依赖。"),
    "K1系统启动与分区配置专题档案.md": ("bsp_kernel_drivers", ["BSP 工程师", "系统移植"], "详解 Ramfs 调试启动、自启脚本、U-Boot 与 OpenSBI 固件合并及隐藏分区。"),
    "K1驱动调试与设备控制专题档案.md": ("bsp_kernel_drivers", ["驱动工程师", "嵌入式软件"], "详解 PD 充电、DTS 启用 I2C、PWM 控制及 GPADC 电压采集调试方法。"),
    "K1_DDR_eMMC_AVL兼容性验证SOP专题档案.md": ("bsp_kernel_drivers", ["测试工程师", "系统稳定性"], "详解 LPDDR4x 与 eMMC 高低温环境压测、memtester/fio 指令及 SOP 判定。"),

    # 模块 4: Bianbu OS 系统与软件生态 (bianbu_os_distribution)
    "K1软件开发与系统集成FAQ专题档案.md": ("bianbu_os_distribution", ["系统集成工程师", "应用开发"], "汇总多媒体显示、无线网络栈部署、性能压测与 OTG 跨系统分区疑难解答。"),

    # 模块 5: 工具链、调试与编译支持 (toolchain_debug_tools)
    "k1_hardware_debug_parameters.md": ("toolchain_debug_tools", ["硬件调试工程师", "测试工程师"], "存放 K1 芯片线刷阻抗要求、休眠功耗、RTC 精度与调试串口/JTAG 规范。"),
    "K1硬件外设接口与物理调试专题档案.md": ("toolchain_debug_tools", ["硬件调试工程师", "嵌入式工程师"], "详解 K1 串口/JTAG 物理引脚定义、电平匹配与调试供电避坑原则。"),

    # 模块 6: 端侧 AI 推理与机器人应用 (edge_ai_robotics)
    "k1_ai_performance_data.md": ("edge_ai_robotics", ["AI 算法工程师", "嵌入式软件"], "存放 K1 通用 50KDMIPS、2.0 TOPS AI 算力、A100 AI Core 与 1B 大模型实测。"),
    "k3_ai_performance_data.md": ("edge_ai_robotics", ["AI 算法工程师", "系统架构师"], "存放 K3 芯片在 AI 算力与主流 8B/30B 大模型本地推理的实测数据。"),
    "ros2_platform_specs.md": ("edge_ai_robotics", ["机器人工程师", "ROS 2 开发者"], "存放 ROS 2 Humble/Jazzy 发行版、CycloneDDS 优化、micro-ROS 与节点开销。"),
    "robot_hardware_specs.md": ("edge_ai_robotics", ["具身智能工程师", "机器人工程师"], "存放 Reachy Mini、LeRobot SO101 机械臂、Linksee 移动车与 ACT/SmolVLA 参数。"),
    "K1大模型本地推理与AI算力专题档案.md": ("edge_ai_robotics", ["AI 算法工程师", "应用开发"], "详解 X60 算力矩阵、llama.cpp 编译标志 -DGGML_CPU_RISCV64_SPACEMIT=ON 与调频。"),
    "K3大模型本地推理与AI算力专题档案.md": ("edge_ai_robotics", ["AI 算法工程师", "系统优化"], "详解 K3 大模型本地运行吞吐、统一内存共享与多线程推理加速。"),
    "SpacemiT_ROS2_机器人与具身智能专题档案.md": ("edge_ai_robotics", ["机器人工程师", "具身 AI 开发者"], "详解 ROS 2 架构、micro-ROS 串口总线、LeRobot SO101 ACT 模仿学习与 SLAM 导航。"),
}

def update_file(path, fname):
    if fname not in DOMAINS_MAP:
        return
    domain, audience, hint = DOMAINS_MAP[fname]
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    if len(lines) < 2 or lines[0].strip() != "---":
        return

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
            
    if end_idx == -1:
        return

    fm_lines = lines[1:end_idx]
    body_lines = lines[end_idx+1:]
    
    # 检查 fm_lines 中是否已有 domain
    has_domain = any(l.startswith("domain:") for l in fm_lines)
    if not has_domain:
        # 插入 domain 和 target_audience
        fm_lines.append(f"domain: {domain}")
        audience_str = "[" + ", ".join(audience) + "]"
        fm_lines.append(f"target_audience: {audience_str}")

    # 检查 body 中是否包含导读框，若无则在 H1 标题下方插入
    body_text = "\n".join(body_lines)
    if "💡 工程师导读与排坑焦点" not in body_text:
        new_body = []
        h1_found = False
        for line in body_lines:
            new_body.append(line)
            if not h1_found and line.startswith("# "):
                h1_found = True
                new_body.append("")
                new_body.append("> [!TIP]")
                new_body.append(f"> **💡 工程师导读与排坑焦点**：{hint}")
                new_body.append(f"> **目标读者**：`{' / '.join(audience)}` | **技术领域**：`{domain}`")
        body_lines = new_body

    new_content = "---\n" + "\n".join(fm_lines) + "\n---\n" + "\n".join(body_lines) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated: {fname}")

def main():
    root = "/Users/bicycle/Spacemit LLM Wiki"
    for folder in ["Evidence", "Knowledge_Atoms"]:
        dir_path = os.path.join(root, folder)
        for fname in os.listdir(dir_path):
            if fname.endswith(".md"):
                full_path = os.path.join(dir_path, fname)
                update_file(full_path, fname)

if __name__ == "__main__":
    main()
