# MCP Lab — Weather MCP Server

A hands-on learning project that implements a **Model Context Protocol (MCP)** server exposing real-time US weather data from the [NOAA National Weather Service API](https://www.weather.gov/documentation/services-web-api). Includes two transport modes (stdio and SSE), an AI agent chat interface powered by Groq, and Docker support.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Run the stdio MCP Server](#1-run-the-stdio-mcp-server)
  - [Run the SSE MCP Server](#2-run-the-sse-mcp-server)
  - [Run the AI Agent Chat](#3-run-the-ai-agent-chat)
  - [Run with Docker](#4-run-with-docker)
- [MCP Tools Reference](#mcp-tools-reference)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project demonstrates how to build and consume an MCP server in Python. It exposes US weather data as callable **MCP tools** that any MCP-compatible client (Claude Desktop, VS Code extensions, custom agents) can discover and invoke.

Two implementations are included side by side so you can compare approaches:

| Directory | Transport | Client |
|-----------|-----------|--------|
| `server/` | stdio | AI agent via `mcp_use` + Groq LLM |
| `mcp-server/` | SSE (HTTP) + stdio | Raw `ClientSession` |

---

## Features

- **Weather Alerts** — fetch active NOAA alerts for any US state by two-letter code
- **Weather Forecast** — get a multi-period forecast by latitude/longitude
- **Two transport modes** — `stdio` for subprocess embedding, `SSE` for HTTP-based remote access
- **AI agent chat loop** — interactive conversation powered by Qwen (via Groq) that uses the weather tools automatically
- **Docker support** — containerise the SSE server in one command
- **No weather API key required** — uses the free public NOAA NWS API

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    MCP Clients                      │
│                                                     │
│  ┌──────────────┐        ┌──────────────────────┐   │
│  │ client.py    │        │ client-sse.py /       │   │
│  │ (AI Agent)   │        │ client-stdio.py       │   │
│  │ Groq LLM +   │        │ (Raw MCP session)     │   │
│  │ mcp_use      │        └──────────┬───────────┘   │
│  └──────┬───────┘                   │               │
└─────────┼─────────────────────────┬─┘               
          │ stdio                   │ SSE / stdio     
          ▼                         ▼                 
┌──────────────────┐   ┌─────────────────────────┐   
│  server/         │   │  mcp-server/             │   
│  weather.py      │   │  server.py               │   
│  (FastMCP)       │   │  (FastMCP, port 8000)    │   
└────────┬─────────┘   └──────────┬──────────────┘   
         │                        │                   
         └────────────┬───────────┘                   
                      ▼                               
            ┌──────────────────┐                      
            │  NOAA NWS API    │                      
            │  api.weather.gov │                      
            └──────────────────┘                      
```

---

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) **or** pip
- A free [Groq API key](https://console.groq.com/) — only needed for the AI agent chat (`server/client.py`)
- Docker (optional, for the containerised SSE server)

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

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> The NOAA weather API is public and requires no key. Only the AI agent chat (`server/client.py`) needs `GROQ_API_KEY`.

---

## Usage

### 1. Run the stdio MCP Server

The `server/weather.py` server communicates over standard I/O. It is designed to be launched by an MCP client (e.g. Claude Desktop) or the AI agent.

```bash
uv run server/weather.py
```

To wire it into an MCP host, point the host at the config file:

```bash
# weather.json already contains the correct command path — update the absolute path if needed
cat server/weather.json
```

### 2. Run the SSE MCP Server

The `mcp-server/server.py` server exposes the same tools over HTTP using Server-Sent Events on port **8000**.

```bash
# Terminal 1 — start the server
uv run mcp-server/server.py

# Terminal 2 — connect with the SSE client
uv run mcp-server/client-sse.py

# Or connect with the stdio client (launches server as subprocess)
uv run mcp-server/client-stdio.py
```

### 3. Run the AI Agent Chat

An interactive chat loop that lets you ask weather questions in plain English. The Groq-hosted Qwen model decides when to call the weather tools automatically.

```bash
uv run server/client.py
```

Example session:

```
You: Are there any weather alerts in Texas right now?
Assistant: Yes, there is currently a Heat Advisory in effect for...

You: What is the forecast for New York City?
Assistant: Here is the forecast for New York City (40.71, -74.00)...

You: clear    # clears conversation history
You: exit     # exits the chat
```

### 4. Run with Docker

```bash
cd mcp-server

# Build the image
docker build -t mcp-weather-server .

# Run the SSE server (accessible at http://localhost:8000)
docker run -p 8000:8000 mcp-weather-server
```

---

## MCP Tools Reference

### `get_weather_alerts(state: str) -> str`

Returns active NOAA weather alerts for a US state.

| Parameter | Type | Description |
|-----------|------|-------------|
| `state` | `str` | Two-letter US state code (e.g. `CA`, `TX`, `NY`) |

### `get_alerts(state: str) -> str`

Identical to `get_weather_alerts` — available in the `mcp-server/` version.

### `get_forecast(latitude: float, longitude: float) -> str`

Returns the next 5 forecast periods for a given location.

| Parameter | Type | Description |
|-----------|------|-------------|
| `latitude` | `float` | Latitude of the location |
| `longitude` | `float` | Longitude of the location |

> Note: The NOAA NWS API only covers **US locations**. Coordinates outside the US will return an error.

---

## Project Structure

```
mcp-lab/
├── server/                  # stdio-based MCP server + AI agent client
│   ├── weather.py           # FastMCP server (stdio transport)
│   ├── client.py            # AI agent chat using mcp_use + Groq
│   └── weather.json         # MCP host config (for Claude Desktop etc.)
│
├── mcp-server/              # SSE-based MCP server + raw clients
│   ├── server.py            # FastMCP server (SSE + stdio transport)
│   ├── client-sse.py        # Raw MCP client over SSE
│   ├── client-stdio.py      # Raw MCP client over stdio
│   └── Dockerfile           # Container image for the SSE server
│
├── main.py                  # Project entry point (placeholder)
├── pyproject.toml           # Project metadata and dependencies
├── requirements.txt         # pip-compatible dependency list
├── uv.lock                  # Locked dependency versions (uv)
└── README.md
```

---

## Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

Please follow [PEP 8](https://peps.python.org/pep-0008/) style and include a short description of what your change does and why.

---

## License

This project is licensed under the [MIT License](LICENSE).
