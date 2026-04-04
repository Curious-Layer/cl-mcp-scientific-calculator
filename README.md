# Scientific Calculator MCP Server

A Model Context Protocol (MCP) server that provides stateless scientific calculator operations.

## Authentication

This is a utility MCP server. No authentication input is required because tools do not access external tenant data.

## Features

- `health_check`: Verify server readiness.
- `evaluate_expression`: Safely evaluate scientific expressions with optional angle mode and precision controls.
- `list_supported_operations`: Return available operators, functions, constants, and angle modes.

## Setup

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
# stdio
python server.py

# sse
python server.py --transport sse --host 127.0.0.1 --port 8001

# streamable-http
python server.py --transport streamable-http --host 127.0.0.1 --port 8001
```

## Example Tool Calls

```json
{
  "tool": "evaluate_expression",
  "arguments": {
    "expression": "sin(pi / 2) + sqrt(16)",
    "angle_mode": "radians",
    "precision": 6
  }
}
```

```json
{
  "tool": "evaluate_expression",
  "arguments": {
    "expression": "sin(30)",
    "angle_mode": "degrees"
  }
}
```

## Project Structure

```text
cl-mcp-scientific-calculator/
|-- server.py
|-- requirements.txt
|-- README.md
`-- scientific_calculator_mcp/
    |-- __init__.py
    |-- cli.py
    |-- config.py
    `-- tools.py
```
