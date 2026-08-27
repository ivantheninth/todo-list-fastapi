import pytest
from openai import OpenAIError

from app.services.llm import llm_service


async def test_llm_success(monkeypatch):
    class FakeResponse:
        output_text = """
        {
            "answer": "Here is your plan",
            "tasks": [
                {
                    "title": "Learn pytest",
                    "note": "Practice unit tests"
                }
            ]
        }
        """

    async def fake_create(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        llm_service.client.responses,
        "create",
        fake_create,
    )

    result = await llm_service.ask("Make me a study plan")

    assert result.answer == "Here is your plan"
    assert len(result.tasks) == 1
    assert result.tasks[0].title == "Learn pytest"
    assert result.tasks[0].note == "Practice unit tests"

import pytest


async def test_llm_invalid_json(monkeypatch):
    class FakeResponse:
        output_text = "This is not JSON"

    async def fake_create(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        llm_service.client.responses,
        "create",
        fake_create,
    )

    with pytest.raises(
        RuntimeError,
        match="LLM returned invalid JSON",
    ):
        await llm_service.ask("Make me a study plan")

async def test_llm_invalid_response_structure(monkeypatch):
    class FakeResponse:
        output_text = """
        {
            "wrong_field": "something"
        }
        """

    async def fake_create(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        llm_service.client.responses,
        "create",
        fake_create,
    )

    with pytest.raises(
        RuntimeError,
        match="LLM returned invalid response structure",
    ):
        await llm_service.ask("Make me a study plan")

async def test_llm_openai_error(monkeypatch):
    async def fake_create(*args, **kwargs):
        raise OpenAIError("OpenAI is unavailable")

    monkeypatch.setattr(
        llm_service.client.responses,
        "create",
        fake_create,
    )

    with pytest.raises(
        RuntimeError,
        match="LLM service is unavailable",
    ):
        await llm_service.ask("Make me a study plan")