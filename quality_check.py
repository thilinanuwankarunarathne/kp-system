"""ingest කළ පිටු වල ගුණාත්මකභාවය පරීක්ෂාව.  ධාවනය: python quality_check.py"""
import sqlite3, re

con = sqlite3.connect("kp.db")
BAD = re.compile("[\ufffd\ue000-\uf8ff]")     # වැරදි/පෞද්ගලික-භාවිත අකුරු
LIG = re.compile("[\ufb00-\ufb06]")             # ﬁ ﬂ වැනි ligature

books = con.execute("SELECT id, title FROM books").fetchall()
for bid, title in books:
    pages = con.execute("SELECT page_no, text FROM pages WHERE book_id=?", (bid,)).fetchall()
    short, bad, lig, table, dups = [], [], [], [], []
    seen = {}
    for no, text in pages:
        n = len(text) or 1
        if n < 200: short.append(no)
        if BAD.search(text): bad.append(no)
        if LIG.search(text): lig.append(no)
        digits = sum(c.isdigit() for c in text)
        if digits / n > 0.35: table.append(no)       # අංක බහුල = වගු පිටු
        key = text[:300]
        if len(key) > 100 and key in seen: dups.append(no)
        seen.setdefault(key, no)
    avg = sum(len(t) for _, t in pages) // max(len(pages), 1)
    print(f"\n=== {title} ===")
    print(f"පිටු {len(pages)} | සාමාන්‍ය අකුරු/පිටුව {avg}")
    for label, lst in [("අකුරු 200ට අඩු", short), ("වැරදි සලකුණු (�)", bad),
                       ("ligature (ﬁ ﬂ)", lig), ("අංක බහුල වගු පිටු", table), ("අනුපිටපත් පිටු", dups)]:
        if lst:
            print(f"  {label}: {len(lst)}  උදා: {lst[:8]}")