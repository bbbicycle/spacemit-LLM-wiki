<!--
 * Copyright 2022-2023 SPACEMIT. All rights reserved.
 * Use of this source code is governed by a BSD-style license
 * that can be found in the LICENSE file.
 * 
 * @Author: David(qiang.fu@spacemit.com)
 * @Date: 2026-04-03 17:56:08
 * @LastEditTime: 2026-05-13 14:14:53
 * @FilePath: \doc\docs-ai\zh\application_tools\llmsdk.md
 * @Description: 
-->
---
sidebar_position: 2
---

# LLM SDK

> **注：** 临时版本，后续统一到AI SDK)

## 平台支持情况

|      平台 & 系统       |       是否支持     |
|-----------------------|-----------------------|
| K1 Buildroot          | ❌ 不支持               |
| K1 OpenHarmony     | ❌ 不支持              |
| K1 Bianbu LXQT/GNOME    | ❌ 不支持             |
| K3 Buildroot          | ❌ 不支持              |
| K3 OpenHarmony     | ❌ 不支持              |
| K3 Bianbu LXQT/GNOME  | ✅ 支持                |

## 安装服务

```bash
sudo apt update
sudo apt install llm-sdk
```


**Base URL:** `http://localhost:8050`

---

##  API目录

- [System](#system)
- [Models - 模型管理](#models---模型管理)
- [Chat - 聊天](#chat---聊天)
- [Sessions - 会话管理](#sessions---会话管理)
- [Knowledge Bases - 知识库管理](#knowledge-bases---知识库管理)
- [Assets - 静态资源](#assets---静态资源)

---

## System

### GET `/`
根路径，返回 API 基本信息。

**响应示例：**
```json
{"message": "llm-sdk LLM Chat API"}
```

---

### GET `/api/health`
健康检查。

**响应示例：**
```json
{"status": "healthy", "app": "llm-sdk"}
```

---

## Models - 模型管理

**前缀：** `/api/models`

模型类型（`model_type`）可选值：`llm` | `embed` | `rerank`

---

### GET `/api/models/list`
获取指定类型的所有模型列表（从数据库读取）。

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model_type | string | `llm` | 模型类型 |

**响应示例：**
```json
{
  "models": [
    {
      "id": 1,
      "name": "Qwen2.5-7B-Q4",
      "path": "/home/user/.cache/llm-sdk/models/llm/model.gguf",
      "download_url": "https://example.com/model.gguf",
      "is_downloaded": true,
      "is_current": true,
      "model_type": "llm"
    }
  ]
}
```

---

### GET `/api/models/current`
获取当前运行的模型信息。

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model_type | string | `llm` | 模型类型 |

**响应示例：**
```json
{
  "mode": "llm",
  "model_name": "Qwen2.5-7B-Q4",
  "model_path": "/home/user/.cache/llm-sdk/models/llm/model.gguf",
  "status": "running"
}
```

---

### POST `/api/models/download`
触发模型下载（后台异步，立即返回）。

**请求体（JSON）：**
```json
{"model_id": 1}
```

**响应示例：**
```json
{"success": true, "message": "Download started for Qwen2.5-7B-Q4"}
```

若已下载：
```json
{"success": true, "already_downloaded": true, "message": "Model already downloaded"}
```

---

### POST `/api/models/download/cancel`
取消正在进行的模型下载。

**请求体（JSON）：**
```json
{"model_id": 1}
```

**响应示例：**
```json
{"success": true, "message": "Download cancelled for Qwen2.5-7B-Q4"}
```

---

### GET `/api/models/download/status`
获取指定模型的下载状态。

**查询参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model_id | int | 否 | 模型 ID |

**响应示例：**
```json
{
  "status": "downloading",
  "downloaded": 1048576,
  "total": 4294967296,
  "progress": 0.024,
  "error": null
}
```

`status` 可选值：`not_started` | `downloading` | `completed` | `error`

---

### GET `/api/models/download/status/all` (SSE)
SSE 流式推送所有模型的下载状态。

**查询参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model_type | string | 否 | 筛选指定类型 |

**SSE 事件格式：**
```
data: {"tasks": {"1": {"status": "downloading", "progress": 0.5}}, "timestamp": 12345.0}
```

---

### POST `/api/models/start`
启动指定模型的 llama-server。

**请求体（JSON）：**
```json
{"model_id": 1}
```

**响应示例：**
```json
{"success": true, "message": "Server started"}
```

---

### POST `/api/models/start_all`
在后台启动所有模式（llm/embed/rerank）的当前模型服务器。

**响应示例：**
```json
{"success": true, "message": "Starting all model servers in background"}
```

---

### POST `/api/models/stop_all`
停止所有模式（llm/embed/rerank）的模型服务器。

**响应示例：**
```json
{"success": true, "message": "All model servers stopped"}
```

---

### POST `/api/models/stop`
停止指定模型对应类型的服务器。

**请求体（JSON）：**
```json
{"model_id": 1}
```

**响应示例：**
```json
{"success": true, "message": "Server stopped"}
```

---

### POST `/api/models/set_current`
将指定模型设为对应类型的当前模型（仅更新数据库，不启动服务器）。

**请求体（JSON）：**
```json
{"model_id": 1}
```

**响应示例：**
```json
{"success": true, "message": "Set Qwen2.5-7B-Q4 as current llm model"}
```

---

### GET `/api/models/server_status`
查询指定模式服务器的当前状态（单次）。

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model_type | string | `llm` | 模型类型 |

**响应示例：**
```json
{
  "status": "running",
  "model_id": 1,
  "model_name": "Qwen2.5-7B-Q4",
  "model_path": "/home/user/.cache/llm-sdk/models/llm/model.gguf",
  "error_message": null
}
```

`status` 可选值：`not_started` | `starting` | `running` | `error` | `stopped`

---

### GET `/api/models/server_status/stream` (SSE)
SSE 流式推送服务器状态，频率根据状态自动调整（启动中 0.5s，运行中 3s，其他 2s）。

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model_type | string | `llm` | 模型类型 |

**SSE 事件格式：**
```
data: {"status": "running", "model_id": 1, "model_name": "...", "model_path": "...", "error_message": null, "timestamp": 12345.0}
```

---

### GET `/api/models/all/stream` (SSE)
SSE 统一流：同时推送 llm、embed、rerank 三种模式的服务器状态和下载进度。

**SSE 事件格式：**
```json
{
  "modes": {
    "llm": {
      "server_status": {
        "status": "running",
        "model_id": 1,
        "model_name": "...",
        "model_path": "...",
        "error_message": null
      },
      "download_tasks": {}
    },
    "embed": { "...": "..." },
    "rerank": { "...": "..." }
  },
  "timestamp": 12345.0
}
```

---

### GET `/api/models/get_param`
获取指定类型的模型参数（服务器参数 + 客户端参数）。

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model_type | string | `llm` | 模型类型 |

**响应示例（llm）：**
```json
{
  "context_size": 4096,
  "threads": 4,
  "gpu_layers": 0,
  "batch_size": 512,
  "temperature": 0.7,
  "repeat_penalty": 1.1,
  "max_tokens": 2048
}
```

embed 额外字段：`normalize`, `truncate`

---

### POST `/api/models/update_param` ⚠️ 已废弃
**该接口已废弃，始终返回 `501 Not Implemented`。**

参数现在通过配置文件 `~/.config/llm-sdk/config.yaml` 管理，修改后重启服务器生效。

---

### POST `/api/models/reset_param`
重置指定类型的模型参数：若服务器正在运行则重启以应用配置文件中的默认值。

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model_type | string | `llm` | 模型类型 |

**响应：** 返回当前配置参数（同 `get_param` 格式）

---

## Chat - 聊天

**前缀：** `/api`

---

### POST `/api/chat`
发送聊天消息，支持流式（SSE）和非流式两种响应。

支持两种模式：
- **普通对话**：ConversationChain（带历史上下文）
- **RAG 对话**：提供 `kb_ids` 时自动切换为 RAGChain（检索增强生成）

**请求体（JSON）：**
```json
{
  "message": {
    "role": "user",
    "content": "你好，请介绍一下自己"
  },
  "session_id": 1,
  "stream": true,
  "kb_ids": null,
  "temperature": null,
  "repeat_penalty": null,
  "max_tokens": null,
  "model_type": "llm",
  "rag_params": null,
  "conversation_system_prompt": null
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | object | 是 | 用户消息，包含 role 和 content |
| session_id | int | 是 | 会话 ID |
| stream | bool | 否 | 是否流式响应，默认 `true` |
| kb_ids | string[] | 否 | 知识库 ID 列表，提供则使用 RAG |
| temperature | float | 否 | 覆盖默认温度参数 |
| repeat_penalty | float | 否 | 覆盖默认重复惩罚参数 |
| max_tokens | int | 否 | 覆盖最大生成 token 数 |
| rag_params | object | 否 | RAG 专用参数（`retrieval` 检索配置 + `rag_system_prompt_template` 提示词） |
| conversation_system_prompt | string | 否 | 覆盖普通对话模式的系统提示词 |

`rag_params` 结构示例：
```json
{
  "retrieval": {
    "top_k": 5,
    "embed_k": 20,
    "bm25_k": 10
  },
  "rag_system_prompt_template": "根据以下资料回答：\n\n{context}\n\n{question}"
}
```

**流式响应（SSE）格式：**
```
data: {"type": "chunk", "content": "你好"}
data: {"type": "chunk", "content": "！"}
data: {"type": "done"}
```

RAG 模式可能包含额外的引用事件：
```
data: {"type": "references", "sources": [...]}
```

**非流式响应：**
```json
{"response": "你好！我是一个AI助手..."}
```

**错误：** `404` 会话不存在；`503` RAG 功能不可用

---

## Sessions - 会话管理

**前缀：** `/api/sessions`

---

### POST `/api/sessions`
创建新会话，根据第一条消息自动生成会话名称（最多 50 字符）。

**请求体（JSON）：**
```json
{"first_message": "帮我写一首诗"}
```

**响应示例：**
```json
{"session_id": 1, "session_name": "帮我写一首诗"}
```

---

### GET `/api/sessions`
获取会话列表，按 `updated_at` 降序排列。

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 50 | 返回数量上限 |
| offset | int | 0 | 偏移量 |

**响应示例：**
```json
{
  "sessions": [
    {
      "id": 1,
      "session_name": "帮我写一首诗",
      "created_at": "2026-03-24T10:00:00",
      "updated_at": "2026-03-24T10:05:00",
      "message_count": 4,
      "total_tokens": 512
    }
  ],
  "total": 1
}
```

---

### GET `/api/sessions/{session_id}`
获取指定会话的详情。

**响应：** 同会话列表中单条数据格式。

**错误：** `404` 会话不存在

---

### PUT `/api/sessions/{session_id}/name`
更新会话名称。

**请求体（JSON）：**
```json
{"new_name": "新的会话名称"}
```

**响应示例：**
```json
{"success": true, "message": "Session name updated successfully"}
```

---

### DELETE `/api/sessions/{session_id}`
删除会话（级联删除所有消息）。

**响应示例：**
```json
{"success": true, "message": "Session deleted successfully"}
```

---

### GET `/api/sessions/{session_id}/messages`
获取会话的所有消息。

**响应示例：**
```json
{
  "messages": [
    {
      "id": 1,
      "session_id": 1,
      "role": "user",
      "content": "帮我写一首诗",
      "token_count": 8,
      "created_at": "2026-03-24T10:00:00",
      "metadata": null
    }
  ],
  "session_id": 1,
  "total_tokens": 8
}
```

---

### DELETE `/api/sessions/{session_id}/messages`
清空会话中的所有消息（保留会话本身）。

**响应示例：**
```json
{"success": true, "message": "Messages cleared successfully"}
```

---

## Knowledge Bases - 知识库管理

**前缀：** `/api/knowledge-bases`

---

### GET `/api/knowledge-bases`
获取所有知识库列表。

**响应示例：**
```json
{
  "success": true,
  "knowledge_bases": [
    {
      "id": 1,
      "name": "技术文档库",
      "description": "存放技术相关文档",
      "avatar_url": "/api/assets/minio/avatars/kb_1.png",
      "file_count": 3,
      "created_at": "2026-03-24T10:00:00"
    }
  ],
  "count": 1
}
```

---

### POST `/api/knowledge-bases`
创建新知识库，支持上传头像。

**请求体（form-data）：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 知识库名称 |
| description | string | 否 | 描述 |
| avatar | file | 否 | 头像图片（PNG/JPEG/GIF/WEBP，最大 5MB） |

**响应示例：**
```json
{
  "success": true,
  "message": "Knowledge base '技术文档库' created successfully",
  "kb_id": 1,
  "knowledge_base": { "...": "..." }
}
```

**错误：** `409` 知识库名称已存在

---

### GET `/api/knowledge-bases/{kb_id}`
获取指定知识库的详情。

**响应示例：**
```json
{"success": true, "knowledge_base": { "...": "..." }}
```

---

### PUT `/api/knowledge-bases/{kb_id}`
更新知识库信息（名称、描述、头像）。

**请求体（form-data）：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 新名称 |
| description | string | 否 | 新描述 |
| avatar | file | 否 | 新头像（PNG/JPEG/GIF/WEBP，最大 5MB） |

**响应示例：**
```json
{"success": true, "message": "Knowledge base updated successfully", "knowledge_base": { "...": "..." }}
```

---

### DELETE `/api/knowledge-bases/{kb_id}`
删除知识库（级联删除文件、向量数据、头像）。

**响应示例：**
```json
{"success": true, "message": "Knowledge base '技术文档库' deleted successfully"}
```

---

### POST `/api/knowledge-bases/{kb_id}/files`
上传单个文件到知识库（同步处理解析/分块，不自动向量化）。

**请求体（form-data）：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 要上传的文档文件 |

支持的文件类型：PDF、DOCX、XLSX、PPTX、TXT、MD

**响应示例：**
```json
{
  "success": true,
  "file_id": 42,
  "kb_id": 1,
  "file_name": "document.pdf",
  "chunk_count": 15
}
```

**错误：** `400` 不支持的文件类型

---

### GET `/api/knowledge-bases/{kb_id}/files`
获取知识库中的所有文件列表。

**响应示例：**
```json
{
  "success": true,
  "files": [
    {
      "id": 42,
      "filename": "document.pdf",
      "status": "completed",
      "vectorization_status": "completed",
      "chunk_count": 15,
      "vectorized_chunks": 15,
      "created_at": "2026-03-24T10:00:00"
    }
  ],
  "count": 1
}
```

文件 `status` 可选值：`pending` | `processing` | `completed` | `failed`

文件 `vectorization_status` 可选值：`not_vectorized` | `queued` | `vectorizing` | `completed` | `failed`

---

### GET `/api/knowledge-bases/{kb_id}/files/{file_id}`
获取指定文件的详细信息。

**响应示例：**
```json
{"success": true, "file": { "id": 42, "filename": "document.pdf", "...": "..." }}
```

**错误：** `404` 文件不存在或不属于该知识库

---

### DELETE `/api/knowledge-bases/{kb_id}/files/{file_id}`
从知识库中删除指定文件（同时删除 MinIO 存储、向量数据和数据库记录）。

**响应示例：**
```json
{"success": true, "message": "File 'document.pdf' deleted successfully"}
```

---

### POST `/api/knowledge-bases/{kb_id}/files/{file_id}/cancel`
取消向量化（仅对 `queued` 或 `vectorizing` 状态的文件有效）。正在向量化的文件会删除已生成的部分向量，进度重置为 0。

**响应示例：**
```json
{"success": true, "file_id": 42, "message": "向量化已取消"}
```

**错误：** `409` 文件不在队列中

---

### GET `/api/knowledge-bases/{kb_id}/files/progress/stream` (SSE)
SSE 流：实时推送知识库中所有文件的处理进度（向量化中 0.5s，空闲时 2s）。

**SSE 事件格式：**
```
event: progress
data: {
  "files": [
    {
      "file_id": 42,
      "file_name": "document.pdf",
      "upload_status": "done",
      "vectorization_status": "vectorizing",
      "total_chunks": 15,
      "vectorized_chunks": 8,
      "progress": 53.3
    }
  ],
  "timestamp": "2026-03-24T10:00:00"
}
```

`vectorization_status` 可选值：`not_vectorized` | `queued` | `vectorizing` | `completed` | `failed`

---

### GET `/api/knowledge-bases/{kb_id}/files/{file_id}/progress`
获取文件的向量化进度。

**响应示例：**
```json
{
  "success": true,
  "file_id": 42,
  "filename": "document.pdf",
  "status": "vectorizing",
  "processed_chunks": 8,
  "total_chunks": 15,
  "progress": 53.3,
  "error_message": null
}
```

---

### POST `/api/knowledge-bases/{kb_id}/files/{file_id}/vectorize`
将文件加入向量化队列（幂等操作）。

**响应示例：**
```json
{"success": true, "message": "文件已加入向量化队列", "file_id": 42}
```

**错误：** `409` 文件向量化已完成

---

### POST `/api/knowledge-bases/{kb_id}/files/vectorize_batch`
批量将文件加入向量化队列（仅处理 `not_vectorized` 或 `failed` 状态的文件）。

**请求体（JSON）：**
```json
{"file_ids": [42, 43, 44]}
```

**响应示例：**
```json
{
  "success": true,
  "queued_count": 3,
  "skipped_count": 0,
  "message": "3 个文件已加入向量化队列"
}
```

---

### POST `/api/knowledge-bases/{kb_id}/files/cancel_vectorize_batch`
批量取消向量化（仅处理 `queued` 或 `vectorizing` 状态的文件）。

**请求体（JSON）：**
```json
{"file_ids": [42, 43]}
```

**响应示例：**
```json
{
  "success": true,
  "cancelled_count": 2,
  "skipped_count": 0,
  "message": "2 个文件已取消向量化"
}
```

---

### GET `/api/knowledge-bases/{kb_id}/vectorization/queue`
获取知识库的向量化队列状态（`queued` 和 `vectorizing` 状态的文件）。

**响应示例：**
```json
{
  "success": true,
  "queue": [
    {
      "id": 42,
      "filename": "document.pdf",
      "vectorization_status": "vectorizing",
      "queue_position": 0
    }
  ],
  "queue_length": 1
}
```

---

### GET `/api/knowledge-bases/{kb_id}/files/{file_id}/chunks`
获取文件在 ChromaDB 中的所有 chunk 信息（调试用途）。

**响应示例：**
```json
{
  "kb_id": 1,
  "file_id": 42,
  "chunk_count": 15,
  "chunks": [
    {"document": "...", "metadata": {"source": "document.pdf", "chunk_index": 0}}
  ]
}
```

---

## Assets - 静态资源

**前缀：** `/api/assets`

---

### GET `/api/assets/minio/{file_path}`
从 MinIO 代理提供静态文件（图片、文档、音频等）。

**路径参数：**
| 参数 | 说明 |
|------|------|
| file_path | MinIO 中的文件路径，如 `kb_1/file_123.pdf` |

**特殊行为：**
- PPTX/PPT 文件会自动尝试提供对应的 PDF 预览版（`xxx_preview.pdf`），不存在时回退为原始文件

**支持的内容类型：**
- 图片：PNG、JPEG、GIF、WEBP、SVG
- 文档：PDF、TXT、MD
- Office：PPTX/PPT、DOCX/DOC、XLSX/XLS
- 音频：MP3、WAV、OGG、M4A、FLAC、AAC

**响应：** 文件流（`StreamingResponse`），缓存 1 天，支持 Range 请求（音频拖动进度条）

**错误：**
| 状态码 | 说明 |
|--------|------|
| 400 | 路径包含 `..` 或以 `/` 开头（目录穿越攻击防护） |
| 404 | 文件不存在 |
| 503 | MinIO 客户端未初始化 |
