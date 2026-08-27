from app.schemas.chat import ChatResponse, AITask
from app.services.llm import llm_service

async def test_chat_success(client, monkeypatch):
    async def fake_ask(message: str) -> ChatResponse:
        return ChatResponse(
            answer="Here is your plan",
            tasks=[
                AITask(
                    title="Learn pytest",
                    note="Practice monkeypatch",
                )
            ],
        )

    monkeypatch.setattr(
        llm_service,
        "ask",
        fake_ask,
    )

    response = await client.post(
        "/chat",
        json={"message": "Make me a study plan"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "Here is your plan"
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Learn pytest"
    assert data["tasks"][0]["note"] == "Practice monkeypatch"

async def test_chat_llm_unavailable(client, monkeypatch):
    async def fake_ask(message: str):
        raise RuntimeError("LLM service is unavailable")

    monkeypatch.setattr(
        llm_service,
        "ask",
        fake_ask,
    )

    response = await client.post(
        "/chat",
        json={"message": "Hello"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "LLM service is temporarily unavailable"
    }

async def test_chat_empty_message(client):
    response = await client.post(
        "/chat",
        json={"message": ""},
    )

    assert response.status_code == 422