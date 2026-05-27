"""MCP server exposing the Measure-phase statistics tool.

Run standalone for inspection:
    PYTHONPATH=src python3 mcp_server/stats_server.py
The agent connects to this server over stdio and calls these tools to verify the
learner's analysis. Keeping statistics behind MCP means tool-use happens over the
real protocol, exactly as it would against any third-party MCP server.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from dmaic_coach.tools.stats import (  # noqa: E402
    descriptive_stats,
    process_capability,
    dpmo_sigma,
)

mcp = FastMCP("dmaic-stats")


@mcp.tool()
def capability(data: list[float], lsl: float | None = None,
               usl: float | None = None, target: float | None = None) -> dict:
    """Compute process capability (Pp/Ppk) and expected ppm out of spec."""
    return process_capability(data, lsl=lsl, usl=usl, target=target)


@mcp.tool()
def describe(data: list[float]) -> dict:
    """Descriptive statistics (n, mean, std, min, max, median)."""
    return descriptive_stats(data)


@mcp.tool()
def dpmo(defects: float, units: float, opportunities: float = 1) -> dict:
    """DPMO and process sigma level (1.5 sigma shift convention)."""
    return dpmo_sigma(defects, units, opportunities)


if __name__ == "__main__":
    mcp.run()
