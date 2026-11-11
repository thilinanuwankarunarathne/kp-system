"""(විකල්ප) Local LLM (Ollama - නොමිලේ) මගින් පිටු වලින් KP නීති JSON ලෙස උපුටා rules වගුවට දමයි.
පෙර: ollama pull qwen2.5:7b     ධාවනය: python extract_rules.py <book_id>
පිටු අංකය සහිතව සුරකින නිසා සෑම නීතියක්ම මුල් පොත සමඟ සසඳා verified=1 කළ යුතුය."""
import sqlite3, sys, json, requests

PROMPT = """You are extracting astrology rules from a KP (Krishnamurti Paddhati) textbook page.
Return ONLY a JSON list. Each item: {"topic": str, "rule": str, "houses": [int], "planets": [str]}.
Copy the rule faithfully from the text; do NOT add anything not on the page. If no rule, return [].

PAGE:
"""
con = sqlite3.connect("kp.db")
book_id = int(sys.argv[1])
pages = con.execute("SELECT page_no, text FROM pages WHERE book_id=? AND needs_review=0 "
                    "AND page_no NOT IN (SELECT page_no FROM rules WHERE book_id=?)", (book_id, book_id)).fetchall()
for page_no, text in pages:
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5:7b", "prompt": PROMPT + text[:6000], "stream": False, "format": "json"}, timeout=300)
    try:
        data = json.loads(r.json()["response"])
        items = data if isinstance(data, list) else data.get("rules", [])
    except Exception:
        continue
    for it in items:
        con.execute("INSERT INTO rules(book_id,page_no,topic,rule_text,houses,planets) VALUES (?,?,?,?,?,?)",
                    (book_id, page_no, it.get("topic"), it.get("rule"),
                     json.dumps(it.get("houses")), json.dumps(it.get("planets"))))
    con.commit()
    print("page", page_no, "rules", len(items))
