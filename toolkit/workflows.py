"""High-level, reusable workflows built from templates. Each takes an LLM instance."""
from .llm import LLM
from .templates import TEMPLATES


def _run(llm: LLM, name: str, temperature: float = 0.2, **vars) -> str:
    t = TEMPLATES[name]
    return llm.complete(t.render(**vars), system=t.system, temperature=temperature)


def _run_json(llm: LLM, name: str, **vars):
    t = TEMPLATES[name]
    return llm.complete_json(t.render(**vars), system=t.system, temperature=0.0)


def summarize(llm: LLM, text: str, audience: str = "a busy executive", n_bullets: int = 3) -> str:
    return _run(llm, "summarize", text=text, audience=audience, n_bullets=n_bullets)


def classify(llm: LLM, text: str, few_shot: bool = True) -> dict:
    return _run_json(llm, "classify_few_shot" if few_shot else "classify_zero_shot", text=text)


def extract_entities(llm: LLM, text: str) -> dict:
    return _run_json(llm, "extract_entities", text=text)


def draft_email(llm: LLM, context: str, recipient: str, goal: str,
                tone: str = "professional and friendly", max_words: int = 120) -> str:
    return _run(llm, "email_draft", temperature=0.5, context=context, recipient=recipient,
                goal=goal, tone=tone, max_words=max_words)


def resume_bullets(llm: LLM, experience: str, job_description: str, target_role: str,
                   n_bullets: int = 4) -> str:
    return _run(llm, "resume_bullets", temperature=0.4, experience=experience,
                job_description=job_description, target_role=target_role, n_bullets=n_bullets)


def debug_code(llm: LLM, code: str, error: str, language: str = "Python") -> str:
    return _run(llm, "code_debug", code=code, error=error, language=language)


def review_code(llm: LLM, code: str, language: str = "Python") -> list:
    return _run_json(llm, "code_review", code=code, language=language)


def research_brief(llm: LLM, topic: str, audience: str = "a smart non-expert") -> str:
    return _run(llm, "research_brief", temperature=0.3, topic=topic, audience=audience)
