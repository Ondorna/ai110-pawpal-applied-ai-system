# Model Card — PawPal+

## Model Overview

**Model used:** Gemini 2.5 Flash Lite (via Google GenAI SDK)  
**Task:** Retrieval-Augmented Generation — given a pet's profile and a curated knowledge snippet, generate personalised pet care advice.  
**Interface:** Streamlit web app

---

## AI Collaboration

I used Claude to help design and build this system.

**Helpful:** Claude suggested separating the RAG logic into its own module (`rag_engine.py`) rather than putting everything in `app.py`. This made it possible to write and run `test_rag.py` independently without launching the full UI — a genuinely good software design decision I wouldn't have prioritised on my own.

**Flawed:** Claude generated code using `google.generativeai`, which is deprecated, and used `list[str]` type hints that only work in Python 3.10+. My environment is Python 3.9, so both broke immediately. I had to switch to the `google-genai` SDK and replace type hints with `List[str]` from the `typing` module. Good reminder to always test AI-generated code in your actual environment before assuming it works.

---

## Biases and Limitations

- The knowledge base contains general pet care advice only. It does not account for breed-specific needs, individual health conditions, or regional veterinary standards.
- The system has no memory — it cannot track changes in a pet's health over time.
- Advice quality depends on how well the user's focus area matches the knowledge base sections. A vague or off-topic query may retrieve irrelevant context.
- The model may produce overly optimistic advice for pets with special medical needs not captured in the task list.

---

## Potential Misuse

A user could rely on PawPal+ advice instead of consulting a vet, especially for health-related questions. To mitigate this, all outputs are framed as suggestions and health responses always recommend professional consultation. The system does not diagnose conditions or prescribe treatments.

---

## Testing Results

```
python test_rag.py
Results: 9/9 tests passed ✅
```

| Test | Result |
|------|--------|
| Dog knowledge file loads | ✅ PASS |
| Cat knowledge file loads | ✅ PASS |
| Unknown species falls back to other_care.txt | ✅ PASS |
| Keyword 'FEEDING' matches dog section | ✅ PASS |
| Keyword 'EXERCISE' matches cat section | ✅ PASS |
| No keyword match returns full fallback text | ✅ PASS |
| High confidence: dog + feeding + tasks | ✅ PASS |
| Medium confidence: cat + grooming + no tasks | ✅ PASS |
| Lower confidence for unknown species | ✅ PASS |

**What I learned:** Testing retrieval separately from generation made debugging much faster. I could confirm the knowledge base was loading correctly before troubleshooting API issues.

**Surprises:** The confidence score for "rabbit" came back as 40% instead of 0%, because `other_care.txt` exists as a fallback. Technically correct, but it could mislead a user into thinking the system has specific rabbit knowledge. A future fix would distinguish between exact species matches and generic fallbacks in the confidence label.

---

## Confidence Scoring

Before each Gemini API call, the system runs `estimate_confidence()` which checks:
- Does a knowledge file exist for this species? (+0.4)
- Does the file contain a section matching the focus area? (+0.3)
- Does the pet have at least one existing task? (+0.3)

This gives users a signal about how well-grounded the AI response will be before they see it.