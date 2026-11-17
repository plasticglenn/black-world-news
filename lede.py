# ============================================================
# BLACK WORLD NEWS: the lede
# Pulls the publisher's own opening line for a story, so cards
# show a headline plus the first line of the article (BBC style)
# instead of an AI written summary. Our analysis lives elsewhere.
# ============================================================
import re
import html as _html

MAX_LEN = 220

# Paragraphs that are page furniture, not the story.
_JUNK = re.compile(
    r"(cookie|subscribe|sign up|newsletter|javascript|your browser|all rights reserved|"
    r"copyright|advertisement|click here|read more|share this|follow us|photo:|image:|"
    r"getty images|reuters/|ap photo|file photo|published|updated|minutes? ago|hours? ago)",
    re.I,
)


_ABBR = {"Mr", "Mrs", "Ms", "Dr", "Prof", "Gen", "Gov", "Sen", "Rep", "St", "Jr", "Sr",
         "Rev", "Hon", "Lt", "Col", "Sgt", "Capt", "No", "vs", "U.S", "U.K", "U.N", "Inc", "Ltd", "Co"}


def _clean(text):
    text = _html.unescape(text or "")
    text = re.sub(r"\s+", " ", text).strip()
    # Drop a wire dateline like "LAGOS, Nigeria (AP) — " or "ACCRA (Reuters) - "
    text = re.sub(r"^[A-Z][A-Z .,'/]{2,60}\((?:AP|Reuters|AFP|CNN|BBC)\)\s*[—–-]+\s*", "", text)
    return text


def first_sentence(text, max_len=MAX_LEN):
    # One sentence, trimmed at a word if it runs long.
    text = _clean(text)
    if not text:
        return ""
    s = text
    for m in re.finditer(r"[.!?][\"\u201d\u2019']?(?=\s+[A-Z\u201c\"])", text):
        before = text[:m.start()].rsplit(" ", 1)[-1]
        if before in _ABBR or len(before.replace(".", "")) <= 1:
            continue   # "Dr. Asare", "U.S. officials", "J. Mensah"
        s = text[:m.end()]
        break
    if len(s) > max_len:
        s = s[:max_len].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    return s


def _meta(soup, *names):
    for n in names:
        tag = soup.find("meta", property=n) or soup.find("meta", attrs={"name": n})
        if tag and tag.get("content", "").strip():
            return tag["content"]
    return ""


def _first_paragraph(soup):
    body = soup.find("article") or soup.find("main") or soup.body or soup
    for p in body.find_all("p"):
        t = _clean(p.get_text(" "))
        if len(t) < 60 or _JUNK.search(t[:80]):
            continue
        return t
    return ""


def extract_lede(soup):
    # The publisher's standfirst (og:description) is the line news sites
    # write for exactly this job, so it comes first. Otherwise take the
    # opening paragraph of the article body.
    desc = _clean(_meta(soup, "og:description", "description", "twitter:description"))
    if len(desc) >= 40 and not _JUNK.search(desc[:60]):
        return first_sentence(desc)
    para = _first_paragraph(soup)
    return first_sentence(para) if para else ""
