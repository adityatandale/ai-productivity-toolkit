"""Prompt evaluation harness.

Runs labelled test cases against prompt variants, scores them with automatic checks,
and writes a Markdown testing report.

    python -m evaluation.eval_prompts            # real model (needs ANTHROPIC_API_KEY)
    python -m evaluation.eval_prompts --out evaluation/report.md
"""
import argparse
import datetime
import sys
from collections import defaultdict

from toolkit import LLM, TEMPLATES, extract_json

# (message, expected category) -- extend with your own edge cases
CLASSIFY_CASES = [
    ("I was billed $49 but my plan costs $29.", "billing"),
    ("The dashboard shows a blank page after login.", "technical"),
    ("Please change the email address on my profile.", "account"),
    ("Where can I read your privacy policy?", "other"),
    ("My card was declined even though it has funds.", "billing"),
    ("API returns 500 when I send a JSON body.", "technical"),
    ("I want to delete my account permanently.", "account"),
    ("Can you recommend a good project management book?", "other"),
    ("Refund me, this is the third time you double charged me!!", "billing"),      # noisy
    ("app not working", "technical"),                                              # vague
]

SUMMARY_TEXT = (
    "The quarterly review showed revenue up 12% year over year, driven mainly by the new "
    "subscription tier. Churn rose slightly from 3.1% to 3.6%, concentrated in customers on "
    "monthly plans. Support tickets about billing doubled after the pricing change. The team "
    "proposes offering annual-plan discounts and adding a billing FAQ before the next release."
)

ENTITY_TEXT = "On 3 March 2026, Priya Nair of Acme Corp signed a $250,000 contract with Globex."


def check_classification(reply, expected):
    checks = {}
    try:
        data = extract_json(reply)
        checks["valid_json"] = True
        checks["has_keys"] = isinstance(data, dict) and {"category", "confidence", "reason"} <= set(data)
        checks["allowed_label"] = data.get("category") in {"billing", "technical", "account", "other"}
        checks["correct"] = data.get("category") == expected
    except (ValueError, AttributeError):
        checks.update(valid_json=False, has_keys=False, allowed_label=False, correct=False)
    return checks


def check_summary(reply, n_bullets=3):
    lines = [l.strip() for l in reply.splitlines() if l.strip()]
    bullets = [l for l in lines if l.startswith(("-", "*", "•"))]
    return {
        "bullet_count": len(bullets) == n_bullets,
        "bullets_under_20_words": all(len(b.lstrip("-*• ").split()) < 20 for b in bullets),
        "has_action_line": any(l.lower().startswith("action:") for l in lines),
    }


def check_entities(reply):
    try:
        d = extract_json(reply)
    except ValueError:
        return {"valid_json": False}
    ok_keys = isinstance(d, dict) and {"people", "organizations", "dates", "amounts"} <= set(d)
    flat = " ".join(str(v) for v in (d.values() if isinstance(d, dict) else []))
    return {"valid_json": True, "has_keys": ok_keys,
            "found_person": "Priya" in flat, "found_amount": "250,000" in flat}


def run(llm, out_path):
    rows = defaultdict(lambda: defaultdict(list))   # variant -> check -> [bool]
    failures = []

    for variant in ("classify_zero_shot", "classify_few_shot"):
        t = TEMPLATES[variant]
        for text, expected in CLASSIFY_CASES:
            reply = llm.complete(t.render(text=text), system=t.system, temperature=0.0, max_tokens=200)
            for name, ok in check_classification(reply, expected).items():
                rows[variant][name].append(ok)
                if name == "correct" and not ok:
                    failures.append((variant, text, expected, reply[:120]))

    t = TEMPLATES["summarize"]
    reply = llm.complete(t.render(text=SUMMARY_TEXT, audience="an executive", n_bullets=3),
                         system=t.system, temperature=0.0)
    for name, ok in check_summary(reply).items():
        rows["summarize"][name].append(ok)

    t = TEMPLATES["extract_entities"]
    reply = llm.complete(t.render(text=ENTITY_TEXT), system=t.system, temperature=0.0, max_tokens=300)
    for name, ok in check_entities(reply).items():
        rows["extract_entities"][name].append(ok)

    lines = [
        "# Prompt Testing Report",
        f"\nGenerated: {datetime.datetime.now():%Y-%m-%d %H:%M}  |  Model: `{llm.model}`  |  API calls: {llm.calls}\n",
        "| Prompt variant | Check | Passed | Rate |",
        "|---|---|---|---|",
    ]
    for variant, checks in rows.items():
        for check, results in checks.items():
            p = sum(results)
            lines.append(f"| {variant} | {check} | {p}/{len(results)} | {p/len(results):.0%} |")

    lines += ["\n## Failed classification cases\n"]
    if failures:
        lines += ["| Variant | Input | Expected | Model reply |", "|---|---|---|---|"]
        lines += [f"| {v} | {t} | {e} | `{r.replace(chr(10), ' ')}` |" for v, t, e, r in failures]
    else:
        lines.append("None.")
    lines += ["\n## Analysis (fill in)\n",
              "- Which variant won and by how much?",
              "- What kinds of inputs failed (noisy, vague, ambiguous)?",
              "- What prompt change will you try next, and what result do you expect?"]

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Report written to {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="evaluation/report.md")
    args = ap.parse_args()
    try:
        run(LLM(), args.out)
    except Exception as e:  # noqa: BLE001
        sys.exit(f"Could not run evaluation: {e}\nSet ANTHROPIC_API_KEY first.")
