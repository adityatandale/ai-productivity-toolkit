# AI Productivity Toolkit

Reusable, tested prompt workflows for everyday work: **summarization, classification, data extraction, email, resume writing, code debugging/review, and research briefs**. Includes an evaluation harness that produces a prompt testing report.

## Quick start
```bash
git clone https://github.com/<your-username>/ai-productivity-toolkit.git
cd ai-productivity-toolkit
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key      # Windows: set ANTHROPIC_API_KEY=your-key
python -m pytest -q                     # offline tests, no key needed
python -m evaluation.eval_prompts       # writes evaluation/report.md
```

```python
from toolkit import LLM, workflows

llm = LLM()
print(workflows.summarize(llm, "…long text…", audience="a new hire", n_bullets=3))
print(workflows.classify(llm, "I was charged twice"))          # {'category': 'billing', ...}
print(workflows.draft_email(llm, context="Demo went well", recipient="Sam (client)",
                            goal="Book a follow-up call", max_words=100))
```

## Project layout
| Path | Purpose |
|---|---|
| `toolkit/llm.py` | LLM wrapper, JSON extraction, self-repair retry for invalid JSON |
| `toolkit/templates.py` | 9 prompt templates (role + context + task + constraints + format) |
| `toolkit/workflows.py` | One-call workflows: summarize, classify, extract, email, resume, debug, review, research |
| `evaluation/eval_prompts.py` | Test cases, automatic checks, Markdown report generator |
| `tests/` | Offline unit tests (fake model backend) |
| `notebooks/Prompt_Engineering_Lab.ipynb` | Colab lab: zero/few-shot, roles, constraints, JSON, debugging, evaluation |
| `docs/prompt_patterns.md` | Prompt engineering cheat sheet |

## Design principles
1. **Every prompt has the same anatomy:** role, context, task, constraints, output format.
2. **Structured outputs are validated**, not trusted: JSON is parsed, checked for keys, and auto-repaired once.
3. **Prompts are tested like code:** labelled cases, measurable checks, a report you can compare across versions.
4. **The model is swappable:** the backend is a plain function, so tests run offline and providers can change.

## Results
Run `python -m evaluation.eval_prompts` and paste your table from `evaluation/report.md` here, along with your analysis of zero-shot vs few-shot.

## Limitations
- Automatic checks verify format and labels, not writing quality; review generated emails and resumes yourself.
- Resume prompts forbid invented metrics, but always verify every claim before sending.
- Small test sets give noisy rates; add more cases for real decisions.

## License
MIT
