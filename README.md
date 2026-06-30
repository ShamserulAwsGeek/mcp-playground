<div align="center">

# MCP Lab — Weather MCP Server

**A hands-on reference implementation of the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) in Python.**

Real-time US weather data · Two transport modes · AI agent chat · Docker ready

[![Python](https://img.shields.io/badge/python-3.13%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-1.28%2B-purple)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![uv](https://img.shields.io/badge/managed%20with-uv-orange)](https://docs.astral.sh/uv/)
[![NOAA API](https://img.shields.io/badge/data-NOAA%20NWS%20API-0077B6)](https://www.weather.gov/documentation/services-web-api)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [stdio MCP Server](#1-stdio-mcp-server)
  - [SSE MCP Server](#2-sse-mcp-server-http)
  - [AI Agent Chat](#3-ai-agent-chat)
  - [Docker](#4-docker)
- [MCP Tools Reference](#mcp-tools-reference)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project is a **complete, runnable example** of an MCP server built with Python and [FastMCP](https://github.com/jlowin/fastmcp). It surfaces live US weather data from the [NOAA National Weather Service API](https://www.weather.gov/documentation/services-web-api) as callable MCP tools, allowing any MCP-compatible client — Claude Desktop, VS Code extensions, or a custom agent — to discover and invoke them.

Two implementations run side-by-side so you can compare approaches:

| Directory | Transport | Client side |
|-----------|-----------|-------------|
| `server/` | `stdio` | AI agent via `mcp_use` + Groq LLM |
| `mcp-server/` | `SSE` (HTTP) + `stdio` | Raw `ClientSession` |

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/<your-username>/mcp-lab.git
cd mcp-lab
uv sync

# 2. Add your Groq key
echo "GROQ_API_KEY=your_key_here" > .env

# 3. Run the AI agent chat
uv run server/client.py
```

```
You: Are there any weather alerts in Texas?
Assistant: Yes — there is currently a Heat Advisory in effect for...

You: What's the forecast for New York City?
Assistant: Here is the 5-period forecast for NYC (40.71, -74.00)...

You: clear    # clear conversation history
You: exit     # quit
```

> No weather API key required — NOAA NWS is a free, public API.

---

## Tech Stack

| Layer | Tool |
|-------|------|
| MCP framework | [FastMCP](https://github.com/jlowin/fastmcp) via `mcp[cli]` |
| AI agent orchestration | [`mcp_use`](https://github.com/mcp-use/mcp-use) |
| LLM | Qwen QwQ-32B via [Groq](https://console.groq.com/) (`langchain-groq`) |
| HTTP client | [`httpx`](https://www.python-httpx.org/) |
| Weather data | [NOAA National Weather Service REST API](https://www.weather.gov/documentation/services-web-api) |
| Dependency management | [uv](https://docs.astral.sh/uv/) |
| Containerisation | Docker |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        MCP Clients                           │
│                                                              │
│  ┌─────────────────────┐      ┌────────────────────────────┐ │
│  │   server/client.py  │      │  mcp-server/client-sse.py  │ │
│  │   ───────────────── │      │  mcp-server/client-stdio.py│ │
│  │   MCPAgent          │      │  ────────────────────────  │ │
│  │   Groq (Qwen) LLM   │      │  Raw MCP ClientSession     │ │
│  └──────────┬──────────┘      └────────────┬───────────────┘ │
└─────────────┼──────────────────────────────┼──────────────── ┘
              │ stdio (subprocess)           │ SSE (HTTP) / stdio
              ▼                              ▼
┌─────────────────────────┐   ┌──────────────────────────────┐
│  server/weather.py      │   │  mcp-server/server.py        │
│  ────────────────────── │   │  ──────────────────────────  │
│  FastMCP (stdio)        │   │  FastMCP (SSE, port 8000)    │
│  Tools: get_weather_    │   │  Tools: get_alerts           │
│         alerts          │   │         get_forecast         │
└──────────┬──────────────┘   └──────────────┬───────────────┘
           │                                 │
           └──────────────┬──────────────────┘
                          ▼
              ┌───────────────────────┐
              │     NOAA NWS REST API │
              │  api.weather.gov      │
              └───────────────────────┘
```

**Data flow (AI agent path):**

```
User prompt
    → MCPAgent (mcp_use)
        → Groq LLM decides which MCP tool to call
            → FastMCP server executes tool
                → NOAA NWS API (HTTP)
            ← Raw weather JSON
        ← Formatted tool result
    ← Natural-language response
User
```

---

## Features

- **Weather alerts** — fetch active NOAA alerts for any US state by two-letter code
- **Weather forecast** — get a multi-period forecast for any US lat/lon coordinate
- **Two transport modes** — `stdio` for subprocess embedding, `SSE` for HTTP-based remote access
- **AI agent chat loop** — interactive conversation; the LLM automatically decides when to call tools
- **Persistent conversation memory** — multi-turn context retained across the session
- **Docker support** — containerise the SSE server in one command
- **No weather API key** — uses the free public NOAA NWS API

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.13+ | Required by `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | latest | Recommended package manager |
| [Groq API key](https://console.groq.com/) | — | Free tier available; needed only for AI agent chat |
| Docker | any recent | Optional; only for containerised SSE server |

---

## Installation

### Using uv (recommended)

```bash
git clone https://github.com/<your-username>/mcp-lab.git
cd mcp-lab
uv sync
```

### Using pip

```bash
git clone https://github.com/<your-username>/mcp-lab.git
cd mcp-lab
pip install -r requirements.txt
```

---

## Configuration

Copy the example env file and fill in your Groq key:

```bash
cp .env.example .env   # or create .env manually
```

`.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> **Note:** The NOAA weather API is public and requires no credentials. `GROQ_API_KEY` is only needed for the AI agent chat (`server/client.py`).

---

## Usage

### 1. stdio MCP Server

`server/weather.py` communicates over standard I/O. It is designed to be spawned by an MCP host (e.g. Claude Desktop) or programmatically by the AI agent.

```bash
uv run server/weather.py
```

To register it with an MCP host, inspect the bundled config:

```bash
cat server/weather.json   # update the absolute path if needed
```

---

### 2. SSE MCP Server (HTTP)

`mcp-server/server.py` exposes the same tools over HTTP using Server-Sent Events on port **8000**.

```bash
# Terminal 1 — start the server
uv run mcp-server/server.py

# Terminal 2 — connect with the SSE client
uv run mcp-server/client-sse.py

# Or use the stdio client (spawns server as a subprocess)
uv run mcp-server/client-stdio.py
```

The server is available at `http://localhost:8000`.

---

### 3. AI Agent Chat

An interactive chat loop that understands plain-English weather queries. The Groq-hosted Qwen model automatically decides when to call the weather tools.

```bash
uv run server/client.py
```

**Example session:**

```
===== Interactive MCP Chat =====
Type 'exit' or 'quit' to end the conversation
Type 'clear' to clear conversation history
==================================

You: Are there any weather alerts in California?
Assistant: Yes, there is currently a Fire Weather Watch in effect for...

You: What is the forecast for Chicago?
Assistant: Here is the forecast for Chicago (41.88, -87.63)...

You: clear
Conversation history cleared.

You: exit
Ending conversation...
```

---

### 4. Docker

Build and run the SSE server as a container:

```bash
cd mcp-server

# Build the image
docker build -t mcp-weather-server .

# Run (SSE server accessible at http://localhost:8000)
docker run -p 8000:8000 mcp-weather-server
```

---

## MCP Tools Reference

Both server implementations expose the same logical tools under slightly different names.

---

### `get_weather_alerts` · `get_alerts`

Fetch active NOAA weather alerts for a US state.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `state` | `str` | Yes | Two-letter US state code — e.g. `CA`, `TX`, `NY` |

**Returns:** A formatted string listing each active alert with event type, affected area, severity, description, and instructions. Returns `"No active alerts for this state."` when none exist.

**Example:**

```python
get_alerts("TX")
# Event: Heat Advisory
# Area: South Central Texas
# Severity: Moderate
# ...
```

---

### `get_forecast`

Fetch the next five forecast periods for a US latitude/longitude coordinate.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `latitude` | `float` | Yes | Latitude of the target location |
| `longitude` | `float` | Yes | Longitude of the target location |

**Returns:** A formatted string with up to 5 forecast periods, each including period name, temperature, wind speed/direction, and a detailed forecast description.

> **Coverage:** NOAA NWS only covers **US locations**. Coordinates outside the US will return an error.

**Example:**

```python
get_forecast(40.71, -74.00)
# Tonight:
# Temperature: 68°F
# Wind: 10 mph S
# Forecast: Partly cloudy, with a low around 68...
```

---

## Project Structure

```
mcp-lab/
│
├── server/                     # stdio transport — AI agent demo
│   ├── weather.py              # FastMCP server (stdio)
│   ├── client.py               # AI agent chat (mcp_use + Groq LLM)
│   └── weather.json            # MCP host config (Claude Desktop, etc.)
│
├── mcp-server/                 # SSE/HTTP transport — raw client demo
│   ├── server.py               # FastMCP server (SSE, port 8000)
│   ├── client-sse.py           # Raw MCP client over SSE
│   ├── client-stdio.py         # Raw MCP client over stdio
│   └── Dockerfile              # Container image for the SSE server
│
├── main.py                     # Entry point placeholder
├── pyproject.toml              # Project metadata and dependencies (uv/pip)
├── requirements.txt            # pip-compatible dependency list
├── uv.lock                     # Locked dependency graph (uv)
├── .env.example                # Environment variable template
├── .gitignore
└── README.md
```

---

## Troubleshooting

**`GROQ_API_KEY` not found**

```
KeyError: 'GROQ_API_KEY'
```

Make sure a `.env` file exists in the project root with a valid key. The AI agent chat loads it automatically via `python-dotenv`.

---

**NOAA API returns no data for a location**

The NOAA NWS API only covers **US locations**. Coordinates outside the US (or offshore) will return an error from the `/points` endpoint. Verify your lat/lon is within the continental US, Alaska, or Hawaii.

---

**SSE client can't connect to `localhost:8000`**

Make sure `mcp-server/server.py` is running in a separate terminal before launching `client-sse.py`. Check the server logs for any port-binding errors.

---

**`uv sync` fails on Python version**

This project requires Python 3.13+. Check your active version:

```bash
python --version
uv python list
```

Install a compatible interpreter with `uv python install 3.13`.

---

**Docker build fails at `uv pip install`**

The Dockerfile uses Python 3.11-slim as its base image to keep the image lean; this is separate from the local dev requirement of 3.13+. If you see dependency resolution errors, confirm your `requirements.txt` is up to date:

```bash
uv pip compile pyproject.toml -o requirements.txt
```

---

## Contributing

Contributions, issues, and feature requests are welcome.

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/my-feature`
3. **Make your changes** — follow [PEP 8](https://peps.python.org/pep-0008/) style
4. **Test** your changes locally before opening a PR
5. **Commit**: `git commit -m "feat: add my feature"`
6. **Push**: `git push origin feature/my-feature`
7. **Open a Pull Request** with a clear description of what changed and why

Please open an issue first for large changes so the approach can be discussed before significant work is invested.

---

## License

This project is licensed under the [MIT License](LICENSE).
