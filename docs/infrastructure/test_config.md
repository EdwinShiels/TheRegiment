✅ Test Setup

Test Suite: `pytest` + `pytest-asyncio`

Tests required for:
- All engine runners (with dummy data)
- Discord command handling (mock events)
- API routes (FastAPI `httpx` test client)

Mocks:
- Discord API
- NeonDB writes (via in-memory or test DB)

Test goal: ensure schema adherence and delivery behavior — not full integration yet.
