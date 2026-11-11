# """KP Database UI (Streamlit) - Sinhala / English.   Run:  streamlit run app.py"""
# import os, sqlite3
# import pandas as pd
# import streamlit as st
# import setup_db, ingest_pdf
# import i18n, i18n_extra
# from i18n import T, sn
# import kp_ui
#
# BASE = os.path.dirname(os.path.abspath(__file__))
# os.chdir(BASE)
# os.makedirs("books", exist_ok=True)
#
# st.set_page_config(page_title="KP Database", layout="wide")
#
#
# def get_con():
#     con = sqlite3.connect("kp.db")
#     con.executescript(setup_db.SCHEMA)
#     if con.execute("SELECT COUNT(*) FROM sublords").fetchone()[0] == 0:
#         con.executemany("INSERT INTO sublords(sign,sign_lord,nakshatra,star_lord,sub_lord,start_deg,"
#                         "end_deg,start_dms,end_dms) VALUES (?,?,?,?,?,?,?,?,?)", setup_db.build_sublords())
#         con.commit()
#     return con
#
#
# con = get_con()
#
# # ---------- language switch (whole UI + reports follow this)
# if "lang" not in st.session_state:
#     st.session_state["lang"] = "si"
# st.sidebar.radio("Language / භාෂාව", ["si", "en"], key="lang", horizontal=True,
#                  format_func=lambda x: "සිංහල" if x == "si" else "English")
#
# PAGES = ["horo", "books", "upload", "search", "review", "sub"]
# page = st.sidebar.radio(T("menu"), PAGES, format_func=lambda k: T("m_" + k), key="page")
#
# if page == "horo":
#     kp_ui.render(con)
#
# elif page == "books":
#     df = pd.read_sql("""SELECT b.id, b.title, b.total_pages, COUNT(p.id) AS saved_pages,
#                         SUM(p.needs_review) AS needs_review, SUM(p.method='ocr') AS ocr_pages
#                         FROM books b LEFT JOIN pages p ON p.book_id=b.id GROUP BY b.id""", con)
#     st.dataframe(df, use_container_width=True)
#
# elif page == "upload":
#     up = st.file_uploader(T("upload_pdf"), type="pdf")
#     title = st.text_input(T("book_title"))
#     if up and title and st.button(T("ingest_btn")):
#         path = os.path.join("books", up.name)
#         with open(path, "wb") as f:
#             f.write(up.getbuffer())
#         with st.spinner(T("reading_pages")):
#             ingest_pdf.main(path, title)
#         st.success(T("done_books"))
#
# elif page == "search":
#     q = st.text_input(T("search_words"), placeholder="7th cusp sub lord marriage")
#     if q:
#         try:
#             rows = con.execute("""SELECT b.title, p.page_no, snippet(pages_fts,0,'**','**',' … ',30), p.text
#                 FROM pages_fts JOIN pages p ON p.id=pages_fts.rowid JOIN books b ON b.id=p.book_id
#                 WHERE pages_fts MATCH ? ORDER BY rank LIMIT 20""", (q,)).fetchall()
#         except sqlite3.OperationalError as e:
#             rows = []; st.error(T("search_err", e=e))
#         st.caption(T("results", n=len(rows)))
#         for title, pno, snip, full in rows:
#             with st.expander(f"{title} — {T('page')} {pno}"):
#                 st.markdown(snip)
#                 st.text(full)
#
# elif page == "review":
#     rows = con.execute("""SELECT p.id, b.title, p.page_no, p.text FROM pages p JOIN books b ON b.id=p.book_id
#                           WHERE p.needs_review=1 LIMIT 50""").fetchall()
#     st.caption(T("review_caption", n=len(rows)))
#     for pid, title, pno, text in rows:
#         with st.expander(f"{title} — {T('page')} {pno}"):
#             new = st.text_area("text", text, key=f"t{pid}", height=200)
#             if st.button(T("save"), key=f"s{pid}"):
#                 con.execute("INSERT INTO pages_fts(pages_fts,rowid,text) VALUES('delete',?,?)", (pid, text))
#                 con.execute("UPDATE pages SET text=?, char_count=?, needs_review=0 WHERE id=?", (new, len(new), pid))
#                 con.execute("INSERT INTO pages_fts(rowid,text) VALUES (?,?)", (pid, new))
#                 con.commit(); st.rerun()
#
# else:
#     df = pd.read_sql("SELECT id, sign, nakshatra, star_lord, sub_lord, start_dms, end_dms FROM sublords", con)
#     c1, c2 = st.columns(2)
#     ALL = "__all__"
#     sign = c1.selectbox(T("sign_filter"), [ALL] + sorted(df.sign.unique()),
#                         format_func=lambda x: T("all") if x == ALL else sn(x))
#     lord = c2.selectbox(T("sublord_filter"), [ALL] + sorted(df.sub_lord.unique()),
#                         format_func=lambda x: T("all") if x == ALL else i18n.pn(x))
#     if sign != ALL: df = df[df.sign == sign]
#     if lord != ALL: df = df[df.sub_lord == lord]
#     if i18n.L() == "si":
#         df = df.assign(sign=df.sign.map(i18n.sn), nakshatra=df.nakshatra.map(i18n.nn),
#                        star_lord=df.star_lord.map(i18n.pn), sub_lord=df.sub_lord.map(i18n.pn))
#     st.dataframe(df, use_container_width=True, hide_index=True)

"""KP Database UI (Streamlit) - Sinhala / English.   Run:  streamlit run app.py"""
import os, sqlite3
import pandas as pd
import streamlit as st
import setup_db, ingest_pdf
import i18n, i18n_extra
from i18n import T, sn
import kp_ui
import kp_report as rep
import fitz  # PyMuPDF (PDF කියවීම සඳහා)

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
os.makedirs("books", exist_ok=True)

st.set_page_config(page_title="KP Database", layout="wide")


def get_con():
    con = sqlite3.connect("kp.db")
    con.executescript(setup_db.SCHEMA)
    if con.execute("SELECT COUNT(*) FROM sublords").fetchone()[0] == 0:
        con.executemany("INSERT INTO sublords(sign,sign_lord,nakshatra,star_lord,sub_lord,start_deg,"
                        "end_deg,start_dms,end_dms) VALUES (?,?,?,?,?,?,?,?,?)", setup_db.build_sublords())
        con.commit()
    return con


con = get_con()

# ---------- language switch (whole UI + reports follow this)
if "lang" not in st.session_state:
    st.session_state["lang"] = "si"
st.sidebar.radio("Language / භාෂාව", ["si", "en"], key="lang", horizontal=True,
                 format_func=lambda x: "සිංහල" if x == "si" else "English")

# නව මෙනු අයිතමය සඳහා පරිවර්තන (i18n.TR වෙත එක් කිරීම)
if "m_pdf_analysis" not in i18n.TR:
    i18n.TR["m_pdf_analysis"] = {"en": "📄 AstroSage PDF Analysis", "si": "📄 AstroSage PDF විශ්ලේෂණය"}

PAGES = ["horo", "books", "upload", "search", "review", "sub", "pdf_analysis"]
page = st.sidebar.radio(T("menu"), PAGES, format_func=lambda k: T("m_" + k), key="page")

# PDF වලින් අකුරු උපුටා ගන්නා function එක
def parse_astrosage_pdf(pdf_buffer):
    """Uploaded PDF ගොනුවෙන් සියලුම Text දත්ත උපුටා ගැනීම"""
    doc = fitz.open(stream=pdf_buffer.read(), filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    return text

if page == "horo":
    kp_ui.render(con)

elif page == "books":
    df = pd.read_sql("""SELECT b.id, b.title, b.total_pages, COUNT(p.id) AS saved_pages,
                        SUM(p.needs_review) AS needs_review, SUM(p.method='ocr') AS ocr_pages
                        FROM books b LEFT JOIN pages p ON p.book_id=b.id GROUP BY b.id""", con)
    st.dataframe(df, use_container_width=True)

elif page == "upload":
    up = st.file_uploader(T("upload_pdf"), type="pdf")
    title = st.text_input(T("book_title"))
    if up and title and st.button(T("ingest_btn")):
        path = os.path.join("books", up.name)
        with open(path, "wb") as f:
            f.write(up.getbuffer())
        with st.spinner(T("reading_pages")):
            ingest_pdf.main(path, title)
        st.success(T("done_books"))

elif page == "search":
    q = st.text_input(T("search_words"), placeholder="7th cusp sub lord marriage")
    if q:
        try:
            rows = con.execute("""SELECT b.title, p.page_no, snippet(pages_fts,0,'**','**',' … ',30), p.text
                FROM pages_fts JOIN pages p ON p.id=pages_fts.rowid JOIN books b ON b.id=p.book_id
                WHERE pages_fts MATCH ? ORDER BY rank LIMIT 20""", (q,)).fetchall()
        except sqlite3.OperationalError as e:
            rows = []; st.error(T("search_err", e=e))
        st.caption(T("results", n=len(rows)))
        for title, pno, snip, full in rows:
            with st.expander(f"{title} — {T('page')} {pno}"):
                st.markdown(snip)
                st.text(full)

elif page == "review":
    rows = con.execute("""SELECT p.id, b.title, p.page_no, p.text FROM pages p JOIN books b ON b.id=p.book_id
                          WHERE p.needs_review=1 LIMIT 50""").fetchall()
    st.caption(T("review_caption", n=len(rows)))
    for pid, title, pno, text in rows:
        with st.expander(f"{title} — {T('page')} {pno}"):
            new = st.text_area("text", text, key=f"t{pid}", height=200)
            if st.button(T("save"), key=f"s{pid}"):
                con.execute("INSERT INTO pages_fts(pages_fts,rowid,text) VALUES('delete',?,?)", (pid, text))
                con.execute("UPDATE pages SET text=?, char_count=?, needs_review=0 WHERE id=?", (new, len(new), pid))
                con.execute("INSERT INTO pages_fts(rowid,text) VALUES (?,?)", (pid, new))
                con.commit(); st.rerun()

# ----------------- නවතම AstroSage PDF විශ්ලේෂණ කොටස -----------------
elif page == "pdf_analysis":
    st.header(T("m_pdf_analysis"))

    if st.session_state["lang"] == "si":
        st.info("AstroSage හෝ වෙනත් මෘදුකාංගයකින් ලබාගත් දත්ත සහිත KP PDF වාර්තාවක් මෙහි Upload කරන්න.")
        pdf_label = "PDF කේන්දරය තෝරන්න"
        btn_label = "✨ ජීවිත මාර්ගෝපදේශය නිර්මාණය කරන්න"
        loading_text = "PDF දත්ත කියවමින් සහ AI වාර්තාව සකසමින්... (මෙයට තත්පර කිහිපයක් ගතවනු ඇත)"
        success_text = "සාර්ථකයි! ඔබේ සවිස්තරාත්මක වාර්තාව පහතින් කියවන්න."
        dl_label = "⬇️ AI වාර්තාව බාගන්න (.md ගොනුවක් ලෙස)"
    else:
        st.info("Upload a KP PDF report from AstroSage or similar software here.")
        pdf_label = "Select PDF Horoscope"
        btn_label = "✨ Generate Life Guide"
        loading_text = "Reading PDF data and generating AI report... (This may take a few seconds)"
        success_text = "Success! Read your detailed report below."
        dl_label = "⬇️ Download AI Report (as .md file)"

    pdf_file = st.file_uploader(pdf_label, type="pdf")
    gkey = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API Key")

    if pdf_file and gkey and st.button(btn_label):
        with st.spinner(loading_text):
            try:
                # 1. PDF එකෙන් දත්ත (Facts) ලබා ගැනීම
                raw_facts = parse_astrosage_pdf(pdf_file)

                # 2. Database එකෙන් නීති (Rules/Excerpts) ලබා ගැනීම
                excerpts = rep.book_excerpts(con, lang_unused=st.session_state["lang"], n=3)

                # 3. Gemini AI වෙත යවා සවිස්තරාත්මක වාර්තාව ලබා ගැනීම
                report_md = rep.gemini_text(
                    facts_md=raw_facts,
                    excerpts=excerpts,
                    lang=st.session_state["lang"],
                    key=gkey,
                    model="gemini-3.1-flash-lite"
                )

                st.success(success_text)

                # වාර්තාව තිරයේ පෙන්වීම
                st.markdown(report_md)

                # Markdown ගොනුවක් ලෙස බාගත කිරීමට
                st.download_button(
                    label=dl_label,
                    data=report_md,
                    file_name="KP_Life_Guide_from_PDF.pdf",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Error / දෝෂයක් මතු විය: {e}")

else:
    df = pd.read_sql("SELECT id, sign, nakshatra, star_lord, sub_lord, start_dms, end_dms FROM sublords", con)
    c1, c2 = st.columns(2)
    ALL = "__all__"
    sign = c1.selectbox(T("sign_filter"), [ALL] + sorted(df.sign.unique()),
                        format_func=lambda x: T("all") if x == ALL else sn(x))
    lord = c2.selectbox(T("sublord_filter"), [ALL] + sorted(df.sub_lord.unique()),
                        format_func=lambda x: T("all") if x == ALL else i18n.pn(x))
    if sign != ALL: df = df[df.sign == sign]
    if lord != ALL: df = df[df.sub_lord == lord]
    if i18n.L() == "si":
        df = df.assign(sign=df.sign.map(i18n.sn), nakshatra=df.nakshatra.map(i18n.nn),
                       star_lord=df.star_lord.map(i18n.pn), sub_lord=df.sub_lord.map(i18n.pn))
    st.dataframe(df, use_container_width=True, hide_index=True)