"""KP database සකස් කිරීම (SQLite). සම්පූර්ණ KP Sub-Lord වගුව (≈249) ගණනය කර ඇතුළත් කරයි.
ධාවනය: python setup_db.py
"""
import sqlite3
from fractions import Fraction

DB = "kp.db"
DASHA = [("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
         ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
              "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
              "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
              "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
              "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus",
              "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS books(
  id INTEGER PRIMARY KEY, title TEXT, filename TEXT, sha256 TEXT UNIQUE, total_pages INTEGER);
CREATE TABLE IF NOT EXISTS pages(
  id INTEGER PRIMARY KEY, book_id INTEGER REFERENCES books(id), page_no INTEGER,
  text TEXT, method TEXT, char_count INTEGER, needs_review INTEGER DEFAULT 0,
  UNIQUE(book_id, page_no));
CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(text, content='pages', content_rowid='id');
CREATE TRIGGER IF NOT EXISTS pages_ai AFTER INSERT ON pages BEGIN
  INSERT INTO pages_fts(rowid, text) VALUES (new.id, new.text); END;
CREATE TABLE IF NOT EXISTS rules(
  id INTEGER PRIMARY KEY, book_id INTEGER, page_no INTEGER, topic TEXT,
  rule_text TEXT, houses TEXT, planets TEXT, verified INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS sublords(
  id INTEGER PRIMARY KEY, sign TEXT, sign_lord TEXT, nakshatra TEXT,
  star_lord TEXT, sub_lord TEXT, start_deg REAL, end_deg REAL, start_dms TEXT, end_dms TEXT);
"""

def dms(arcmin):
    total_sec = round(float(arcmin) * 60)
    d, r = divmod(total_sec, 3600)
    m, s = divmod(r, 60)
    return f"{d % 30:02d}°{m:02d}'{s:02d}\"" if not (total_sec and d % 30 == 0 and m == 0 and s == 0 and d) else f"30°00'00\""

def build_sublords():
    """27 නැකැත් × 9 sub = 243 කොටස්; රාශි සීමා වලින් කැපෙන ඒවා බෙදා (≈249) ලබාගනී."""
    NAK = Fraction(800)      # 13°20' = 800 arcmin
    SIGN = Fraction(1800)    # 30° = 1800 arcmin
    segs = []
    for n in range(27):
        start_idx = n % 9
        pos = n * NAK
        for k in range(9):
            sub, yrs = DASHA[(start_idx + k) % 9]
            length = NAK * yrs / 120
            segs.append([pos, pos + length, n, DASHA[start_idx][0], sub])
            pos += length
    rows = []
    for s, e, n, star, sub in segs:
        cur = s
        while cur < e:
            sign_idx = int(cur // SIGN)
            nxt = min(e, (sign_idx + 1) * SIGN)
            rows.append((SIGNS[sign_idx], SIGN_LORDS[sign_idx], NAKSHATRAS[n], star, sub,
                         float(cur) / 60, float(nxt) / 60, dms(cur), dms(nxt)))
            cur = nxt
    return rows

if __name__ == "__main__":
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    con.execute("DELETE FROM sublords")
    rows = build_sublords()
    con.executemany("INSERT INTO sublords(sign,sign_lord,nakshatra,star_lord,sub_lord,"
                    "start_deg,end_deg,start_dms,end_dms) VALUES (?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    print("Sub-lord rows:", len(rows), "(KP සම්මත වගුව 249)")
    for r in con.execute("SELECT * FROM sublords LIMIT 5"):
        print(r)
    con.close()
