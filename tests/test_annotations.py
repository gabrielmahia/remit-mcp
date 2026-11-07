"""Every tool is a pure reader and says so; tools that contact an outside service say that too. Clients use these hints to decide what is safe to auto-approve."""
import asyncio

from fastmcp import Client

from remit_mcp import server


def test_every_tool_declares_read_only_and_only_live_tools_are_open_world():
    async def tools():
        async with Client(server.mcp) as c:
            return await c.list_tools()
    ts = asyncio.run(tools())
    assert {t.name for t in ts} >= server.LIVE_TOOLS
    for t in ts:
        a = t.annotations
        assert a is not None and a.read_only_hint is True and a.idempotent_hint is True, t.name
        assert a.open_world_hint is (t.name in server.LIVE_TOOLS), t.name
