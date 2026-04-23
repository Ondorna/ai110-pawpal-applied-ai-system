"""
test_rag.py — Automated test harness for PawPal+ RAG engine

Runs without calling the Gemini API (tests retrieval + confidence only).
Run with:  python test_rag.py
"""

from rag_engine import retrieve, estimate_confidence

PASS = "✅ PASS"
FAIL = "❌ FAIL"
results = []


def check(name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    results.append((name, status, detail))
    print(f"{status}  {name}" + (f" — {detail}" if detail else ""))


# ── Retrieval tests ───────────────────────────────────────────────────────────

# 1. Dog file loads
text = retrieve("dog")
check("Dog knowledge file loads", len(text) > 100, f"{len(text)} chars")

# 2. Cat file loads
text = retrieve("cat")
check("Cat knowledge file loads", len(text) > 100, f"{len(text)} chars")

# 3. Unknown species falls back to other_care.txt
text = retrieve("rabbit")
check("Unknown species falls back to other_care.txt", len(text) > 100)

# 4. Keyword match returns relevant section
text = retrieve("dog", ["FEEDING"])
check("Keyword 'FEEDING' matches dog section", "FEEDING" in text)

# 5. Keyword match for exercise
text = retrieve("cat", ["EXERCISE"])
check("Keyword 'EXERCISE' matches cat section", "EXERCISE" in text)

# 6. No keyword match → returns full file (fallback)
text = retrieve("dog", ["NONEXISTENTKEYWORD99"])
check("No keyword match returns full fallback text", len(text) > 100)

# ── Confidence tests ──────────────────────────────────────────────────────────

# 7. Known species + matching focus + tasks → high confidence
score = estimate_confidence("dog", "feeding", ["Morning walk", "Feed breakfast"])
check("High confidence: dog + feeding + tasks", score >= 0.9, f"score={score}")

# 8. Known species + focus, no tasks → medium confidence
score = estimate_confidence("cat", "grooming", [])
check("Medium confidence: cat + grooming + no tasks", 0.5 <= score <= 0.8, f"score={score}")

# 9. Unknown species → lower confidence (no exact file)
score = estimate_confidence("rabbit", "general", [])
check("Lower confidence for unknown species", score <= 0.5, f"score={score}")

# ── Summary ───────────────────────────────────────────────────────────────────
passed = sum(1 for _, s, _ in results if s == PASS)
total = len(results)
print(f"\n{'─'*40}")
print(f"Results: {passed}/{total} tests passed")
if passed == total:
    print("🎉 All tests passed!")
else:
    failed = [(n, d) for n, s, d in results if s == FAIL]
    print("Failed tests:")
    for name, detail in failed:
        print(f"  • {name} {detail}")