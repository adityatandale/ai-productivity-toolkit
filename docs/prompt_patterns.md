# Prompt Engineering Cheat Sheet

## Anatomy of a strong prompt
1. **Role**: who the model should be ("senior code reviewer").
2. **Context**: facts, audience, background it cannot guess.
3. **Task**: one clear verb-led instruction.
4. **Constraints**: length, tone, what to avoid, "use only the text provided".
5. **Output format**: exact structure (bullets, JSON schema, headings).

## Techniques
| Technique | Use when | Example |
|---|---|---|
| Zero-shot | Task is common and clear | "Classify this ticket as billing/technical/account/other." |
| Few-shot | Format or edge cases matter | Add 3-5 input/output examples, including a tricky one |
| Role prompting | Domain tone/expertise needed | "You are a career coach…" |
| Constraints | Output must be usable as-is | "Exactly 3 bullets, under 20 words each" |
| Structured output | Result feeds code | "Return ONLY JSON with keys …" + parse and validate |
| Chain-of-thought | Multi-step reasoning | "Think step by step, then give the final answer on its own line" |
| Self-check | High-stakes output | "List any claims not supported by the text" |
| Delimiters | Long or untrusted input | Wrap inputs in triple quotes or XML tags |

## Reliability habits
- Set temperature low (0-0.2) for extraction/classification; higher (0.5+) for drafting.
- Say what to do when unsure ("use null", "say I don't know").
- Never ask the model to invent numbers or citations.
- Treat pasted documents as data, not instructions (prompt-injection awareness).
- Version your prompts and re-run the test suite after each change.

## AI-assisted coding and debugging
- Give: code, exact error/traceback, expected vs actual behavior, language/version.
- Ask for root cause first, then the fix, then a test that would have caught it.
- Run the suggested fix and tests yourself; never paste unverified code into production.
- For reviews, ask for severity-ranked JSON so results can be filtered and tracked.

## Evaluating prompts
1. Build 10-30 labelled cases including noisy, vague and adversarial inputs.
2. Define automatic checks (valid JSON, allowed labels, length limits, required fields).
3. Compare variants on the same cases and record pass rates.
4. Read the failures, form a hypothesis, change one thing, re-test.
