"""PDF පොත් පිටු-පිටුව කියවා SQLite වලට සුරකියි. නැවත ධාවනය කළ හැක (resume).
භාවිතය:  python ingest_pdf.py books/KP_Reader1.pdf "KP Reader 1"
"""
import sys, hashlib, sqlite3, io
import fitz  # PyMuPDF

DB = "kp.db"
MIN_CHARS = 80   # මීට අඩු නම් scan කළ පිටුවක් ලෙස සලකා OCR කරයි

def ocr_page(page):
    try:
        import pytesseract
        from PIL import Image
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(img, lang="eng")
    except Exception as e:
        return ""

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main(path, title):
    con = sqlite3.connect(DB)
    digest = sha256(path)
    doc = fitz.open(path)
    row = con.execute("SELECT id FROM books WHERE sha256=?", (digest,)).fetchone()
    if row:
        book_id = row[0]
    else:
        cur = con.execute("INSERT INTO books(title,filename,sha256,total_pages) VALUES (?,?,?,?)",
                          (title, path, digest, len(doc)))
        book_id = cur.lastrowid
    done = {r[0] for r in con.execute("SELECT page_no FROM pages WHERE book_id=?", (book_id,))}
    for i, page in enumerate(doc, start=1):
        if i in done:
            continue
        text, method = page.get_text("text").strip(), "text"
        if len(text) < MIN_CHARS:
            ocr = ocr_page(page).strip()
            if len(ocr) > len(text):
                text, method = ocr, "ocr"
        review = 1 if len(text) < MIN_CHARS else 0
        con.execute("INSERT INTO pages(book_id,page_no,text,method,char_count,needs_review) "
                    "VALUES (?,?,?,?,?,?)", (book_id, i, text, method, len(text), review))
        if i % 25 == 0:
            con.commit()
            print(f"  පිටු {i}/{len(doc)}")
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM pages WHERE book_id=? AND needs_review=1", (book_id,)).fetchone()[0]
    print(f"අවසන්: {title} | පිටු {len(doc)} | අතින් පරීක්ෂා කළ යුතු පිටු {n}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else sys.argv[1])
