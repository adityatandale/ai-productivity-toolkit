"""Reusable prompt templates.

Each template follows one anatomy: ROLE (system) + CONTEXT + TASK + CONSTRAINTS + OUTPUT FORMAT.
Placeholders use {name}; render() fails loudly if one is missing. Literal JSON braces are safe
because only known {identifier} placeholders are substituted.
"""
import re
from dataclasses import dataclass

_VAR = re.compile(r"\{([a-z_]+)\}")


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    system: str
    template: str
    description: str = ""

    @property
    def variables(self):
        return sorted(set(_VAR.findall(self.template)))

    def render(self, **values) -> str:
        missing = [v for v in self.variables if v not in values]
        if missing:
            raise KeyError(f"{self.name}: missing variables {missing}")
        return _VAR.sub(lambda m: str(values[m.group(1)]), self.template)


_T = [
    PromptTemplate(
        "summarize",
        "You are a precise editor who writes faithful, concise summaries.",
        """Summarize the text below for {audience}.

Constraints:
- Exactly {n_bullets} bullet points, each under 20 words.
- Use only information present in the text. Do not add facts.
- End with one line starting "Action:" giving the single most important next step, or "Action: none".

Text:
\"\"\"
{text}
\"\"\"""",
        "Bullet summary with an action line.",
    ),
    PromptTemplate(
        "classify_zero_shot",
        "You are a support-ticket classifier.",
        """Classify the message into exactly one category: billing, technical, account, other.
Return ONLY JSON: {"category": "<category>", "confidence": <0-1>, "reason": "<max 15 words>"}

Message: {text}""",
        "Zero-shot classification with JSON output.",
    ),
    PromptTemplate(
        "classify_few_shot",
        "You are a support-ticket classifier.",
        """Classify the message into exactly one category: billing, technical, account, other.
Return ONLY JSON: {"category": "<category>", "confidence": <0-1>, "reason": "<max 15 words>"}

Examples:
Message: I was charged twice this month.
{"category": "billing", "confidence": 0.95, "reason": "duplicate charge"}

Message: The app crashes when I upload a photo.
{"category": "technical", "confidence": 0.93, "reason": "app crash on upload"}

Message: I can't remember which email I signed up with.
{"category": "account", "confidence": 0.9, "reason": "forgotten sign-up email"}

Message: Do you have an office in Berlin?
{"category": "other", "confidence": 0.85, "reason": "general company question"}

Now classify:
Message: {text}""",
        "Few-shot classification (4 examples) with JSON output.",
    ),
    PromptTemplate(
        "extract_entities",
        "You extract structured data from text. You never invent values.",
        """Extract fields from the text. Use an empty list for anything not stated.
Return ONLY JSON with keys: "people" (list of strings), "organizations" (list of strings),
"dates" (list of strings), "amounts" (list of strings).

Text: {text}""",
        "Entity extraction to JSON.",
    ),
    PromptTemplate(
        "email_draft",
        "You are an executive assistant who writes clear, courteous business email.",
        """Write an email.

Context: {context}
Recipient: {recipient}
Goal: {goal}
Tone: {tone}

Constraints:
- Under {max_words} words.
- Subject line first, formatted as "Subject: ...".
- One clear call to action in the last sentence.
- No filler openers such as "I hope this email finds you well".""",
        "Goal-driven email with tone and length limits.",
    ),
    PromptTemplate(
        "resume_bullets",
        "You are a career coach who writes achievement-focused resume bullets.",
        """Rewrite the experience below as {n_bullets} resume bullets for the target role: {target_role}.

Rules:
- Start each bullet with a strong past-tense verb.
- Keep numbers that appear in the input. NEVER invent metrics; if none exist, describe scope or outcome qualitatively.
- Max 25 words per bullet.
- Mirror relevant keywords from the job description only when they are truthful.

Job description:
{job_description}

My experience:
{experience}""",
        "Truthful, tailored resume bullets.",
    ),
    PromptTemplate(
        "code_debug",
        "You are a senior engineer who debugs methodically and explains root causes.",
        """Debug the {language} code below.

Return in this order:
1. Root cause (2 sentences max)
2. Fixed code (complete, in one code block)
3. Why the fix works (2 sentences max)
4. One test that would have caught this bug

Code:
```
{code}
```

Error / unexpected behavior:
{error}""",
        "Structured debugging response.",
    ),
    PromptTemplate(
        "code_review",
        "You are a careful code reviewer focused on correctness, security and readability.",
        """Review the {language} code below.
Return ONLY a JSON list. Each item: {"severity": "high|medium|low", "line": <int or null>, "issue": "<text>", "suggestion": "<text>"}.
Return [] if you find no issues. Do not comment on style preferences.

Code:
```
{code}
```""",
        "Code review as machine-readable JSON.",
    ),
    PromptTemplate(
        "research_brief",
        "You are a research analyst. You separate established facts from uncertainty.",
        """Create a research brief on: {topic}

Audience: {audience}

Structure:
1. Key question (1 sentence)
2. What is well established (3 bullets)
3. What is uncertain or debated (2 bullets)
4. Five follow-up questions worth investigating
5. Suggested sources to verify (types of sources, not made-up citations)

Do not fabricate statistics, quotes or citations. If you are unsure, say so.""",
        "Research starter with uncertainty flags.",
    ),
]

TEMPLATES = {t.name: t for t in _T}
