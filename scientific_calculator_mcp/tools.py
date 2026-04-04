import ast
import json
import logging
import math
import operator
from typing import Any, Callable

from fastmcp import FastMCP
from pydantic import Field

from .config import (
    DEFAULT_ANGLE_MODE,
    DEFAULT_PRECISION,
    MAX_EXPRESSION_LENGTH,
    MAX_PRECISION,
    MIN_PRECISION,
    SUPPORTED_ANGLE_MODES,
)

logger = logging.getLogger("scientific-calculator-mcp-server")

_BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_ALLOWED_FUNCTIONS: dict[str, Callable[..., Any]] = {
    "abs": abs,
    "acos": math.acos,
    "asin": math.asin,
    "atan": math.atan,
    "ceil": math.ceil,
    "cos": math.cos,
    "degrees": math.degrees,
    "exp": math.exp,
    "factorial": math.factorial,
    "floor": math.floor,
    "log": math.log,
    "log10": math.log10,
    "radians": math.radians,
    "sin": math.sin,
    "sqrt": math.sqrt,
    "tan": math.tan,
}

_CONSTANTS: dict[str, float] = {
    "e": math.e,
    "pi": math.pi,
    "tau": math.tau,
}

_TRIG_INPUT_IN_DEGREES = {"sin", "cos", "tan"}
_TRIG_OUTPUT_IN_DEGREES = {"asin", "acos", "atan"}


def _normalize_angle_mode(angle_mode: str) -> str:
    normalized = angle_mode.lower().strip()
    if normalized not in SUPPORTED_ANGLE_MODES:
        supported = ", ".join(sorted(SUPPORTED_ANGLE_MODES))
        raise ValueError(f"Invalid angle_mode '{angle_mode}'. Use one of: {supported}")
    return normalized


def _to_numeric(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Expression can only contain numeric literals")
    return float(value)


def _call_function(name: str, args: list[float], angle_mode: str) -> float:
    func = _ALLOWED_FUNCTIONS[name]

    if name == "factorial":
        if len(args) != 1:
            raise ValueError("factorial requires exactly one argument")
        arg = args[0]
        if not float(arg).is_integer() or arg < 0:
            raise ValueError("factorial requires a non-negative integer")
        return float(func(int(arg)))

    call_args = args
    if name in _TRIG_INPUT_IN_DEGREES and angle_mode == "degrees":
        call_args = [math.radians(args[0]), *args[1:]]

    result = float(func(*call_args))

    if name in _TRIG_OUTPUT_IN_DEGREES and angle_mode == "degrees":
        return float(math.degrees(result))

    return result


def _evaluate_node(node: ast.AST, angle_mode: str) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate_node(node.body, angle_mode)

    if isinstance(node, ast.Constant):
        return _to_numeric(node.value)

    if isinstance(node, ast.Name):
        if node.id in _CONSTANTS:
            return _CONSTANTS[node.id]
        raise ValueError(f"Unknown name '{node.id}'")

    if isinstance(node, ast.BinOp):
        operator_type = type(node.op)
        if operator_type not in _BINARY_OPERATORS:
            raise ValueError("Unsupported operator in expression")
        left = _evaluate_node(node.left, angle_mode)
        right = _evaluate_node(node.right, angle_mode)
        return float(_BINARY_OPERATORS[operator_type](left, right))

    if isinstance(node, ast.UnaryOp):
        operator_type = type(node.op)
        if operator_type not in _UNARY_OPERATORS:
            raise ValueError("Unsupported unary operator in expression")
        operand = _evaluate_node(node.operand, angle_mode)
        return float(_UNARY_OPERATORS[operator_type](operand))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct function calls are supported")
        if node.keywords:
            raise ValueError("Keyword arguments are not supported")

        function_name = node.func.id
        if function_name not in _ALLOWED_FUNCTIONS:
            raise ValueError(f"Unsupported function '{function_name}'")

        args = [_evaluate_node(arg, angle_mode) for arg in node.args]
        return _call_function(function_name, args, angle_mode)

    raise ValueError("Expression contains unsupported syntax")


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="health_check",
        description="Check server readiness and basic connectivity.",
    )
    def health_check() -> str:
        return json.dumps({"status": "ok", "server": "CL Scientific Calculator MCP Server"})

    @mcp.tool(
        name="evaluate_expression",
        description="Evaluate a scientific calculator expression safely.",
    )
    def evaluate_expression(
        expression: str = Field(
            ..., description="Expression using math operators, constants, and functions"
        ),
        angle_mode: str = Field(
            DEFAULT_ANGLE_MODE,
            description="Angle interpretation for trig functions: radians or degrees",
        ),
        precision: int = Field(
            DEFAULT_PRECISION,
            description="Decimal precision for finite float results",
            ge=MIN_PRECISION,
            le=MAX_PRECISION,
        ),
    ) -> str:
        try:
            normalized_mode = _normalize_angle_mode(angle_mode)
            if len(expression) > MAX_EXPRESSION_LENGTH:
                raise ValueError(
                    f"Expression exceeds max length of {MAX_EXPRESSION_LENGTH} characters"
                )

            parsed = ast.parse(expression, mode="eval")
            result = _evaluate_node(parsed, normalized_mode)

            if math.isfinite(result):
                result = round(result, precision)

            return json.dumps(
                {
                    "expression": expression,
                    "angle_mode": normalized_mode,
                    "precision": precision,
                    "result": result,
                }
            )
        except Exception as e:
            logger.error(f"Failed evaluate_expression for '{expression}': {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool(
        name="list_supported_operations",
        description="List supported operators, functions, and constants.",
    )
    def list_supported_operations() -> str:
        return json.dumps(
            {
                "operators": ["+", "-", "*", "/", "//", "%", "**", "+x", "-x"],
                "functions": sorted(_ALLOWED_FUNCTIONS.keys()),
                "constants": sorted(_CONSTANTS.keys()),
                "angle_modes": sorted(SUPPORTED_ANGLE_MODES),
            }
        )
