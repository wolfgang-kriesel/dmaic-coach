"""Proves the statistics MCP server is independently usable over the protocol."""
import math

from dmaic_coach.agent.tool_client import StatsClient
from dmaic_coach.tools.stats import process_capability


def test_mcp_capability_matches_pure_function():
    data = [2, 4, 4, 4, 5, 5, 7, 9]
    client = StatsClient()
    via_mcp = client.capability(data, lsl=0, usl=10)
    direct = process_capability(data, lsl=0, usl=10)
    assert math.isclose(via_mcp["Ppk"], direct["Ppk"], abs_tol=1e-9)
    assert client.log[0]["tool"] == "capability"


def test_mcp_dpmo_roundtrip():
    client = StatsClient()
    r = client.dpmo(3.4, 1_000_000)
    assert math.isclose(r["sigma_level"], 6.0, abs_tol=0.05)
