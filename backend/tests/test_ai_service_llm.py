import app.services.ai_service as ai_service


def test_summarize_text_uses_llm_when_api_key_present(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        ai_service,
        "_call_openai",
        lambda prompt, *, model=None, max_tokens=None: {
            "content": "A polished LLM summary for the requested content."
        },
        raising=False,
    )

    summary = ai_service.summarize_text(
        "Artificial intelligence is transforming healthcare by improving diagnosis, treatment planning, and patient monitoring."
    )

    assert summary["summary"] == "A polished LLM summary for the requested content."
