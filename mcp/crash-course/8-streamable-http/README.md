# Part 8: Streamable HTTP

As of **March 24, 2025**, the Model Context Protocol has introduced an improvement to its transport layer. The original **HTTP+SSE (Server-Sent Events)** transport has been deprecated in favor of the new **Streamable HTTP** transport. You can find the official [documentation here](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http).

## What's New?

**Streamable HTTP** offers:
- **Better performance** under high load
- **Stateless server support** for easier scaling
- **Single endpoint** instead of separate `/sse` and `/messages` endpoints
- **Improved infrastructure compatibility**

## Server Configuration Options

### 1. Stateful Server (Default)
```python
from mcp.server.fastmcp import FastMCP

# Maintains session state between requests
mcp = FastMCP("StatefulServer")
mcp.run(transport="streamable-http")
```

**Use when**: You need to remember user context, maintain conversation state, or track ongoing operations.

### 2. Stateless Server
```python
# No session persistence - each request is independent
mcp = FastMCP("StatelessServer", stateless_http=True)
mcp.run(transport="streamable-http")
```

**Use when**: Building scalable APIs, microservices, or when you want to deploy across multiple servers without shared state.

### 3. Stateless + JSON-Only Server
```python
# Stateless + always returns JSON (no SSE streaming)
mcp = FastMCP("StatelessServer", stateless_http=True, json_response=True)
mcp.run(transport="streamable-http")
```

**Use when**: Building REST-like APIs, working with clients that don't support SSE, or when you want simple HTTP JSON responses.

## What Do These Options Mean?

### Stateless vs Stateful
- **Stateful**: Server remembers previous interactions, can maintain conversation context
- **Stateless**: Each request is independent, better for scaling and load balancing

### JSON Response Option
- **With SSE** (default): Can stream responses for long-running operations
- **JSON-only**: Always returns immediate JSON responses, simpler for basic tools

## Quick Migration from SSE

**Before (SSE - used in this course):**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator", host="0.0.0.0", port=8050)
mcp.run(transport="sse")
```

**After (Streamable HTTP):**
```python
from mcp.server.fastmcp import FastMCP

# For most new projects (stateless is recommended)
mcp = FastMCP("Calculator", stateless_http=True)
mcp.run(transport="streamable-http")
```

## When to Use Each

| Option | Best For | Example Use Cases |
|--------|----------|-------------------|
| **Stateful** | Interactive applications | Chatbots, multi-step workflows |
| **Stateless** | Production APIs | Tool servers, microservices |
| **Stateless + JSON** | Simple REST APIs | Basic tool calls, webhooks |

## Learn More

For complete documentation, examples, and advanced usage:

[Official Streamable HTTP Documentation](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http)