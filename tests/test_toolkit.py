"""Offline tests: a fake backend stands in for the model, so no API key is needed."""
import pytest

from evaluation.eval_prompts import check_classification, check_summary
from toolkit import LLM, TEMPLATES, extract_json, workflows


def fake(reply):
    return LLM(backend=lambda system, prompt, temperature, max_tokens: reply)


def test_extract_json_plain():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_fenced_and_prose():
    assert extract_json('Sure!\n```json\n{"a": 1}\n```\nDone.') == {"a": 1}
    assert extract_json('Here you go: [1, 2, 3] hope that helps') == [1, 2, 3]


def test_extract_json_failure():
    with pytest.raises(ValueError):
        extract_json("no json here")


def test_all_templates_render_and_keep_json_braces():
    for name, t in TEMPLATES.items():
        values = {v: "X" for v in t.variables}
        rendered = t.render(**values)
        assert "{" not in "".join(f"{{{v}}}" for v in t.variables if f"{{{v}}}" in rendered)
    assert '{"category"' in TEMPLATES["classify_zero_shot"].render(text="hi")


def test_missing_variable_raises():
    with pytest.raises(KeyError):
        TEMPLATES["summarize"].render(text="x")


def test_classify_workflow_parses_json():
    llm = fake('```json\n{"category": "billing", "confidence": 0.9, "reason": "charge"}\n```')
    assert workflows.classify(llm, "double charged")["category"] == "billing"


def test_json_repair_retry():
    replies = iter(["not json", '{"people": [], "organizations": [], "dates": [], "amounts": []}'])
    llm = LLM(backend=lambda *a: next(replies))
    assert "people" in workflows.extract_entities(llm, "text")
    assert llm.calls == 2


def test_check_classification():
    good = check_classification('{"category":"billing","confidence":0.9,"reason":"x"}', "billing")
    assert all(good.values())
    assert check_classification("oops", "billing")["valid_json"] is False


def test_check_summary():
    text = "- one\n- two\n- three\nAction: send FAQ"
    assert all(check_summary(text).values())
    assert check_summary("- only one")["bullet_count"] is False
