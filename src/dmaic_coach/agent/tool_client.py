"""Synchronous client for the statistics MCP server.

The agent calls the statistics tool over a real MCP stdio session — the same way
it would talk to any third-party MCP server. Each call is logged so the transcript
can show the tool-use chain.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
SERVER = os.path.join(_ROOT, "mcp_server", "stats_server.py")


def _parse(result):
    text = result.content[0].text
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return text


async def _call(tool: str, args: dict):
    env = {**os.environ, "PYTHONPATH": os.path.join(_ROOT, "src")}
    params = StdioServerParameters(command=sys.executable, args=[SERVER], env=env)
    # Silence the server's INFO logging so it doesn't interleave with the session.
    with open(os.devnull, "w") as devnull:
        async with stdio_client(params, errlog=devnull) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                res = await session.call_tool(tool, args)
                return _parse(res)


class StatsClient:
    """Thin synchronous wrapper. Records a log of (tool, args, result)."""

    server_path = SERVER

    def __init__(self):
        self.log: list[dict] = []

    def _run(self, tool, args):
        result = asyncio.run(_call(tool, args))
        self.log.append({"tool": tool, "args": args, "result": result})
        return result

    def capability(self, data, lsl=None, usl=None, target=None):
        return self._run("capability", {
            "data": [float(x) for x in data],
            "lsl": lsl, "usl": usl, "target": target,
        })

    def describe(self, data):
        return self._run("describe", {"data": [float(x) for x in data]})

    def dpmo(self, defects, units, opportunities=1):
        return self._run("dpmo", {
            "defects": float(defects), "units": float(units),
            "opportunities": float(opportunities),
        })
