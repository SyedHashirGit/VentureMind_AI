from app.services.memory_service import _extract_text
from app.services.breeth_client import BreethClient


def test_extract_text_joins_text_blocks():
    res = {"content": [{"type": "text", "text": "a"}, {"type": "image"}, {"type": "text", "text": "b"}]}
    assert _extract_text(res) == "a\nb"


def test_extract_text_handles_empty():
    assert _extract_text(None) == "" and _extract_text({}) == ""


def test_mcp_sse_parse_finds_matching_id():
    sse = 'event: message\ndata: {"jsonrpc":"2.0","id":3,"result":{"ok":true}}\n\n'
    msg = BreethClient._parse_sse(sse, 3)
    assert msg["result"]["ok"] is True


def test_mcp_sse_ignores_other_ids():
    sse = 'data: {"jsonrpc":"2.0","id":9,"result":{}}\n'
    assert BreethClient._parse_sse(sse, 3) is None
