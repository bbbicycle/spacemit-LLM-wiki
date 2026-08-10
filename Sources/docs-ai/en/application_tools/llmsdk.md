---
sidebar_position: 2
---

# LLM SDK

> Note: This is a temporary version and will be consolidated into the AI SDK in a future release.

## Platform Support

| Platform & OS | Supported |
| --- | --- |
| K1 Buildroot | ❌ No |
| K1 OpenHarmony | ❌ No |
| K1 Bianbu LXQT/GNOME | ❌ No |
| K3 Buildroot | ❌ No |
| K3 OpenHarmony | ❌ No |
| K3 Bianbu LXQT/GNOME | ✅ Yes |

## Service Installation

```bash
sudo apt update
sudo apt install llm-sdk
```


**Base URL:** `http://localhost:8050`

---

## API Reference

- [System](#system)
- [Models - Model Management](#models---model-management)
- [Chat](#chat)
- [Sessions - Session Management](#sessions---session-management)
- [Knowledge Bases - Knowledge Base Management](#knowledge-bases---knowledge-base-management)
- [Assets - Static Assets](#assets---static-assets)

---

## System

### GET `/`
Root path. Returns basic API information.

**Response Example:**
```json
{"message": "llm-sdk LLM Chat API"}
```

---

### GET `/api/health`
Health check.

**Response Example:**
```json
{"status": "healthy", "app": "llm-sdk"}
```

---

## Models - Model Management

**Prefix:** `/api/models`

Supported `model_type` values: `llm` | `embed` | `rerank`

---

### GET `/api/models/list`
Returns the full model list for the specified type from the database.

**Query Parameters:**
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_type | string | `llm` | Model type |

**Response Example:**
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
Returns information about the currently running model.

**Query Parameters:**
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_type | string | `llm` | Model type |

**Response Example:**
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
Triggers model download asynchronously in the background and returns immediately.

**Request Body (JSON):**
```json
{"model_id": 1}
```

**Response Example:**
```json
{"success": true, "message": "Download started for Qwen2.5-7B-Q4"}
```

If the model has already been downloaded:
```json
{"success": true, "already_downloaded": true, "message": "Model already downloaded"}
```

---

### POST `/api/models/download/cancel`
Cancels an in-progress model download.

**Request Body (JSON):**
```json
{"model_id": 1}
```

**Response Example:**
```json
{"success": true, "message": "Download cancelled for Qwen2.5-7B-Q4"}
```

---

### GET `/api/models/download/status`
Returns the download status for the specified model.

**Query Parameters:**
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| model_id | int | No | Model ID |

**Response Example:**
```json
{
  "status": "downloading",
  "downloaded": 1048576,
  "total": 4294967296,
  "progress": 0.024,
  "error": null
}
```

Supported `status` values: `not_started` | `downloading` | `completed` | `error`

---

### GET `/api/models/download/status/all` (SSE)
SSE stream that pushes download status updates for all models.

**Query Parameters:**
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| model_type | string | No | Filter by model type |

**SSE Event Format:**
```
data: {"tasks": {"1": {"status": "downloading", "progress": 0.5}}, "timestamp": 12345.0}
```

---

### POST `/api/models/start`
Starts the `llama-server` instance for the specified model.

**Request Body (JSON):**
```json
{"model_id": 1}
```

**Response Example:**
```json
{"success": true, "message": "Server started"}
```

---

### POST `/api/models/start_all`
Starts the current model servers for all modes (`llm` / `embed` / `rerank`) in the background.

**Response Example:**
```json
{"success": true, "message": "Starting all model servers in background"}
```

---

### POST `/api/models/stop_all`
Stops model servers for all modes (`llm` / `embed` / `rerank`).

**Response Example:**
```json
{"success": true, "message": "All model servers stopped"}
```

---

### POST `/api/models/stop`
Stops the server for the specified model type.

**Request Body (JSON):**
```json
{"model_id": 1}
```

**Response Example:**
```json
{"success": true, "message": "Server stopped"}
```

---

### POST `/api/models/set_current`
Sets the specified model as the current model for its type. This operation updates only the database and does not start the server.

**Request Body (JSON):**
```json
{"model_id": 1}
```

**Response Example:**
```json
{"success": true, "message": "Set Qwen2.5-7B-Q4 as current llm model"}
```

---

### GET `/api/models/server_status`
Returns the current status of the server for the specified mode.

**Query Parameters:**
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_type | string | `llm` | Model type |

**Response Example:**
```json
{
  "status": "running",
  "model_id": 1,
  "model_name": "Qwen2.5-7B-Q4",
  "model_path": "/home/user/.cache/llm-sdk/models/llm/model.gguf",
  "error_message": null
}
```

Supported `status` values: `not_started` | `starting` | `running` | `error` | `stopped`

---

### GET `/api/models/server_status/stream` (SSE)
SSE stream that pushes server status updates. Update frequency is adjusted automatically by state: `0.5s` while starting, `3s` while running, and `2s` otherwise.

**Query Parameters:**
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_type | string | `llm` | Model type |

**SSE Event Format:**
```
data: {"status": "running", "model_id": 1, "model_name": "...", "model_path": "...", "error_message": null, "timestamp": 12345.0}
```

---

### GET `/api/models/all/stream` (SSE)
Unified SSE stream that pushes both server status and download progress for `llm`, `embed`, and `rerank` modes simultaneously.

**SSE Event Format:**
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
Returns model parameters for the specified type, including both server parameters and client parameters.

**Query Parameters:**
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_type | string | `llm` | Model type |

**Response Example (`llm`):**
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

Additional `embed` fields: `normalize`, `truncate`

---

### POST `/api/models/update_param` ⚠️ Deprecated
**This endpoint is deprecated and always returns `501 Not Implemented`.**

Parameters are now managed through the configuration file `~/.config/llm-sdk/config.yaml`. Changes take effect after the server is restarted.

---

### POST `/api/models/reset_param`
Resets model parameters for the specified type. If the server is running, it restarts automatically so the default values from the configuration file can take effect.

**Query Parameters:**
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_type | string | `llm` | Model type |

**Response:** Returns the current parameter set after reset, using the same format as `get_param`.

---

## Chat

**Prefix:** `/api`

---

### POST `/api/chat`
Sends a chat message and supports both streaming (SSE) and non-streaming responses.

Supported modes:
- **Standard chat**: `ConversationChain`, with historical context
- **RAG chat**: automatically switches to `RAGChain` (retrieval-augmented generation) when `kb_ids` is provided

**Request Body (JSON):**
```json
{
  "message": {
    "role": "user",
    "content": "Hello, please introduce yourself"
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

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| message | object | Yes | User message containing `role` and `content` |
| session_id | int | Yes | Session ID |
| stream | bool | No | Whether to return a streaming response; default is `true` |
| kb_ids | string[] | No | Knowledge base ID list; if provided, RAG mode is used |
| temperature | float | No | Overrides the default temperature |
| repeat_penalty | float | No | Overrides the default repeat penalty |
| max_tokens | int | No | Overrides the maximum number of generated tokens |
| rag_params | object | No | RAG-specific parameters, including `retrieval` settings and `rag_system_prompt_template` |
| conversation_system_prompt | string | No | Overrides the system prompt used in standard chat mode |

Example `rag_params` structure:
```json
{
  "retrieval": {
    "top_k": 5,
    "embed_k": 20,
    "bm25_k": 10
  },
  "rag_system_prompt_template": "Answer based on the following materials:\n\n{context}\n\n{question}"
}
```

**Streaming Response (SSE) Format:**
```
data: {"type": "chunk", "content": "Hello"}
data: {"type": "chunk", "content": "!"}
data: {"type": "done"}
```

Additional reference events may be included in RAG mode:
```
data: {"type": "references", "sources": [...]}
```

**Non-Streaming Response:**
```json
{"response": "Hello! I'm an AI assistant..."}
```

**Errors:** `404` session not found; `503` RAG feature unavailable

---

## Sessions - Session Management

**Prefix:** `/api/sessions`

---

### POST `/api/sessions`
Creates a new session. The session name is automatically generated from the first message (up to 50 characters).

**Request Body (JSON):**
```json
{"first_message": "Write me a poem"}
```

**Response Example:**
```json
{"session_id": 1, "session_name": "Write me a poem"}
```

---

### GET `/api/sessions`
Returns the session list, sorted by `updated_at` in descending order.

**Query Parameters:**
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| limit | int | 50 | Maximum number of results to return |
| offset | int | 0 | Pagination offset |

**Response Example:**
```json
{
  "sessions": [
    {
      "id": 1,
      "session_name": "Write me a poem",
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
Returns the details of the specified session.

**Response:** Same format as a single entry in the session list.

**Errors:** `404` session not found

---

### PUT `/api/sessions/{session_id}/name`
Updates the session name.

**Request Body (JSON):**
```json
{"new_name": "New session name"}
```

**Response Example:**
```json
{"success": true, "message": "Session name updated successfully"}
```

---

### DELETE `/api/sessions/{session_id}`
Deletes the specified session and all associated messages (cascade delete).

**Response Example:**
```json
{"success": true, "message": "Session deleted successfully"}
```

---

### GET `/api/sessions/{session_id}/messages`
Returns all messages in the specified session.

**Response Example:**
```json
{
  "messages": [
    {
      "id": 1,
      "session_id": 1,
      "role": "user",
      "content": "Write me a poem",
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
Clears all messages in the specified session while keeping the session itself.

**Response Example:**
```json
{"success": true, "message": "Messages cleared successfully"}
```

---

## Knowledge Bases - Knowledge Base Management

**Prefix:** `/api/knowledge-bases`

---

### GET `/api/knowledge-bases`
Returns a list of all knowledge bases.

**Response Example:**
```json
{
  "success": true,
  "knowledge_bases": [
    {
      "id": 1,
      "name": "Technical Docs",
      "description": "Technical reference documents",
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
Creates a new knowledge base. Supports an optional avatar image upload.

**Request Body (form-data):**
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | Yes | Knowledge base name |
| description | string | No | Description |
| avatar | file | No | Avatar image (PNG/JPEG/GIF/WEBP, max 5 MB) |

**Response Example:**
```json
{
  "success": true,
  "message": "Knowledge base 'Technical Docs' created successfully",
  "kb_id": 1,
  "knowledge_base": { "...": "..." }
}
```

**Errors:** `409` knowledge base name already exists

---

### GET `/api/knowledge-bases/{kb_id}`
Returns the details of the specified knowledge base.

**Response Example:**
```json
{"success": true, "knowledge_base": { "...": "..." }}
```

---

### PUT `/api/knowledge-bases/{kb_id}`
Updates knowledge base information (name, description, or avatar).

**Request Body (form-data):**
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | Yes | New name |
| description | string | No | New description |
| avatar | file | No | New avatar (PNG/JPEG/GIF/WEBP, max 5 MB) |

**Response Example:**
```json
{"success": true, "message": "Knowledge base updated successfully", "knowledge_base": { "...": "..." }}
```

---

### DELETE `/api/knowledge-bases/{kb_id}`
Deletes the specified knowledge base, including all associated files, vector data, and the avatar (cascade delete).

**Response Example:**
```json
{"success": true, "message": "Knowledge base 'Technical Docs' deleted successfully"}
```

---

### POST `/api/knowledge-bases/{kb_id}/files`
Uploads a single file to the knowledge base. The file is parsed and chunked synchronously before the response is returned. Vectorization is not triggered automatically.

**Request Body (form-data):**
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| file | file | Yes | Document file to upload |

Supported file types: PDF, DOCX, XLSX, PPTX, TXT, MD

**Response Example:**
```json
{
  "success": true,
  "file_id": 42,
  "kb_id": 1,
  "file_name": "document.pdf",
  "chunk_count": 15
}
```

**Errors:** `400` unsupported file type

---

### GET `/api/knowledge-bases/{kb_id}/files`
Returns a list of all files in the specified knowledge base.

**Response Example:**
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

File `status` values: `pending` | `processing` | `completed` | `failed`

File `vectorization_status` values: `not_vectorized` | `queued` | `vectorizing` | `completed` | `failed`

---

### GET `/api/knowledge-bases/{kb_id}/files/{file_id}`
Returns detailed information about the specified file.

**Response Example:**
```json
{"success": true, "file": { "id": 42, "filename": "document.pdf", "...": "..." }}
```

**Errors:** `404` file not found or does not belong to this knowledge base

---

### DELETE `/api/knowledge-bases/{kb_id}/files/{file_id}`
Deletes the specified file from the knowledge base, including its MinIO storage, vector data, and database record.

**Response Example:**
```json
{"success": true, "message": "File 'document.pdf' deleted successfully"}
```

---

### POST `/api/knowledge-bases/{kb_id}/files/{file_id}/cancel`
Cancels vectorization for the specified file. Only valid for files in `queued` or `vectorizing` state. For files currently being vectorized, any partially generated vectors are deleted and progress is reset to 0.

**Response Example:**
```json
{"success": true, "file_id": 42, "message": "Vectorization cancelled"}
```

**Errors:** `409` file is not in the vectorization queue

---

### GET `/api/knowledge-bases/{kb_id}/files/progress/stream` (SSE)
SSE stream that pushes real-time processing progress for all files in the knowledge base. Update interval is `0.5s` while vectorizing, and `2s` when idle.

**SSE Event Format:**
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

`vectorization_status` values: `not_vectorized` | `queued` | `vectorizing` | `completed` | `failed`

---

### GET `/api/knowledge-bases/{kb_id}/files/{file_id}/progress`
Returns the vectorization progress for the specified file.

**Response Example:**
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
Adds the specified file to the vectorization queue. This operation is idempotent.

**Response Example:**
```json
{"success": true, "message": "File added to vectorization queue", "file_id": 42}
```

**Errors:** `409` file has already been vectorized

---

### POST `/api/knowledge-bases/{kb_id}/files/vectorize_batch`
Adds multiple files to the vectorization queue in batch. Only files with `not_vectorized` or `failed` status are processed.

**Request Body (JSON):**
```json
{"file_ids": [42, 43, 44]}
```

**Response Example:**
```json
{
  "success": true,
  "queued_count": 3,
  "skipped_count": 0,
  "message": "3 files added to vectorization queue"
}
```

---

### POST `/api/knowledge-bases/{kb_id}/files/cancel_vectorize_batch`
Cancels vectorization for multiple files in batch. Only files with `queued` or `vectorizing` status are processed.

**Request Body (JSON):**
```json
{"file_ids": [42, 43]}
```

**Response Example:**
```json
{
  "success": true,
  "cancelled_count": 2,
  "skipped_count": 0,
  "message": "2 files cancelled from vectorization"
}
```

---

### GET `/api/knowledge-bases/{kb_id}/vectorization/queue`
Returns the current vectorization queue status for the knowledge base, listing files in `queued` or `vectorizing` state.

**Response Example:**
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
Returns all chunk records for the specified file from ChromaDB. Intended for debugging purposes.

**Response Example:**
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

## Assets - Static Assets

**Prefix:** `/api/assets`

---

### GET `/api/assets/minio/{file_path}`
Proxies and serves static files from MinIO storage (images, documents, audio, etc.).

**Path Parameters:**
| Parameter | Description |
| --- | --- |
| file_path | File path within MinIO, e.g. `kb_1/file_123.pdf` |

**Special Behavior:**
- PPTX/PPT files automatically attempt to serve a pre-generated PDF preview (`xxx_preview.pdf`). If the preview does not exist, the original file is returned as a fallback.

**Supported Content Types:**
- Images: PNG, JPEG, GIF, WEBP, SVG
- Documents: PDF, TXT, MD
- Office: PPTX/PPT, DOCX/DOC, XLSX/XLS
- Audio: MP3, WAV, OGG, M4A, FLAC, AAC

**Response:** File stream (`StreamingResponse`), cached for 1 day. Supports HTTP `Range` requests for partial content delivery (e.g., audio seeking).

**Errors:**
| Status | Description |
| --- | --- |
| 400 | Path contains `..` or starts with `/` (directory traversal protection) |
| 404 | File not found |
| 503 | MinIO client not initialized |
