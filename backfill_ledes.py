# ============================================================
# BLACK WORLD NEWS: lede backfill
# Visits each story's original page once and saves the
# publisher's first line as "lede". Newest stories go first so
# the homepage fills in early. Saves every 50 stories, so you
# can stop it any time and run it again to carry on.
#   python backfill_ledes.py
# ============================================================
import json, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from lede import extract_lede

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ARCHIVE = "stories.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def fetch(url):
    try:
        r = requests.get(url, timeout=12, headers=HEADERS)
        if r.status_code >= 400:
            return ""
        return extract_lede(BeautifulSoup(r.text, "html.parser"))
    except Exception:
        return ""


def main():
    with open(ARCHIVE, "r", encoding="utf-8") as f:
        stories = json.load(f)
    todo = [s for s in stories if "lede" not in s and s.get("url", "").startswith("http")]
    todo.sort(key=lambda s: s.get("saved_at", ""), reverse=True)
    print(f"{len(todo)} stories need a lede.")

    done = got = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, s["url"]): s for s in todo}
        for fut in as_completed(futures):
            s = futures[fut]
            s["lede"] = fut.result()   # "" means we tried; the card shows the headline only
            done += 1
            got += bool(s["lede"])
            if done % 50 == 0 or done == len(todo):
                with open(ARCHIVE, "w", encoding="utf-8") as f:
                    json.dump(stories, f, indent=2, ensure_ascii=False)
                print(f"  {done}/{len(todo)} checked, {got} ledes found")
    print("Done. Now run: python generate_site.py")


if __name__ == "__main__":
    main()
