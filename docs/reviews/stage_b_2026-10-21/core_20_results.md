# 阶段 B：20 题工具与来源评测

通过 20/20；覆盖 6 个 domain；每端 42 次工具调用。

验证检索证据、固定来源、状态提示和双端一致性；参考答复是本轮 AI 的来源审核判据。未运行独立问答模型，不代表模型准确率，也未实物执行。stale/unknown 使用真实 Git 基线回放，不改变当前线上索引。

| 题号 | 问题 | domain | 调用/端 | 实际结果 |
| --- | --- | --- | ---: | --- |
| B01 | K1 与 K3 的 CPU/ISA 能否混用描述？ | chip_product_specs | 2 | 通过 |
| B02 | K3 的 60 TOPS 是否保证30B模型每秒15个token？ | chip_product_specs | 2 | 通过 |
| B03 | K3 跑30B-A3B是否等同于30B Dense，激活3B是否只占3B内存？ | chip_product_specs | 2 | 通过 |
| B04 | MUSE Pi Pro与Pi的排针/网口是否相同，是否属于K3板？ | chip_product_specs | 2 | 通过 |
| B05 | K1 QSPI_DATA3及启动介质选择能否直接照抄K3 GPIO表？ | hardware_schematic_design | 2 | 通过 |
| B06 | K3默认启动顺序及完整Strap管脚清单是什么？ | hardware_schematic_design | 2 | 通过 |
| B07 | K3 VDD0V8_DDR还能按旧版用磁珠独立供电吗？ | hardware_schematic_design | 2 | 通过 |
| B08 | 撤回K3热设计后，能否把0.23°C/W当θJC并保证PL1=15W？ | hardware_schematic_design | 2 | 通过 |
| B09 | MUSE Pi 的26Pin JTAG能否照Pi Pro的40Pin接？ | hardware_schematic_design | 2 | 通过 |
| B10 | Pi Pro 40Pin的I2C3时序能从管脚表直接确定吗？ | hardware_schematic_design | 2 | 通过 |
| B11 | K3 的USB3与PCIe能按全部独立接口同时使用吗？ | hardware_schematic_design | 2 | 通过 |
| B12 | 历史stale的K1调试节点能否直接给接线结论？ | toolchain_debug_tools | 2 | 通过 |
| B13 | Buildroot如何配置内核/U-Boot、选方案并区分K1/K3最终SD镜像名？ | bsp_kernel_drivers | 3 | 通过 |
| B14 | K3 SecureBoot烧eFuse后能否切回未签名镜像？ | bsp_kernel_drivers | 2 | 通过 |
| B15 | 没有直接来源的旧Muse Journey能否保证当前Bianbu包名可用？ | bianbu_os_distribution | 3 | 通过 |
| B16 | K1新Bianbu是否都能用sysfs GPIO；libgpiod版本矩阵是什么？ | bianbu_os_distribution | 2 | 通过 |
| B17 | XSlim当前量化CLI是什么，能把视觉ONNX路线套到所有LLM吗？ | edge_ai_robotics | 2 | 通过 |
| B18 | K3 Pico统一内存是否让30B MoE无内存上限？ | edge_ai_robotics | 2 | 通过 |
| B19 | K1/K3当前支持哪些ROS2版本，Lyrical已经正式支持了吗？ | edge_ai_robotics | 2 | 通过 |
| B20 | 安装ROS-Base就能保证传感器SLAM及Reachy运动控制全栈可用吗？ | edge_ai_robotics | 2 | 通过 |

逐题固定 SHA、行范围、适用版本、参考答复、实际匹配证据和 notice 见 [完整 JSON](core_20_results.json)。
