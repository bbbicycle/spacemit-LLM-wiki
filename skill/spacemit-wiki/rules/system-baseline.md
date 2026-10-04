# Operating System & Software Stack Baseline Rules

操作系统基线、内核版本规范与外设控制指令准则。严禁采用树莓派惯性思维误导嵌入式开发者。

---

## 1. GPIO 控制命令规范 (严禁树莓派专用工具)

SpacemiT 生态板卡采用标准开源 Linux 内核架构，非博通 (Broadcom) 树莓派专用平台。

**Incorrect:**
```bash
# 错误做法：给出树莓派特有的控制命令或已淘汰的旧库
raspi-gpio set 4 op dh
# 或者
gpio -g write 4 1  (wiringPi 命令)
# 结果：命令不存在（Command not found），或者引脚编号错乱导致硬件误操作。
```

**Correct:**
```bash
# 正确做法：使用现代 Linux 通用标准 libgpiod 工具包或 Sysfs 控制
# 1. 查询 GPIO 引脚状态 (需对照 MUSE Pi 26Pin IOMAP 确定 gpiochip 与 offset)
gpioget gpiochip2 12

# 2. 设置 GPIO 输出高电平
gpioset gpiochip2 12=1

# 3. 或通过标准 Sysfs 节点控制
echo 76 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio76/direction
echo 1 > /sys/class/gpio/gpio76/value
```

---

## 2. 自定义 Rootfs 编译必不可少的 `esos.elf` 固件

在构建基于 Debian、Ubuntu 或 Buildroot 的自定义系统镜像时。

**Incorrect:**
```text
# 错误做法：仅拷贝了基础 rootfs 与 Linux 内核模块，忽略了小核实时固件
/lib/modules/6.6.36/  (存在)
/lib/firmware/        (空目录，遗漏 esos.elf)
# 结果：内核引导到 RCPU 通信阶段超时挂死，HDMI 无法输出音频，系统无法完成登录。
```

**Correct:**
```text
# 正确做法：必须从 SDK 明确集成 RCPU 实时协处理器固件
/lib/firmware/esos.elf  (必须存在！由 board/spacemit/k1/target_overlay 提供)
# 作用：负责硬件协处理初始化与 HDMI Audio 中断转发。
```

---

## 3. 设备树 (DTB) 与板卡匹配规范

不同生态板卡（如 Muse Pi vs Muse Pi Pro）硬件外设不同，必须指定专属 DTB。

**Incorrect:**
```text
# 错误做法：在 Muse Pi Pro (高级版) 上直接使用标准版设备树
fdtfile=k1-x_muse_pi.dtb
# 结果：第二路千兆网口 (GMAC1) 缺失节点，板载 Mini PCIe 4G/5G 模组与 SIM 卡槽无法识别。
```

**Correct:**
```text
# 正确做法：根据具体板型精确匹配 DTB
Muse Pi (标准单网口版):  k1-x_muse_pi.dtb
Muse Pi Pro (双网口/4G版): k1-x_muse_pi_pro.dtb
K3 Pico-ITX (带万兆/EC):  k3_pico.dtb
```
