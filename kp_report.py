"""KP report: builds the analysis (Sinhala/English), exports PDF/HTML, optional Gemini writer.
Blocks = list of ("title",txt) ("h1",txt) ("h2",txt) ("p",txt) ("ul",[txt..]) ("table",header,rows)
Needs: pip install fpdf2 uharfbuzz requests"""
import glob, html, os, re, sqlite3
from datetime import timedelta
import kp_engine as kp
import i18n
from i18n_extra import R, HOUSE_MEANING

HERE = os.path.dirname(os.path.abspath(__file__))
ICON = {"Strong": "🟢", "Moderate": "🟡", "Medium": "🟡", "Weak": "🔴"}


# ------------------------------------------------------------------ helpers
def _nm(lang):
    si = lang == "si"
    g = lambda d: (lambda x: d.get(x, x) if si else x)
    return g(i18n.PLANET_SI), g(i18n.SIGN_SI), g(i18n.NAK_SI)


def _topic(k, lang):
    return i18n.TOPIC_SI[k] if lang == "si" else i18n.TOPIC_EN[k]


def fmt(d):
    return d.strftime("%Y-%m-%d")


def book_refs(con, t):
    q = " OR ".join(f'"{w}"' for w in t["kw"])
    try:
        pages = con.execute("""SELECT b.title, p.page_no, snippet(pages_fts,0,'**','**',' … ',30)
            FROM pages_fts JOIN pages p ON p.id=pages_fts.rowid JOIN books b ON b.id=p.book_id
            WHERE pages_fts MATCH ? ORDER BY rank LIMIT 8""", (q,)).fetchall()
    except sqlite3.OperationalError:
        pages = []
    try:
        rules = con.execute("""SELECT b.title, r.page_no, r.rule_text, r.verified FROM rules r
            JOIN books b ON b.id=r.book_id WHERE r.topic LIKE ? ORDER BY r.verified DESC LIMIT 10""",
                            (f"%{t['kw'][0]}%",)).fetchall()
    except sqlite3.OperationalError:
        rules = []
    return pages, rules


def life_table(chart, rp_set, horizon, lang, now, icons=True):
    pn, _, _ = _nm(lang)
    r = lambda k, **kw: R(k, lang, **kw)
    end = now + timedelta(days=365.25 * horizon)
    ic = (lambda l: ICON[l] + " ") if icons else (lambda l: "")
    hdr = [r("area"), r("cusp"), r("cusp_sub"), r("signifies"), r("promise"), r("next_window")]
    rows = []
    for key, t in kp.TOPICS.items():
        pr = kp.promise(chart, t)
        w = kp.windows(chart, t, now, end, rp_set)
        nxt = next((x for x in w if x["level"] == "Strong"), None) or (w[0] if w else None)
        rows.append([_topic(key, lang), t["cusp"], pn(pr["sub"]), ", ".join(map(str, pr["houses"])),
                     ic(pr["level"]) + r("lvl_" + pr["level"]),
                     (f'{ic(nxt["level"])}{fmt(nxt["start"])} → {fmt(nxt["end"])} ({pn(nxt["md"])}-{pn(nxt["ad"])})'
                      if nxt else "—")])
    return hdr, rows


# ------------------------------------------------------------------ blocks
def facts_blocks(chart, rp, horizon, lang, name="", place="", now=None):
    from datetime import datetime
    now = now or datetime.now()
    end = now + timedelta(days=365.25 * horizon)
    pn, sn, nn = _nm(lang)
    r = lambda k, **kw: R(k, lang, **kw)
    asc, moon = chart["cusps"][0], chart["planets"]["Moon"]
    plc = i18n.PLACE_SI.get(place, place) if lang == "si" else place
    B = [("title", r("r_title")), ("h1", r("r_basic")),
         ("p", r("r_basic_line", name=name or r("native"), dt=f"{chart['birth']:%Y-%m-%d %H:%M}", place=plc,
                 lat=f"{chart['lat']:.4f}", lon=f"{chart['lon']:.4f}", tz=chart["tz"])),
         ("p", r("r_asc_line", lagna=sn(asc["sign"]), star=pn(asc["star"]), sub=pn(asc["sub"]),
                 msign=sn(moon["sign"]), nak=nn(moon["nakshatra"]), ay=f"{chart['ayanamsa']:.4f}")),
         ("h1", r("r_method_h")), ("p", r("r_method"))]

    B += [("h1", r("r_chart_h")),
          ("table", [r("c_planet"), r("c_pos"), r("c_nak"), r("c_star"), r("c_sub"), r("c_subsub"), r("c_house"), r("c_retro")],
           [[pn(p), f'{kp.dms(d["lon"])} {sn(d["sign"])}', nn(d["nakshatra"]), pn(d["star"]), pn(d["sub"]),
             pn(d["subsub"]), d["house"], r("c_retro") if d["retro"] else ""] for p, d in chart["planets"].items()]),
          ("h1", r("r_cusp_h")),
          ("table", [r("c_house"), r("c_pos"), r("c_signlord"), r("c_star"), r("c_sub"), r("c_subsub")],
           [[c["house"], f'{kp.dms(c["lon"])} {sn(c["sign"])}', pn(c["sign_lord"]), pn(c["star"]), pn(c["sub"]),
             pn(c["subsub"])] for c in chart["cusps"]]),
          ("h1", r("r_sig_h")), ("p", r("sig_caption")),
          ("table", [r("c_planet"), "L1", "L2", "L3", "L4", r("all_houses")],
           [[pn(p), ",".join(map(str, s["levels"][0])), ",".join(map(str, s["levels"][1])),
             ",".join(map(str, s["levels"][2])), ",".join(map(str, s["levels"][3])),
             ", ".join(map(str, s["houses"]))] for p, s in chart["sig"].items()])]

    B.append(("h1", r("r_dasha_h")))
    cur = kp.current_period(chart, now)
    if cur:
        pr = next((x for x in kp.pratyantars(cur) if x["start"] <= now < x["end"]), None)
        B.append(("p", r("r_dasha_now", md=pn(cur["md"]), ad=pn(cur["ad"]), pd=pn(pr["lord"]) if pr else "-",
                         a=fmt(cur["start"]), b=fmt(cur["end"]))))
    B.append(("table", [r("md"), r("ad"), r("from"), r("to"), r("md_sig"), r("ad_sig")],
              [[pn(p["md"]), pn(p["ad"]), fmt(p["start"]), fmt(p["end"]),
                ", ".join(map(str, chart["sig"][p["md"]]["houses"])), ", ".join(map(str, chart["sig"][p["ad"]]["houses"]))]
               for p in chart["dasha"] if p["end"] >= now and p["start"] <= end][:40]))

    rp_set = set(rp.values())
    hdr, rows = life_table(chart, rp_set, horizon, lang, now, icons=False)
    B += [("h1", r("r_summary_h")), ("table", hdr, rows),
          ("h1", r("r_rp_h")),
          ("table", [r("rp_source"), r("c_planet")], [[i18n.RP_SI.get(k, k) if lang == "si" else k, pn(v)] for k, v in rp.items()])]
    return B


def topic_blocks(chart, rp, horizon, lang, con=None, now=None):
    from datetime import datetime
    now = now or datetime.now()
    end = now + timedelta(days=365.25 * horizon)
    pn, _, _ = _nm(lang)
    r = lambda k, **kw: R(k, lang, **kw)
    rp_set = set(rp.values())
    cur = kp.current_period(chart, now)
    hm = HOUSE_MEANING[lang]
    B = [("h1", r("r_detail_h"))]
    for key, t in kp.TOPICS.items():
        pr = kp.promise(chart, t)
        w = kp.windows(chart, t, now, end, rp_set)
        none = r("none")
        B.append(("h2", f"{_topic(key, lang)} - {r('lvl_' + pr['level'])}"))
        B.append(("p", r("r_topic_intro", n=t["cusp"], topic=_topic(key, lang), sub=pn(pr["sub"]),
                         star=pn(pr["star"]), h=", ".join(map(str, pr["houses"])))))
        B.append(("p", r("r_fav", need=t["fav"], m=pr["fav"] or none)))
        B.append(("p", r("r_deny", need=t["deny"], m=pr["deny"] or none)))
        B.append(("p", r("r_hm", t="; ".join(f"{h} = {hm[h - 1]}" for h in sorted(set(t["fav"] + t["deny"]))))))
        B.append(("p", r("r_verdict_" + pr["level"])))
        B.append(("p", r("r_windows_h", y=horizon) + ":"))
        if w:
            top = sorted(w, key=lambda x: (x["level"] != "Strong", x["start"]))[:6]
            B.append(("ul", [r("r_window_item", lvl=r("lvl_" + x["level"]), a=fmt(x["start"]), b=fmt(x["end"]),
                               md=pn(x["md"]), ad=pn(x["ad"]),
                               rp=(r("r_rp_suffix", x=", ".join(pn(y) for y in x["rp"])) if x["rp"] else ""))
                             for x in top]))
        else:
            B.append(("p", r("r_no_windows")))
        if cur:
            inw = any(x["md"] == cur["md"] and x["ad"] == cur["ad"] for x in w)
            B.append(("p", r("r_now_in" if inw else "r_now_out", md=pn(cur["md"]), ad=pn(cur["ad"]))))
        if con is not None:
            pages, rules = book_refs(con, t)
            items = [f'{"[OK] " if ver else "[?] "}{rule} - {bt}, p.{pno}' for bt, pno, rule, ver in rules[:4]]
            items += [f"{bt}, p.{pno}" for bt, pno, _ in pages[:4]]
            B.append(("p", r("r_book_h") + ":"))
            B.append(("ul", items) if items else ("p", r("r_no_book")))
    B.append(("p", r("r_disc")))
    return B


def book_excerpts(con, lang_unused=None, n=2, maxc=350):
    """English book snippets per topic - extra context for Gemini."""
    out = []
    for key, t in kp.TOPICS.items():
        pages, _ = book_refs(con, t)
        for bt, pno, snip in pages[:n]:
            out.append(f"[{key}] {bt}, p.{pno}: " + re.sub(r"\s+", " ", snip.replace("**", ""))[:maxc])
    return "\n".join(out)


# ------------------------------------------------------------------ markdown <-> blocks
def blocks_to_md(blocks):
    L = []
    for b in blocks:
        k = b[0]
        if k == "title": L.append(f"# {b[1]}\n")
        elif k == "h1": L.append(f"\n## {b[1]}\n")
        elif k == "h2": L.append(f"\n### {b[1]}\n")
        elif k == "p": L.append(b[1] + "\n")
        elif k == "ul": L += [f"- {x}" for x in b[1]] + [""]
        elif k == "table":
            L.append(" | ".join(map(str, b[1])))
            L += [" | ".join(map(str, row)) for row in b[2]] + [""]
    return "\n".join(L)


def blocks_to_streamlit_md(blocks):
    L = []
    for b in blocks:
        k = b[0]
        if k == "title": L.append(f"# {b[1]}")
        elif k == "h1": L.append(f"## {b[1]}")
        elif k == "h2": L.append(f"### {b[1]}")
        elif k == "p": L.append(b[1])
        elif k == "ul": L.append("\n".join(f"- {x}" for x in b[1]))
        elif k == "table":
            L.append("| " + " | ".join(map(str, b[1])) + " |\n|" + "---|" * len(b[1]) + "\n" +
                     "\n".join("| " + " | ".join(str(c) for c in row) + " |" for row in b[2]))
    return "\n\n".join(L)


def parse_md(text):
    text = re.sub(r"```\w*", "", text).replace("**", "").replace("__", "")
    B, ul = [], []
    def flush():
        nonlocal ul
        if ul: B.append(("ul", ul)); ul = []
    for line in text.splitlines():
        s = line.strip()
        if not s: flush(); continue
        m = re.match(r"^(#{1,6})\s+(.*)", s)
        if m:
            flush(); n = len(m.group(1))
            B.append(("title" if n == 1 and not B else "h1" if n <= 2 else "h2", m.group(2).strip())); continue
        m = re.match(r"^[-*•]\s+(.*)", s)
        if m: ul.append(m.group(1)); continue
        flush()
        if re.match(r"^\|?[\s:-]+\|[\s|:-]*$", s): continue
        B.append(("p", s.strip("|").replace(" | ", "  ·  ")))
    flush()
    return B


# # kp_report.py හි මෙම function එක යාවත්කාලීන කරන්න
# def gemini_text(facts_md, excerpts, lang, key, model="gemini-3.5-flash-lite"):
#     import requests
#     langname = "Sinhala (සිංහල)" if lang == "si" else "English"
#
#     system = (
#         "You are a master KP astrologer and an empathetic life guide. Your task is to write an EXTREMELY DETAILED, "
#         "COMPREHENSIVE, AND IN-DEPTH life report. The final output MUST be equivalent to a 5 to 7-page printed book "
#         "(at least 2500 to 3500 words). Do not summarize; expand deeply on every point.\n\n"
#
#         "CRITICAL RULES:\n"
#         "1. NO JARGON: Translate all astrological data (cusps, sub-lords, significators) into plain, engaging human language. "
#         "Do not use raw astro-math terms in the text.\n"
#
#         "2. EXTREME LENGTH & DEPTH: You must write a very long report. Use the following structure and write 3-4 long paragraphs for EACH section:\n"
#         "   - Section 1: Introduction & Deep Personality Analysis (Hidden strengths, weaknesses, mindset).\n"
#         "   - Section 2: Past Validations (Deduce and describe 4 to 5 highly specific micro-level past events or emotional phases they have likely experienced to build trust).\n"
#         "   - Section 3: Career, Business & Financial Matrix (Micro-level scenarios: e.g., 'You will likely earn through tech-investments, hidden sources, or sudden property gains', outline workplace dynamics).\n"
#         "   - Section 4: Love, Marriage & Family Life (Deep psychological breakdown of their relationships, partner's nature, and family dynamics).\n"
#         "   - Section 5: Health, Vitality & Well-being (Preventative care based on planetary alignments).\n"
#         "   - Section 6: Upcoming 3-5 Years In-Depth (Month-by-month or phase-by-phase breakdown based on current/upcoming Dasha & Bhukti).\n"
#         "   - Section 7: Psychological Guidance & Constructive Advice (How to navigate challenges).\n\n"
#
#         "3. MICRO-LEVEL SCENARIOS: Provide ultra-specific examples for every prediction. Instead of 'financial gains', describe 'sudden income from an old investment or a female relative'.\n"
#         "4. TONE & SAFETY: Be highly premium, warm, and professional. NEVER predict death, fatal accidents, or incurable diseases. Frame challenges as areas for growth.\n"
#         f"5. LANGUAGE: Write the ENTIRE report fluently in {langname}. Use rich, expressive storytelling language.\n"
#         "6. FORMAT: Use ONLY markdown headings (#, ##, ###), bold text (**text**), and bullets (-). No tables, no HTML."
#     )
#
#     user = (
#         "Generate a massively detailed, 5+ page micro-level life reading based on these astrology facts.\n\n"
#         "ASTROLOGY FACTS (Extract deeply from Dasha balances, Cusps, and Planets):\n" + facts_md +
#         "\n\nKP REFERENCE GUIDELINES (Use to shape the advice):\n" + excerpts
#     )
#
#     # maxOutputTokens 8192 (උපරිම අගය) ලෙස තබා ඇත, එවිට දිගු වාර්තාවක් ලබාගත හැක.
#     resp = requests.post(
#         f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
#         headers={"x-goog-api-key": key, "Content-Type": "application/json"},
#         json={"system_instruction": {"parts": [{"text": system}]},
#               "contents": [{"role": "user", "parts": [{"text": user}]}],
#               "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192}}, timeout=240)
#
#     if resp.status_code != 200:
#         raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
#     data = resp.json()
#     try:
#         return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
#     except (KeyError, IndexError):
#         raise RuntimeError("empty response: " + str(data)[:300])

def gemini_text(facts_md, excerpts, lang, key, model="gemini-3.5-flash-lite"):
    import requests
    langname = "Sinhala (සිංහල)" if lang == "si" else "English"

    system = (
        "You are a master KP astrologer and an empathetic life guide. Your task is to write an EXTREMELY DETAILED, "
        "COMPREHENSIVE, AND IN-DEPTH life report. The final output MUST be equivalent to a 5 to 7-page printed book "
        "(at least 2500 to 3500 words). Do not summarize; expand deeply on every point.\n\n"

        "CRITICAL RULES:\n"
        "1. NO JARGON: Translate all astrological data (cusps, sub-lords, significators) into plain, engaging human language. "
        "Do not use raw astro-math terms in the text.\n"

        "2. EXTREME LENGTH, DEPTH & SPECIFICITY: You must write a very long report. Use the following structure and write 3-4 long paragraphs for EACH section. You MUST deeply analyze and answer the specific life aspects requested below:\n"
        "   - Section 1: Introduction, Gender & Deep Personality Analysis (Analyze the planetary energies to deduce the native's gender traits/inclinations. Discuss hidden strengths, weaknesses, and core mindset).\n"
        "   - Section 2: Educational Stream & Intellect (Deep dive into their education based on 4th, 5th, and 9th cusps. Explicitly state WHICH STREAM they studied or are suited for—e.g., Tech, Medicine, Arts, Commerce, IT—based on planets like Mercury/Jupiter/Mars).\n"
        "   - Section 3: Siblings & Family Dynamics (Analyze the 3rd and 11th cusps to deduce the likely number of siblings. Explicitly state how many BROTHERS and SISTERS they might have, and describe the relationship with them).\n"
        "   - Section 4: Past Validations (Deduce and describe 4 to 5 highly specific micro-level past events or emotional phases they have likely experienced to build trust).\n"
        "   - Section 5: Career, Business & Financial Matrix (Explicitly analyze the 2nd, 6th, 7th, and 10th cusps to state whether they are destined for a JOB or BUSINESS. Pinpoint the exact professional field/industry, wealth potential, and workplace dynamics).\n"
        "   - Section 6: Love, Marriage & Partner Profile (Deep psychological breakdown. Who is the marriage partner? Explicitly describe the partner's physical traits, profession, financial status, and nature in deep detail based on the 7th cusp sub-lord).\n"
        "   - Section 7: Health, Vitality & Well-being (Preventative care based on 1st, 6th, and 8th house planetary alignments).\n"
        "   - Section 8: Upcoming 3-5 Years In-Depth (Month-by-month or phase-by-phase breakdown based on current/upcoming Dasha & Bhukti).\n"
        "   - Section 9: Psychological Guidance & Constructive Advice (How to navigate challenges and maximize potential).\n\n"

        "3. MICRO-LEVEL SCENARIOS: Provide ultra-specific examples for every prediction. Instead of 'financial gains', describe 'sudden income from an old tech investment or a female relative'.\n"
        "4. TONE & SAFETY: Be highly premium, warm, and professional. NEVER predict death, fatal accidents, or incurable diseases. Frame challenges as areas for growth.\n"
        f"5. LANGUAGE: Write the ENTIRE report fluently in {langname}. Use rich, expressive storytelling language.\n"
        "6. FORMAT: Use ONLY markdown headings (#, ##, ###), bold text (**text**), and bullets (-). No tables, no HTML."
    )

    user = (
        "Generate a massively detailed, 5+ page micro-level life reading based on these astrology facts.\n\n"
        "ASTROLOGY FACTS (Extract deeply from Dasha balances, Cusps, and Planets to find education, siblings, career, and partner details):\n" + facts_md +
        "\n\nKP REFERENCE GUIDELINES (Use to shape the advice):\n" + excerpts
    )

    # maxOutputTokens 8192 (උපරිම අගය) ලෙස තබා ඇත, එවිට දිගු වාර්තාවක් ලබාගත හැක.
    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json={"system_instruction": {"parts": [{"text": system}]},
              "contents": [{"role": "user", "parts": [{"text": user}]}],
              "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192}}, timeout=240)

    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    try:
        return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError):
        raise RuntimeError("empty response: " + str(data)[:300])


def make_report(con, chart, rp, horizon, lang, name, place, mode="rules", key=None, model="gemini-2.5-flash"):
    """Returns (blocks, error_or_None)."""
    facts = facts_blocks(chart, rp, horizon, lang, name, place)
    topics = topic_blocks(chart, rp, horizon, lang, con)
    if mode == "gemini" and key:
        try:
            txt = gemini_text(blocks_to_md(facts + topics), book_excerpts(con), lang, key.strip(), model.strip())
            ai = [b for b in parse_md(txt) if b[0] != "title"]
            return facts + [("h1", R("r_ai_h", lang))] + ai + [("p", R("r_disc", lang))], None
        except Exception as e:
            return facts + topics, str(e)
    return facts + topics, None


# ------------------------------------------------------------------ export
def _find(patterns):
    for p in patterns:
        for f in glob.glob(p):
            if os.path.isfile(f):
                return f
    return None


def find_fonts():
    sin = _find([os.path.join(HERE, "fonts", "*Sinhala*.ttf"), os.path.join(HERE, "fonts", "iskpota.ttf"),
                 r"C:\Windows\Fonts\iskpota.ttf", "/usr/share/fonts/truetype/noto/NotoSansSinhala-Regular.ttf",
                 "/usr/share/fonts/truetype/lklug/lklug.ttf", "/usr/share/fonts/**/NotoSansSinhala*.ttf"])
    lat = _find([os.path.join(HERE, "fonts", "DejaVuSans.ttf"), r"C:\Windows\Fonts\arial.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                 "/Library/Fonts/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"])
    return sin, lat


_EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]")


def _clean(s):
    return _EMOJI.sub("", str(s).replace("**", "")).strip()


def render_pdf(blocks, lang):
    from fpdf import FPDF
    sin, lat = find_fonts()
    if lang == "si" and not sin:
        raise RuntimeError(R("rep_nofont", "en"))
    if lang != "si" and not lat:
        raise RuntimeError(R("rep_nolatin", "en"))

    class Pdf(FPDF):
        main = "L"
        def footer(self):
            self.set_y(-12); self.set_font(self.main, size=8)
            self.cell(0, 6, str(self.page_no()), align="C")

    pdf = Pdf(format="A4", unit="mm")
    pdf.set_auto_page_break(True, 15); pdf.set_margins(15, 15, 15)
    if lat: pdf.add_font("L", "", lat)
    if lang == "si":
        pdf.add_font("S", "", sin); pdf.main = "S"
        if lat: pdf.set_fallback_fonts(["L"])
        pdf.set_text_shaping(True)          # needs: pip install uharfbuzz (correct Sinhala conjuncts)
    main = pdf.main
    pdf.add_page()
    nl = dict(new_x="LMARGIN", new_y="NEXT")
    for b in blocks:
        k = b[0]
        if k == "title":
            pdf.set_font(main, size=20); pdf.multi_cell(0, 10, _clean(b[1]), **nl); pdf.ln(2)
        elif k == "h1":
            pdf.ln(3); pdf.set_font(main, size=15); pdf.multi_cell(0, 8, _clean(b[1]), **nl); pdf.ln(1)
        elif k == "h2":
            pdf.ln(2); pdf.set_font(main, size=12.5); pdf.multi_cell(0, 7, _clean(b[1]), **nl)
        elif k == "p":
            pdf.set_font(main, size=10.5); pdf.multi_cell(0, 5.8, _clean(b[1]), **nl); pdf.ln(1.5)
        elif k == "ul":
            pdf.set_font(main, size=10.5)
            for x in b[1]:
                pdf.multi_cell(0, 5.8, "-  " + _clean(x), **nl)
            pdf.ln(1.5)
        elif k == "table":
            pdf.set_font(main, size=8.5)
            with pdf.table(text_align="LEFT", line_height=5) as t:
                for row in [b[1]] + b[2]:
                    rw = t.row()
                    for c in row:
                        rw.cell(_clean(c))
            pdf.ln(3)
    return bytes(pdf.output())


def render_html(blocks, lang):
    e = lambda s: html.escape(_clean(s))
    out = [f"<!doctype html><html lang='{lang}'><meta charset='utf-8'><title>KP Report</title><style>"
           "body{font-family:'Noto Sans Sinhala','Iskoola Pota','Nirmala UI',Arial,sans-serif;max-width:860px;margin:2em auto;line-height:1.6}"
           "table{border-collapse:collapse;width:100%;font-size:12px;margin:8px 0}td,th{border:1px solid #999;padding:3px 6px;text-align:left}"
           "th{background:#eee}@media print{h1,h2,h3{page-break-after:avoid}table{page-break-inside:auto}}</style><body>"]
    for b in blocks:
        k = b[0]
        if k == "title": out.append(f"<h1>{e(b[1])}</h1>")
        elif k == "h1": out.append(f"<h2>{e(b[1])}</h2>")
        elif k == "h2": out.append(f"<h3>{e(b[1])}</h3>")
        elif k == "p": out.append(f"<p>{e(b[1])}</p>")
        elif k == "ul": out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in b[1]) + "</ul>")
        elif k == "table":
            out.append("<table><tr>" + "".join(f"<th>{e(h)}</th>" for h in b[1]) + "</tr>" +
                       "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in row) + "</tr>" for row in b[2]) + "</table>")
    out.append("</body></html>")
    return "\n".join(out).encode("utf-8")