# ============================================================
# BLACK WORLD NEWS — Framing Backfill
# Re-writes narrative_analysis for old stories that were cut off
# mid-sentence or that all start the same boring way ("The story
# frames..."). Also fills in cui_bono where it is missing.
# Runs through the archive, saving after every story so a rate
# limit never loses progress. Just run it again to continue.
#   python backfill_framing.py
# ============================================================
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from groq import Groq
from json_repair import repair_json

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"
ARCHIVE = "stories.json"


def load():
    with open(ARCHIVE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(d):
    with open(ARCHIVE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def needs_fix(s):
    na = (s.get("narrative_analysis") or "").strip()
    if not na:
        return True
    # Cut off mid-sentence (no ending punctuation)
    if na[-1] not in ".!?\"”":
        return True
    # Boring repeated opener
    low = na.lower()
    if low.startswith("the story frames") or low.startswith("this story frames"):
        return True
    # Missing the "who benefits" line
    if not (s.get("cui_bono") or "").strip():
        return True
    return False


def fix_one(s):
    title = s.get("title_en") or s.get("title", "")
    summary = s.get("summary_en") or s.get("summary", "")
    framing = s.get("narrative_framing", "")
    prompt = f"""You are a media analyst for a news service covering Black communities globally.

Story headline: {title}
Story summary: {summary}
Current framing label: {framing}

Write JSON only with two fields:
- "narrative_analysis": ONE complete, self-contained sentence (about 20 to 35 words) describing how Black people are portrayed in this story and what that portrayal implies. It MUST end in a period and never be cut off. Vary the opening — DO NOT begin with "The story frames" or "This story frames". Open naturally, fitting THIS story (e.g. "Black Britons appear mainly as...", "By reducing the issue to numbers...", "Readers meet these communities as...", "Portrayed as resilient...", "Notably absent is...").
- "cui_bono": one plain sentence, max 15 words, naming the specific entity, corporation, government, or industry that benefits most from the conditions described. If genuinely unclear, write "Unclear." No moralizing.
"""
    resp = client.chat.completions.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.choices[0].message.content
    if "```" in raw:
        raw = raw.split("```")[-2] if raw.count("```") >= 2 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw[raw.find("{"):raw.rfind("}") + 1].strip()
    data = json.loads(repair_json(raw))
    return data


def main():
    stories = load()
    todo = [i for i, s in enumerate(stories) if needs_fix(s)]
    print(f"{len(todo)} of {len(stories)} stories need a framing fix.\n")
    done = 0
    for n, i in enumerate(todo, 1):
        s = stories[i]
        title = (s.get("title_en") or s.get("title", ""))[:60]
        try:
            data = fix_one(s)
            if data.get("narrative_analysis"):
                s["narrative_analysis"] = data["narrative_analysis"].strip()
            if data.get("cui_bono"):
                s["cui_bono"] = data["cui_bono"].strip()
            save(stories)  # save after every story
            done += 1
            print(f"[{n}/{len(todo)}] OK  {title}")
        except Exception as e:
            msg = str(e)
            if "429" in msg or "rate_limit" in msg:
                print(f"\nRate limit reached after {done} fixes. "
                      f"Run again later to continue.")
                break
            print(f"[{n}/{len(todo)}] FAIL {title} — {msg[:80]}")
    print(f"\nDone for now. Fixed {done} stories this run.")


if __name__ == "__main__":
    main()
