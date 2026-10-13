# 系统、固件与 GPIO 核实

涉及系统安装、设备树、GPIO、Rootfs 或引导故障时读取。

- 先确认板型、发行版、内核、SDK 和工具版本，再给命令。Bianbu、Buildroot 及第三方系统的镜像、分区、服务和驱动条件不可混用。
- GPIO 用实际内核支持的 Linux 接口。先核对 IOMAP、gpiochip/offset、引脚复用和 libgpiod 版本；不要把树莓派专用命令套用到 Spacemit 板卡。
- 命令示例应标注需要替换的值。未核实 gpiochip、offset 或 sysfs 编号时，不给看似可直接执行的固定引脚命令。
- 自定义 Rootfs 排查应检查平台要求的协处理器固件及安装路径，例如 K1 相关资料中的 `esos.elf`；缺失固件是待验证原因，不能凭“引导挂起”直接断定。
- DTB 必须与板型、硬件版本和当前 SDK 匹配；文件名以该版本的构建产物为准。
- 结合日志定位问题。精炼专题不足时可定向核实官方 SDK/原始文档，不必等待完整报错堆栈。

优先定位 Buildroot 系统定制专题、板卡上手动线、`esos_rcpu_firmware_specs` 和对应 IOMAP 文档。
