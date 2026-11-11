"""සුරකින ලද පොත් තුළ සෙවීම (පිටු අංකය සමඟ).  python search.py "7th cusp sub lord marriage" """
import sqlite3, sys
con = sqlite3.connect("kp.db")
q = sys.argv[1]
sql = """SELECT b.title, p.page_no, snippet(pages_fts, 0, '[', ']', ' … ', 20)
         FROM pages_fts JOIN pages p ON p.id = pages_fts.rowid
         JOIN books b ON b.id = p.book_id
         WHERE pages_fts MATCH ? ORDER BY rank LIMIT 10"""
for title, page, snip in con.execute(sql, (q,)):
    print(f"{title} - පිටුව {page}\n   {snip}\n")
