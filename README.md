# Scientific Calculator MCP Server

A Model Context Protocol (MCP) server that provides stateless scientific calculator operations.

## Authentication

This is a utility MCP server. No authentication input is required because tools do not access external tenant data.

## Features

- `health_check`: Verify server readiness.
- `evaluate_expression`: Safely evaluate scientific expressions with optional angle mode and precision controls.
- `list_supported_operations`: Return available operators, functions, constants, and angle modes.

## Available Tools

### `health_check`

Checks server readiness and basic connectivity.

Arguments:
- None.

Example call:

```json
{
  "tool": "health_check",
  "arguments": {}
}
```

### `evaluate_expression`

Evaluates a scientific expression safely using an allowlisted AST evaluator.

Arguments:
- `expression` (required, string): Scientific expression to evaluate.
  - Supports operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`, unary `+x`, unary `-x`.
  - Supports constants: `pi`, `e`, `tau`.
  - Supports functions: `abs`, `acos`, `asin`, `atan`, `ceil`, `cos`, `degrees`, `exp`, `factorial`, `floor`, `log`, `log10`, `radians`, `sin`, `sqrt`, `tan`.
  - Maximum length: 512 characters.
- `angle_mode` (optional, string): Trigonometric angle mode.
  - Allowed values: `radians`, `degrees`.
  - Default: `radians`.
- `precision` (optional, integer): Decimal precision for finite float results.
  - Allowed range: 0 to 15.
  - Default: 10.

Example call:

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

### `list_supported_operations`

Returns the server's current supported operators, functions, constants, and angle modes.

Arguments:
- None.

Example call:

```json
{
  "tool": "list_supported_operations",
  "arguments": {}
}
```

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
