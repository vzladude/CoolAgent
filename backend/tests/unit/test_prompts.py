from app.ai.prompts import SYSTEM_PROMPT_CHAT, build_rag_prompt


def test_build_rag_prompt_uses_base_prompt_without_context():
    prompt = build_rag_prompt(None)

    assert prompt == SYSTEM_PROMPT_CHAT
    assert "DOCUMENTACION TECNICA RELEVANTE" not in prompt.upper()


def test_build_rag_prompt_injects_context_and_source_instructions():
    prompt = build_rag_prompt("Manual Carrier 38AKS: codigo E7")

    assert "Manual Carrier 38AKS" in prompt
    assert "DOCUMENTACI" in prompt
    assert "Cita el nombre del documento fuente" in prompt
