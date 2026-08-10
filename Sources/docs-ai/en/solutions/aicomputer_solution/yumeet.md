---
sidebar_position: 3
---

# yumeet

**yumeet** is a locally run AI meeting assistant desktop application. All audio processing, transcription, translation, and summarization are performed on-device, enabling efficient meeting documentation while keeping sensitive data private.

The application is built on a full speech pipeline — VAD, ASR, speaker diarization, translation, and TTS — paired with LLM-based summarization. It supports real-time microphone recording, offline audio import, meeting archiving, and full-text search across records.

## Key Features

- **Real-Time Speech Transcription**: Low-latency, on-device transcription through the integrated speech service.
- **Real-Time Machine Translation**: Produces translated output alongside the transcription stream.
- **AI Meeting Summarization**: Automatically generates a structured meeting summary using an LLM.
- **Meeting Record Management**: Filter, search, rename, and delete past meeting records.
- **Local File Management**: Save raw audio and export text summaries to local storage.
- **Flexible Deployment Options**: Runs either as a browser-based web app or as a native Tauri desktop application.

## Platform Support

| Platform & OS              | Supported          |
|----------------------------|--------------------|
| K1 Buildroot               | ❌ No   |
| K1 OpenHarmony             | ❌ No   |
| K1 Bianbu LXQT/GNOME       | ❌ No   |
| K3 Buildroot               | ❌ No   |
| K3 OpenHarmony             | ❌ No   |
| K3 Bianbu LXQT/GNOME       | ✅ Yes       |

## Technical Architecture

### Application Stack

- **Frontend Framework**: Vue 3.4+ / TypeScript 5.4 / Vite 5.4
- **Desktop Shell**: Tauri 2 (Rust)
- **Audio Processing**: Web Audio API, PCM conversion
- **Markdown Rendering**: markdown-it + DOMPurify (XSS protection)
- **Local Storage**: File System Access API
- **Visual Effects**: Motion V, OGL

### Service Dependencies

- **Speech Service**:
  [Speech SDK](https://www.spacemit.com/community/document/info?lang=en&nodepath=ai/application_tools/speechsdk.md)
- **Large Language Model Service**:
  [LLM SDK](https://www.spacemit.com/community/document/info?lang=en&nodepath=ai/application_tools/llmsdk.md)

### System Architecture Diagram

![](../static/yumeet_en-1.png)

### Workflow Overview

1. **Real-Time Transcription**: Start transcription → Audio capture → Speech service processing → Live text output.
2. **Meeting Summarization**: End meeting → Read transcription → LLM generates summary → Auto-save.
3. **History Retrieval**: Enter keyword → Match title / tag / content → Navigate to record detail.

## Installation

On first installation, `sm-sdk` automatically downloads the required model package (approximately 2 GB).

```bash
sudo apt update
sudo apt install yumeet llm-sdk sm-sdk
```

## Source Code Download

On Bianbu, the `yumeet` source package can be retrieved directly via `apt`.

### 1. Configure the `apt` Source

Confirm that `/etc/apt/sources.list.d/bianbu.sources` includes both `deb` and `deb-src` under `Types`:

```text
Types: deb deb-src
URIs: https://archive.spacemit.com/bianbu4/
Suites: resolute resolute-security resolute-updates resolute-backports resolute-porting resolute-customization
Components: main universe restricted multiverse
```

If only `deb` is present, add `deb-src` and then update the package index:

```bash
sudo apt update
```

### 2. Download the Source Package

Once the source is configured, download the `yumeet` source package:

```bash
mkdir -p ~/Workspace/yumeet-src
cd ~/Workspace/yumeet-src
apt source yumeet
```

After this completes, the directory will contain a `.dsc` file, the original compressed archive, and the extracted source tree, which you can use to inspect the Debian packaging files and source code.

## Quick Start

### 1. Launch the Application

Open the system application menu, search for **yumeet**, and launch it.

![](../static/yumeet_en-2.png)

### 2. Configure AI Services

On first use, confirm that the following services are configured correctly:

- **LLM Service**: Default model `Qwen3.5-2B`
- **Speech Service**: Default model `Qwen3-ASR-0.6B`
- **Translation Service**: Default model `HY-MT1.5-1.8B`

![](../static/yumeet_en-3.png)

### 3. Configure Storage Paths

Two storage directories can be configured:

- **Meeting Records Directory**: Stores TXT, PDF, or Markdown files generated through **Download Summary**.
- **Meeting Audio Directory**: Stores backup audio files saved after a real-time transcription session ends.

![](../static/yumeet_en-4.png)

## Transcription Features

### 1. Real-Time Transcription (Microphone)

#### 1.1 Start a Meeting

Live transcription can be started from either of the following entry points:

- Home page entry
  ![](../static/yumeet_en-5.png)
- Meeting page entry
  ![](../static/yumeet_en-6.png)

#### 1.2 Meeting Setup

After transcription begins, the **Meeting Setup** dialog is displayed.

- **Required field**: Meeting topic
- **Tags and participant entries**: After entering a value, click the `+` icon on the left to add it

Field descriptions:

- **Meeting Topic**: Displayed as the title of the meeting record.
- **Meeting Tags**: Supports both primary and secondary tags; the primary tag is highlighted at the top of the record card.
- **Participants**: Supports registration of multiple attendees.

![](../static/yumeet_en-7.png)

Click **Start Recording** when done.

#### 1.3 Transcription in Progress

While recording, the interface displays:

- Live transcription and translation output
- A session timer with pause controls
- A display mode toggle to switch between views

![](../static/yumeet_en-8.png)
![](../static/yumeet_en-9.png)

#### 1.4 Generate a Meeting Summary

A summary can be generated in two ways:

1. **During recording** — Click **Start** in **Summary Session** at any time.
![](../static/yumeet_en-10.png)

2. **After recording ends** — Summarization starts automatically when you stop the session.
![](../static/yumeet_en-11.png)

The following images show which services are loaded at each trigger point:

- Clicking **Start Transcription** or **Import Audio** loads the speech and translation services.
  ![](../static/yumeet_en-12.png)
- Clicking **Start** in **Summary** or **Pause → End** loads the LLM service.
  ![](../static/yumeet_en-13.png)
- Clicking **Download Summary** in the **Meeting Minutes** section also invokes the LLM service.
  ![](../static/yumeet_en-14.png)

### 2. Import Audio (Offline Transcription)

#### 2.1 Start Import

Click **Import Audio** to open the file picker.

#### 2.2 Select a File

Supported audio formats include `wav`, `mp3`, and `m4a`.
![](../static/yumeet_en-15.png)

#### 2.3 Processing

After the file is imported, it enters the offline transcription pipeline.

![](../static/yumeet_en-16.png)

> Offline transcription processes the entire file before displaying any output. Intermediate results are not shown during processing.

#### 2.4 Transcription Result

When processing completes, a meeting summary is generated automatically.
![](../static/yumeet_en-17.png)

### 3. Search Within the Transcript

You can search for keywords within the current meeting session. Matching segments are highlighted.
![](../static/yumeet_en-18.png)

## Meeting Management

### 1. Meeting Record List

The record list provides the following tools for navigating your meeting history:

- Filter by date range
- Filter by meeting tag
- Search by title or primary tag
- Open a detailed record page
- Rename or delete a record
- Paginate through large record sets

![](../static/yumeet_en-19.png)
![](../static/yumeet_en-20.png)
![](../static/yumeet_en-21.png)

### 2. Detailed Meeting Record

The detail page displays the structured summary generated by the LLM from the meeting transcript.

![](../static/yumeet_en-22.png)

- Default collapse behavior:
  - **Original Transcript** is collapsed by default.
  - Other summary sections are expanded by default.
- The search box at the top of the page supports full-text search with highlighted matches.

![](../static/yumeet_en-23.png)
![](../static/yumeet_en-24.png)

## System and Settings

### 1. Storage Policy

yumeet manages two categories of local files:

- Original audio files from real-time transcription meetings
- Text files exported from detailed meeting records

![](../static/yumeet_en-25.png)

Notes:

- Deleting a meeting record removes only the text record. The original audio file is not affected.
- If audio retention is disabled, raw audio is discarded when a live session ends.

### 2. System Status

The **System Status** page shows current resource usage and lets you manually refresh the performance metrics.
![](../static/yumeet_en-26.png)

- **Debug Check**: Available only when developer mode is enabled. Use `Ctrl+Shift+I` to open DevTools alongside it.
- **Performance Monitoring**: Click the refresh button in the upper-right corner to update the displayed metrics.

### 3. Other Settings

![](../static/yumeet_en-27.png)

- **UI Design**: Adjust font scaling and toggle animations.
- **AI Service Connection**: Adjust ports and service addresses for LLM-SDK, SM-SDK, and the translation service.
- **License**: Upload, collapse, and view license content.
- **Settings Page Search**: Filter and display settings by keyword.
