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
        assert a is not None and a.readOnlyHint is True and a.idempotentHint is True, t.name
        assert a.openWorldHint is (t.name in server.LIVE_TOOLS), t.name
