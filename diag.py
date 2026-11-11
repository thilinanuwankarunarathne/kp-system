import sqlite3, re, collections
con = sqlite3.connect("kp.db")
rows = con.execute("SELECT page_no, text FROM pages WHERE book_id=3").fetchall()
bad = re.compile("[\ufffd\ue000-\uf8ff]")
cnt = collections.Counter(c for _, t in rows for c in bad.findall(t))
for ch, n in cnt.most_common(10): print(hex(ord(ch)), n)
page, text = next((p, t) for p, t in rows if bad.search(t))
m = bad.search(text); print(page, repr(text[max(0,m.start()-60):m.end()+60]))