# PawPal+ — AI Pet Care Planner

A Streamlit app that helps pet owners plan daily care routines. I extended my Module 2 project by adding a RAG-powered AI advice engine using the Gemini API.


🎬 [Watch the demo](https://www.loom.com/share/15ca298692d94ec483a22cbcdc6070e7)

---

## Original Project

Built on top of [Module 2: PawPal+](https://github.com/Ondorna/ai110-module2show-pawpal-starter), which had task scheduling, conflict detection, and JSON persistence but no AI. I added a RAG engine that retrieves care knowledge before calling the AI, so advice is grounded in real facts instead of hallucinated.

---

## What it does

- Add and manage pet care tasks (walks, feeding, grooming, etc.)
- Generate a daily schedule with conflict detection
- Get AI advice tailored to your pet's species, age, and existing schedule
- See a confidence score before each AI call
- All RAG calls are logged to `pawpal_rag.log`

---

## Architecture

![System Architecture](assets/architecture.png)

```
User input → Streamlit UI → RAG engine → Gemini API → advice
                                ↑
                         knowledge_base/
                           dog_care.txt
                           cat_care.txt
                           other_care.txt
```

User picks a pet and focus area. The RAG engine pulls the relevant section from the knowledge base, builds a prompt with the pet's profile and current tasks, and sends it to Gemini. The response shows up alongside the raw retrieved text so you can see exactly what the AI was working from.

---

## Setup

```bash
git clone https://github.com/Ondorna/ai110-module2show-pawpal-starter.git
cd ai110-module2show-pawpal-starter
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with your Gemini API key (get one free at [aistudio.google.com](https://aistudio.google.com/apikey)):

```
GEMINI_API_KEY=your_key_here
```

```bash
streamlit run app.py   # start the app
python test_rag.py     # run tests
```

---

## Sample outputs

**Dog, exercise, 3 tasks scheduled, confidence 100%:**
> "Mochi is 3 years old, so a good baseline for daily exercise is 30–60 minutes. It's great that Mochi already has three walks scheduled! Consider making one a sniff walk for mental stimulation, adding a short 5–15 minute training session between walks, and rotating toys regularly to prevent boredom."

**Retrieved knowledge (RAG context):**
> EXERCISE section from `dog_care.txt` — most adult dogs need 30–60 minutes per day, puppies need short frequent play sessions, avoid intense exercise after meals.

**Confidence score:**
- Dog + exercise + 3 tasks → 100% ✅
- Unknown species + no tasks → 40% ⚠️ (falls back to `other_care.txt`)

---

## Design decisions

I chose keyword-based retrieval over a vector database because the knowledge base is small and structured — FEEDING, EXERCISE, GROOMING sections match cleanly to user intent without needing embeddings. It's also easier to debug.

I kept `rag_engine.py` separate from `app.py` so I could test retrieval and confidence scoring without spinning up the UI.

The confidence score was my way of making the system's uncertainty visible — if the score is low, the AI has less to work from and the output should be taken with more skepticism.

---

## Testing

```bash
python test_rag.py
# 9/9 tests passed ✅
```

Tests cover file loading, keyword matching, fallback behavior, and confidence scoring. I ran retrieval tests separately from generation so I could confirm the knowledge base was working before debugging API issues.

The biggest hurdle was the Gemini SDK — `google.generativeai` is deprecated and `gemini-2.0-flash` hit free-tier quota limits immediately. I switched to `google-genai` and `gemini-2.5-flash-lite` which resolved both.

---

## Reflection

The knowledge base only covers general advice — it doesn't know about breed-specific needs or individual health conditions. Someone could use this instead of consulting a vet, which is a real risk. I tried to mitigate it by framing all output as suggestions and always recommending vet visits for health questions.

The "rabbit" edge case surprised me: it scored 40% confidence instead of 0% because `other_care.txt` exists as a fallback. Technically correct, but misleading — a user might think I have specific rabbit data.

Claude was useful for the initial architecture but generated code with deprecated imports and Python 3.10-only type hints that broke on my 3.9 setup. I had to fix both manually. Good reminder to always test AI-generated code in your actual environment.

---

## Project structure

```
├── app.py              # Streamlit UI
├── rag_engine.py       # retrieval + generation + confidence scoring
├── pawpal_system.py    # Owner, Pet, Task, Scheduler
├── test_rag.py         # 9 tests
├── data.json           # persisted data
├── pawpal_rag.log      # RAG call log
├── assets              # architecture diagram
└── knowledge_base/
    ├── dog_care.txt
    ├── cat_care.txt
    └── other_care.txt
```

Dependencies: `streamlit`, `google-genai`, `python-dotenv`, `pytest`

---

*CodePath AI110 — Module 5 Final Project*