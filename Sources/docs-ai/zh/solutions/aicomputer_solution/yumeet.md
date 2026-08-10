sidebar_position: 3

# 与会（yumeet）

**yumeet** 是一个本地运行的 AI 会议助手桌面应用。音频处理、转写、翻译与总结均可在本地完成，用于提升会议记录效率并保护隐私数据。

它基于语音流水线（VAD / ASR / Diarization / Translation / TTS）与 LLM 总结能力，支持实时录音、离线音频导入、会议归档与检索。

## ✨ 核心能力

- **实时语音转录**：通过语音服务进行低延迟转写。
- **实时机器翻译**：支持在转录过程中输出翻译文本。
- **AI 会议总结**：基于 LLM 自动生成结构化会议总结。
- **会议记录管理**：支持历史记录筛选、搜索、重命名、删除。
- **本地文件管理**：支持保存音频源文件与导出文本总结。
- **跨形态运行**：支持浏览器形态与 Tauri 桌面形态。

## 平台支持情况

|      平台 & 系统       |       是否支持     |
|-----------------------|-----------------------|
| K1 Buildroot          | ❌ 不支持              |
| K1 OpenHarmony        | ❌ 不支持              |
| K1 Bianbu LXQT/GNOME    | ❌ 不支持            |
| K3 Buildroot          | ❌ 不支持              |
| K3 OpenHarmony       | ❌ 不支持              |
| K3 Bianbu LXQT/GNOME  | ✅ 支持                |

## 技术架构

### 应用技术栈

- **前端框架**：Vue 3.4+ / TypeScript 5.4 / Vite 5.4
- **桌面壳层**：Tauri 2（Rust）
- **音频处理**：Web Audio API、PCM 转换
- **Markdown 渲染**：markdown-it + DOMPurify（XSS 防护）
- **本地存储**：File System Access API
- **视觉能力**：Motion V、OGL

### 依赖服务

- **语音服务**：
  [Speech SDK](https://www.spacemit.com/community/document/info?lang=zh&nodepath=software/SDK/bianbu/ai/speechsdk.md)
- **大模型服务**：
  [LLM SDK](https://www.spacemit.com/community/document/info?lang=zh&nodepath=software/SDK/bianbu/ai/llmsdk.md)

### 系统架构图

![启动应用](../static/yumeet-framework.png)


### 工作流程

1. **实时转录流程**：开始转录 → 音频采集 → 语音服务处理 → 实时文本输出。
2. **会议总结流程**：结束会议 → 读取转录结果 → LLM 生成总结 → 自动保存。
3. **历史检索流程**：输入关键词 → 匹配标题/标签/内容 → 跳转记录详情。

## 🚀 安装

首次安装 `sm-sdk` 会自动下载模型包（约 2 GB）。

```bash
sudo apt update
sudo apt install yumeet llm-sdk sm-sdk
```

## 源码下载

在 Bianbu 环境中，可以直接通过 `apt` 获取 `yumeet` 的源码包。

### 1. 配置 `apt` 源

确认 `/etc/apt/sources.list.d/bianbu.sources` 中的 `Types` 同时包含 `deb` 和 `deb-src`：

```text
Types: deb deb-src
URIs: https://archive.spacemit.com/bianbu4/
Suites: resolute resolute-security resolute-updates resolute-backports resolute-porting resolute-customization
Components: main universe restricted multiverse
```

如果当前只有 `deb`，需要补充 `deb-src` 后再更新索引：

```bash
sudo apt update
```

### 2. 下载源码包

完成源配置后，可直接下载 `yumeet` 源码包：

```bash
mkdir -p ~/Workspace/yumeet-src
cd ~/Workspace/yumeet-src
apt source yumeet
```

执行完成后，当前目录下通常会生成 `.dsc`、原始压缩包以及解压后的源码目录，可用于查看 Debian 打包文件和源码内容。

## 快速开始

### 1) 启动应用

在系统菜单中搜索 **yumeet** 或 **与会** 并启动。

![启动应用](../static/yumeet.png)

### 2) 配置 AI 服务

首次使用建议确认以下服务配置：

1. **大模型服务**：默认 `Qwen3.5-2B`
2. **语言服务**：默认 `Qwen3-ASR-0.6B`
3. **翻译服务**：默认 `HY-MT1.5-1.8B`

![AI服务配置](../static/yumeet-1.png)

### 3) 配置存储路径

可配置两类目录：

1. **会议记录目录**：用于保存“下载总结”生成的 TXT / PDF / Markdown
2. **会议音频目录**：用于保存实时转录结束后的会议音频备份

![会议内容存储路径](../static/yumeet-2.png)

## 转录功能

### 1) 实时转录（麦克风）

#### 1.1 开始会议

可在两个入口启动实时转录：

1. 首页入口
2. 会议页入口

![实时转录入口-首页](../static/yumeet-3.png)
![实时转录入口-会议页](../static/yumeet-4.png)

#### 1.2 会议设定

开始转录后会弹出“会议设定”窗口。

- **必填项**：会议主题
- **标签与人员录入**：输入后需点击左侧 `+` 才会加入

字段说明：

- **会议主题**：作为会议记录标题显示
- **会议标签**：支持主标签/副标签，主标签会在记录卡片顶部突出展示
- **参会人员**：支持多参会人员登记

![会议设定](../static/yumeet-5.png)

完成后点击“开始录制”。

#### 1.3 转录过程

转录期间可查看：

- 当前转录/翻译输出
- 计时与暂停控制
- 显示内容切换

![转录过程](../static/yumeet-6.png)
![转录显示切换](../static/yumeet-7.png)

#### 1.4 生成会议总结

支持两种总结触发方式：

1. **录制中手动触发**“生成总结”

![录制中生成总结](../static/yumeet-8.png)

2. **结束录制后自动触发**总结流程

![结束录制并总结](../static/yumeet-9.png)

默认服务加载行为：

1. 点击“开始转录”或“导入音频”时，会加载语言服务和翻译服务
2. 点击“生成总结”或“暂停→结束”时，会加载大模型服务
3. 在“详细会议记录”页面点击“下载总结”时，也会调用大模型服务

![默认服务加载-1](../static/yumeet-10.png)
![默认服务加载-2](../static/yumeet-11.png)
![默认服务加载-3](../static/yumeet-12.png)

### 2) 导入音频（离线转录）

#### 2.1 开始导入

点击“导入音频”进入文件选择。

#### 2.2 选择文件

支持 `wav`、`mp3`、`m4a` 音频格式。

![导入音频文件](../static/yumeet-13.png)

#### 2.3 处理过程

导入成功后进入静态文件转录流程。

![导入处理中](../static/yumeet-14.png)

> 当前离线转录在整段处理完成前，不会持续显示中间转录文本。

#### 2.4 转录结果

处理结束后会自动执行会议总结。

![离线转录结果](../static/yumeet-15.png)

### 3) 转录内容搜索

可在当前会议内搜索关键词并高亮命中句段。

![转录内容搜索](../static/yumeet-16.png)

## 会议管理

### 1) 会议记录列表

记录列表支持以下能力：

1. 按时间范围筛选
2. 按会议标签筛选
3. 按标题/主标签搜索
4. 进入详细记录页
5. 记录重命名与删除
6. 分页浏览

![会议记录概览](../static/yumeet-17.png)
![会议标签筛选](../static/yumeet-18.png)
![会议记录搜索](../static/yumeet-19.png)
![会议记录操作](../static/yumeet-20.png)

### 2) 详细会议记录

详细页用于查看 LLM 对转录内容的总结结构。

![详细会议记录](../static/yumeet-21.png)

- 折叠项默认行为：
  - “转录原文”默认折叠
  - 其他摘要模块默认展开
- 页面顶部搜索框支持全文高亮检索

![详细记录折叠](../static/yumeet-22.png)
![详细记录搜索](../static/yumeet-23.png)

## 系统与设置

### 1) 存储策略

涉及两类文件：

1. 实时转录会议的原始音频
2. 详细会议记录导出的文本文件

![会议存储设置-1](../static/yumeet-24.png)
![会议存储设置-2](../static/yumeet-25.png)

说明：

- 删除会议记录仅删除文本记录，不删除原始音频
- 若关闭音频保留策略，实时会议结束后不保存音频源文件

### 2) 系统状态

可查看系统状态并手动刷新性能监控数据。

![系统状态-1](../static/yumeet-26.png)
![系统状态-2](../static/yumeet-27.png)

- **Debug 检查**：仅在开发模式开启后可用（可配合 `Ctrl+Shift+I`）
- **系统性能监控**：通过右上角刷新按钮更新显示

### 3) 其他设置

![其他设置](../static/yumeet-28.png)

- **UI 设置**：字体缩放、动态效果开关
- **AI 服务设置**：端口及服务地址调整（LLM-SDK / SM-SDK / 翻译服务）
- **许可证管理**：上传、折叠、查看许可证内容
- **设置页搜索**：按关键词过滤并显示匹配项
