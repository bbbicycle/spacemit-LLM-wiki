---
sidebar_position: 2
---

# Zenow

**Zenow** is a locally-run AI knowledge assistant desktop application. All data processing occurs on-device, ensuring complete privacy — no data ever leaves the machine. It supports multi-model management, intelligent conversations, knowledge base Q&A, and voice interaction.

## Key Features

- **Privacy-first**: All data is processed locally and never uploaded to the cloud.
- **Multi-model support**: Run LLM, Embedding, and Reranking models simultaneously.
- **Knowledge base Q&A**: Perform intelligent Q&A over your local documents.
- **Multi-turn conversations**: Maintain contextual memory across continuous dialogue sessions.

## Platform Support

| Platform & OS              | Acceleration Supported |
|----------------------------|------------------------|
| K1 Buildroot               | ❌ No        |
| K1 OpenHarmony             | ❌ No        |
| K1 Bianbu LXQT/GNOME       | ❌ No        |
| K3 Buildroot               | ❌ No        |
| K3 OpenHarmony             | ❌ No        |
| K3 Bianbu LXQT/GNOME       | ✅ Yes            |

## Architecture

### Core Technology Stack

Zenow is built on the following technologies:

- **[LLM SDK](https://www.spacemit.com/community/document/info?lang=en&nodepath=ai/application_tools/llmsdk.md)** — Large language model inference engine
  - Multi-turn dialogue
  - Knowledge base Q&A

- **Frontend**
  - Electron — Cross-platform desktop application framework
  - React + TypeScript — User interface
  - Vite — Build tooling

- **Backend**
  - FastAPI — High-performance API service
  - Python — Runtime environment
  - SQLite — Local data storage

### System Architecture Diagram

![System architecture diagram](../static/zenow_26.png)

### Data Flow

1. **Chat flow**: User input → Frontend → Backend session manager → LLM Server → Streaming response
2. **Knowledge base Q&A**: User query → Embed initial retrieval → Weighted fusion (Embed + BM25 + Rerank) → LLM generates answer

## Installation

Run the following commands in a terminal to install Zenow:

```bash
sudo apt update
sudo apt install zenow
```

## Quick Start

### 1. Launch the Application

Open the application menu from the bottom-left corner, search for **zenow**, and click to launch.

<img src="../static/zenow_1_en.jpg" alt="" width="300">

> 💡 **Tip**: Right-click the application icon and select **Add to Desktop**, then mark it as trusted for quick access in future sessions.

### 2. Download Models

On first launch, AI models must be downloaded before use:

1. Click the **Settings** icon in the left sidebar.
2. Locate the desired model in the model list.
3. Click the model name to begin downloading.

![](../static/zenow_2_en.jpg)

You can download multiple models simultaneously:

![](../static/zenow_3_en.jpg)

### 3. Start a Model

Once a model has downloaded, click its name again to start it. Model status is indicated by a colored indicator:

| Indicator | Status      |
|-----------|-------------|
| 🔴 Red    | Stopped |
| 🟡 Yellow | Starting |
| 🟢 Green  | Running      |

![](../static/zenow_4_en.jpg)

> ⚠️ **Important**: To use the full knowledge base feature, download and start at least one model of each type:
> - **LLM model** — Generates conversational responses
> - **Embed model** — Encodes text into vector representations
> - **Rerank model** — Re-scores and ranks retrieval results

## Features

### Intelligent Chat

#### Start a New Conversation

1. Click **Chat** in the left sidebar.
2. Confirm the LLM model status shows green.
3. Enter a question in the input dialog box 
4. Press Enter, or click the send button.

![](../static/zenow_13_en.jpg)

The application automatically creates a conversation session and supports multi-turn dialogue with persistent context memory.

![](../static/zenow_19_en.jpg)

### Knowledge Base Management

#### Pre-loaded Knowledge Base

A SpacemiT knowledge base is included by default and can be used to query topics covered within it, such as the K3's computing performance.

![Pre-loaded knowledge base](../static/zenow_27_en.png)

#### Create a Knowledge Base

1. Click **Knowledge Base** in the left sidebar.
2. Click the **Create Knowledge Base** button.
3. Enter a name and description for the knowledge base.
4. Optionally, select a custom avatar.

![Create knowledge base](../static/zenow_20_en.jpg)

#### Import Documents

1. Open a knowledge base.
   ![](../static/zenow_5_en.jpg)
2. Click the **Add Material** button.
   ![](../static/zenow_7_en.jpg)
3. Select the files or folder to upload (hold **Ctrl** to select multiple files).
   ![](../static/zenow_8_en.jpg)
4. Wait for document processing to complete.
   ![](../static/zenow_11_en.jpg)
5. If the page is navigated away from before vectorization finishes, a prompt will appear — click **Continue Vectorization** and wait for the process to complete.
   ![](../static/zenow_12_en.jpg)

#### Chat with a Knowledge Base

1. Start a new conversation or select an existing session.
2. In the input dialogue box, type **@** and select the target knowledge base.
   ![](../static/zenow_14_en.jpg)
3. Enter a question and press Enter. 
   ![](../static/zenow_15_en.jpg)
   The AI will respond based on the knowledge base content.
   ![](../static/zenow_16_en.jpg)

## Advanced Settings

### Parameters

![Chat parameters](../static/zenow_24_en.png)

The following LLM parameters can be configured on the Settings page:

**LLM Parameters**
- **Temperature**: Controls output randomness. Default: `0.7`. Range: `0.0–2.0`. Higher values produce more varied responses.
- **repeat Penalty**: Reduces repetitive output. Default: `1.1`.
- **Max Tokens**: Maximum number of tokens per response. Default: `2048`.

**Conversation System Prompt**
- Defines the AI's role, behavior, and response style.
- Applies to standard chat mode (when no knowledge base is selected).

### RAG Parameters

![RAG parameters](../static/zenow_25_en.png)

Knowledge base Q&A uses a two-stage retrieval and weighted fusion strategy. The following parameters can be configured:

**LLM Client Parameters (RAG mode)**
- **Temperature**: Default: `0` (deterministic output).
- **Repeat Penalty**: Default: `1.1`.
- **Max Tokens**: Default: `120`.

**Retrieval Parameters**

- **Top K** (final result count)
  - Number of document chunks returned to the LLM after weighted fusion.
  - Default: `5`. Range: `1–20`.
  - Affects context length and generation quality.

- **Initial K** (initial retrieval count)
  - Number of candidate documents retrieved in the first-stage Embed vector search.
  - Default: `10`. Range: `5–100`.
  - Higher values improve recall but increase computational cost.

- **Min Similarity** (minimum similarity threshold)
  - Similarity threshold below which results are filtered out.
  - Default: `-1` (no filtering). Range: `-1.0–1.0`.

**Fusion Weight Parameters**

- **Embed Weight** (embedding weight)
  - Weight of the Embed vector similarity score in the fusion formula.
  - Default: `0.4`. Range: `0.0–1.0`.
  - Controls the importance of semantic similarity.

- **BM25 Weight** (keyword weight)
  - Weight of the BM25 keyword matching score in the fusion formula.
  - Default: `0.2`. Range: `0.0–1.0`.
  - Controls the importance of exact keyword matching.

- **Rerank Weight** (reranking weight)
  - Weight of the Rerank model score in the fusion formula.
  - Default: `0.4`. Range: `0.0–1.0`.
  - Controls the importance of deep semantic understanding.

> 💡 **Weight note**: The three weights should sum to `1.0`. The system normalizes them automatically. Setting a weight to `0` disables the corresponding retriever.

**Toggle Parameters**

- **Enable BM25**: Enables BM25 keyword retrieval. Default: `true`.
- **Use Rerank**: Enables Rerank re-scoring. Default: `true`.

**Retrieval Pipeline**

1. **Stage 1 — Embed initial filtering**
   - Performs vector similarity search using the Embed model.
   - Retrieves `initial_k` candidate document chunks.

2. **Stage 2 — Weighted fusion**
   - **Embed score**: Semantic relevance based on cosine similarity.
   - **BM25 score**: Keyword matching using pre-processed tokenization results (if enabled).
   - **Rerank score**: Deep semantic understanding via the Rerank model (if enabled).
   - **Fusion formula**: `final_score = embed_weight × embed_score + bm25_weight × bm25_score + rerank_weight × rerank_score`

3. **Stage 3 — Final output**
   - Results are sorted by fusion score.
   - Results below `min_similarity` are filtered out.
   - The top `top_k` results are passed to the LLM.
   - Injected into the `{context}` placeholder in the RAG system prompt.

> 💡 **Performance tip**: BM25 uses pre-processed tokenization stored in the database, eliminating the need for real-time tokenization. Adjust weights and toggles to balance recall and precision.

**RAG System Prompt Template (`rag_system_prompt_template`)**
- Used in knowledge base Q&A mode.
- Must contain the `{context}` placeholder.
- Takes effect when a knowledge base is selected via `@`.
- `{context}` is replaced with the retrieved document content at query time.

## Troubleshooting

### Model download fails

- Check that the network connection is active.
- Verify that sufficient disk space is available.
- Try initiating the download again.

### Model fails to start (red indicator)

- Check that system memory is sufficient. The 30B model requires 32 GB of RAM or more.

### Knowledge base Q&A quality is poor

- Ensure that LLM, Embed, and Rerank models are all running.
- Tune the RAG parameters (e.g., `top_k`, `initial_k`, `embed_weight`, `bm25_weight`).
- Verify that the uploaded documents contain content relevant to the queries.

### How to improve response speed

- Use a smaller model (e.g., 2B instead of 30B).
- Reduce the context window size.