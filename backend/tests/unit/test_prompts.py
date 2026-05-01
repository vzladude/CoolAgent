from app.ai.prompts import SYSTEM_PROMPT_CHAT, build_rag_prompt
from app.services.domain_guard import PROMPT_POLICY_VERSION


def test_build_rag_prompt_uses_base_prompt_without_context():
    prompt = build_rag_prompt(None)

    assert prompt == SYSTEM_PROMPT_CHAT
    assert "DOCUMENTACION TECNICA RELEVANTE" not in prompt.upper()


def test_build_rag_prompt_injects_context_and_source_instructions():
    prompt = build_rag_prompt("Manual Carrier 38AKS: codigo E7")

    assert "Manual Carrier 38AKS" in prompt
    assert "DOCUMENTACI" in prompt
    assert "Cita el nombre del documento fuente" in prompt


def test_system_prompt_defines_refrigeration_general_scope_and_policy_version():
    assert PROMPT_POLICY_VERSION in SYSTEM_PROMPT_CHAT
    assert "refrigeración general" in SYSTEM_PROMPT_CHAT
    assert "Neveras y congeladores" in SYSTEM_PROMPT_CHAT
    assert "No respondas consultas" in SYSTEM_PROMPT_CHAT
