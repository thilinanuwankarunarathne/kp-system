"""KP Horoscope page (Sinhala / English).  Used from app.py:  kp_ui.render(con)"""
from datetime import datetime, date, time, timedelta
import pandas as pd
import streamlit as st
import kp_engine as kp
import kp_report as rep
import i18n, i18n_extra                      # i18n_extra adds the extra texts
from i18n import T, L, pn, sn, nn, place_name, rp_name, topic_name, abbr

PLACES = {
    "Colombo": (6.9271, 79.8612), "Negombo": (7.2083, 79.8358), "Kandy": (7.2906, 80.6337),
    "Galle": (6.0535, 80.2210), "Matara": (5.9549, 80.5550), "Jaffna": (9.6615, 80.0255),
    "Kurunegala": (7.4863, 80.3623), "Anuradhapura": (8.3114, 80.4037),
    "Ratnapura": (6.6828, 80.3992), "Batticaloa": (7.7310, 81.6747),
    "Chennai": (13.0827, 80.2707), "Mumbai": (19.0760, 72.8777), "Delhi": (28.6139, 77.2090),
    "Custom": (7.0, 80.0),
}
ICON = rep.ICON
SI_LAYOUT = [[11, 0, 1, 2], [10, None, None, 3], [9, None, None, 4], [8, 7, 6, 5]]


def ensure_tables(con):
    con.execute("""CREATE TABLE IF NOT EXISTS clients(
        id INTEGER PRIMARY KEY, name TEXT, birth TEXT, tz REAL, lat REAL, lon REAL, place TEXT)""")
    con.commit()


def fmt(d):
    return d.strftime("%Y-%m-%d")


def lvl(x):
    return f'{ICON[x]} {T("lvl_" + x)}'


def place_label(p):
    return T("custom") if p == "Custom" else place_name(p)


def south_indian(chart, title):
    by = {i: [] for i in range(12)}
    for p, d in chart["planets"].items():
        by[int(d["lon"] // 30)].append(abbr(p) + (f'({T("c_retro")})' if d["retro"] and p not in ("Rahu", "Ketu") else ""))
    by[int(chart["cusps"][0]["lon"] // 30)].insert(0, f'<b>{T("asc")}</b>')
    cell = "border:1px solid #888;width:25%;height:80px;vertical-align:top;padding:4px;font-size:13px"
    rows = ""
    for ri, r in enumerate(SI_LAYOUT):
        cells = ""
        for ci, s in enumerate(r):
            if s is None:
                if ri == 1 and ci == 1:
                    cells += (f'<td colspan="2" rowspan="2" style="{cell};text-align:center;vertical-align:middle">'
                              f'<b>{title}</b><br>{T("rasi")}</td>')
            else:
                nm = sn(kp.SIGNS[s]) if L() == "si" else kp.SIGNS[s][:3]
                cells += f'<td style="{cell}"><small style="opacity:.6">{nm}</small><br>{" ".join(by[s])}</td>'
        rows += f"<tr>{cells}</tr>"
    st.markdown(f'<table style="border-collapse:collapse;width:100%;max-width:560px">{rows}</table>',
                unsafe_allow_html=True)


def render(con):
    ensure_tables(con)
    st.title(T("title"))
    with st.expander(T("guide_title"), expanded="chart" not in st.session_state):
        st.markdown(T("guide"))

    # ---------- input
    st.subheader(T("sec_birth"))
    saved = con.execute("SELECT id, name, birth FROM clients ORDER BY id DESC").fetchall()
    if saved:
        sel = st.selectbox(T("load_saved"), ["—"] + [f"{i} · {n} · {b[:10]}" for i, n, b in saved])
        if sel != "—" and st.button(T("load")):
            r = con.execute("SELECT name,birth,tz,lat,lon,place FROM clients WHERE id=?",
                            (int(sel.split(" · ")[0]),)).fetchone()
            bd = datetime.fromisoformat(r[1])
            st.session_state.update(chart=kp.build_chart(bd, r[2], r[3], r[4]), name=r[0], place=r[5],
                                    inputs=(r[1], r[2], r[3], r[4]))
            st.rerun()

    c1, c2, c3 = st.columns(3)
    name = c1.text_input(T("name"), value=st.session_state.get("name", ""))
    dob = c2.date_input(T("dob"), value=date(1990, 1, 1), min_value=date(1900, 1, 1), max_value=date.today())
    tob = c3.time_input(T("tob"), value=time(6, 0), step=60)
    c4, c5, c6, c7 = st.columns(4)
    place = c4.selectbox(T("place"), list(PLACES), format_func=place_label)
    la, lo = PLACES[place]
    lat = c5.number_input(T("lat"), value=la, format="%.4f", key=f"lat_{place}")
    lon = c6.number_input(T("lon"), value=lo, format="%.4f", key=f"lon_{place}")
    tz = c7.number_input(T("tz"), value=5.5, step=0.5)

    b1, b2 = st.columns(2)
    if b1.button(T("calc"), type="primary"):
        bd = datetime.combine(dob, tob)
        st.session_state.update(chart=kp.build_chart(bd, tz, lat, lon), name=name, place=place,
                                inputs=(bd.isoformat(), tz, lat, lon))
        st.session_state.pop("report", None)
    if b2.button(T("save_person")) and "inputs" in st.session_state:
        bd, z, a, o = st.session_state["inputs"]
        con.execute("INSERT INTO clients(name,birth,tz,lat,lon,place) VALUES (?,?,?,?,?,?)",
                    (name or "Unnamed", bd, z, a, o, place))
        con.commit(); st.success(T("saved_ok"))

    chart = st.session_state.get("chart")
    if not chart:
        st.info(T("fill_info"))
        return

    title = st.session_state.get("name") or T("native")
    st.success(T("summary", name=title, dt=f"{chart['birth']:%Y-%m-%d %H:%M}",
                 lagna=sn(chart["cusps"][0]["sign"]), nak=nn(chart["planets"]["Moon"]["nakshatra"]),
                 ay=f"{chart['ayanamsa']:.4f}°"))
    horizon = st.slider(T("look_ahead"), 1, 30, 10)
    now = datetime.now()
    rp = kp.ruling_planets(now, chart["tz"], chart["lat"], chart["lon"])
    rp_set = set(rp.values())

    t_chart, t_sig, t_das, t_life, t_book, t_rp, t_rep = st.tabs(
        [T("tab_chart"), T("tab_sig"), T("tab_dasha"), T("tab_life"), T("tab_book"), T("tab_rp"), T("tab_report")])

    # ---------- chart
    with t_chart:
        south_indian(chart, title)
        st.markdown(f"**{T('planets')}**")
        st.dataframe(pd.DataFrame([{T("c_planet"): pn(p), T("c_pos"): f'{kp.dms(d["lon"])} {sn(d["sign"])}',
                                    T("c_nak"): nn(d["nakshatra"]), T("c_star"): pn(d["star"]),
                                    T("c_sub"): pn(d["sub"]), T("c_subsub"): pn(d["subsub"]),
                                    T("c_house"): d["house"], T("c_retro"): T("c_retro") if d["retro"] else ""}
                                   for p, d in chart["planets"].items()]), hide_index=True, use_container_width=True)
        st.markdown(f"**{T('cusps')}**")
        st.dataframe(pd.DataFrame([{T("c_house"): c["house"], T("c_pos"): f'{kp.dms(c["lon"])} {sn(c["sign"])}',
                                    T("c_signlord"): pn(c["sign_lord"]), T("c_star"): pn(c["star"]),
                                    T("c_sub"): pn(c["sub"]), T("c_subsub"): pn(c["subsub"])}
                                   for c in chart["cusps"]]), hide_index=True, use_container_width=True)

    # ---------- significators
    with t_sig:
        st.caption(T("sig_caption"))
        st.dataframe(pd.DataFrame([{T("c_planet"): pn(p), "L1": ",".join(map(str, s["levels"][0])),
                                    "L2": ",".join(map(str, s["levels"][1])), "L3": ",".join(map(str, s["levels"][2])),
                                    "L4": ",".join(map(str, s["levels"][3])),
                                    T("all_houses"): ", ".join(map(str, s["houses"]))}
                                   for p, s in chart["sig"].items()]), hide_index=True, use_container_width=True)
        st.markdown(f"**{T('house_wise')}**")
        st.dataframe(pd.DataFrame([{T("c_house"): h, T("c_planets"): ", ".join(
            pn(p) for p in kp.PLANETS if h in chart["sig"][p]["houses"])} for h in range(1, 13)]),
            hide_index=True, use_container_width=True)

    # ---------- dasha
    with t_das:
        cur = kp.current_period(chart, now)
        end = now + timedelta(days=365.25 * horizon)
        if cur:
            st.markdown(f"**{T('now')}:** {T('md')} **{pn(cur['md'])}** · {T('ad')} **{pn(cur['ad'])}** "
                        f"({fmt(cur['start'])} → {fmt(cur['end'])})")
            pr = next((x for x in kp.pratyantars(cur) if x["start"] <= now < x["end"]), None)
            if pr:
                st.markdown(f"{T('pd')}: **{pn(pr['lord'])}** ({fmt(pr['start'])} → {fmt(pr['end'])})")
        st.dataframe(pd.DataFrame([{T("md"): pn(p["md"]), T("ad"): pn(p["ad"]), T("from"): fmt(p["start"]),
                                    T("to"): fmt(p["end"]),
                                    T("md_sig"): ", ".join(map(str, chart["sig"][p["md"]]["houses"])),
                                    T("ad_sig"): ", ".join(map(str, chart["sig"][p["ad"]]["houses"]))}
                                   for p in chart["dasha"] if p["end"] >= now and p["start"] <= end]),
                     hide_index=True, use_container_width=True)

    # ---------- life areas
    with t_life:
        st.markdown(f"**{T('overview')}**")
        hdr, rows = rep.life_table(chart, rp_set, horizon, L(), now, icons=True)
        st.dataframe(pd.DataFrame(rows, columns=hdr), hide_index=True, use_container_width=True)
        st.divider()
        key = st.selectbox(T("choose_area"), list(kp.TOPICS), format_func=topic_name)
        t = kp.TOPICS[key]
        pr = kp.promise(chart, t)
        none = T("none")
        st.markdown(f"### {ICON[pr['level']]} {T('promise_h', lvl=T('lvl_' + pr['level']))}")
        st.write(T("cusp_line", n=t["cusp"], sub=pn(pr["sub"]), star=pn(pr["star"]), h=", ".join(map(str, pr["houses"]))))
        st.write(T("fav_line", need=t["fav"], m=pr["fav"] or none))
        st.write(T("deny_line", need=t["deny"], m=pr["deny"] or none))
        w = kp.windows(chart, t, now, now + timedelta(days=365.25 * horizon), rp_set)
        st.markdown(f"### {T('fav_periods')}")
        if pr["level"] == "Weak":
            st.warning(T("weak_warn"))
        if w:
            st.dataframe(pd.DataFrame([{T("strength"): lvl(x["level"]), T("from"): fmt(x["start"]), T("to"): fmt(x["end"]),
                                        T("dasha_bhukti"): f'{pn(x["md"])}-{pn(x["ad"])}',
                                        T("md_match"): x["md_houses"], T("ad_match"): x["ad_houses"],
                                        T("rp_match"): ", ".join(pn(y) for y in x["rp"]) or "—"} for x in w]),
                         hide_index=True, use_container_width=True)
        else:
            st.info(T("no_windows"))

    # ---------- book references
    with t_book:
        bk = st.selectbox(T("topic"), list(kp.TOPICS), format_func=topic_name, key="bk")
        pages, rules = rep.book_refs(con, kp.TOPICS[bk])
        st.markdown(f"**{T('rules_h')}**")
        for title_, pno, rule, ver in rules:
            st.write(f"{'✅' if ver else '⚠️'} {rule}  — *{title_}, {T('page_no')} {pno}*")
        if not rules:
            st.caption(T("no_rules"))
        st.markdown(f"**{T('pages_h')}**")
        for title_, pno, snip in pages:
            with st.expander(f"{title_} — {T('page_no')} {pno}"):
                st.markdown(snip)
        if not pages:
            st.caption(T("no_pages"))

    # ---------- ruling planets
    with t_rp:
        st.caption(T("rp_caption", now=f"{now:%Y-%m-%d %H:%M}"))
        st.dataframe(pd.DataFrame([[rp_name(k), pn(v)] for k, v in rp.items()],
                                  columns=[T("rp_source"), T("c_planet")]), hide_index=True, use_container_width=True)
        st.write(T("rp_combined"), ", ".join(pn(p) for p in sorted(rp_set)))

    # ---------- full report + download
    with t_rep:
        st.write(T("rep_intro"))
        mode = st.radio(T("rep_mode"), ["rules", "gemini"], format_func=lambda m: T("rep_mode_" + m), horizontal=True)
        gkey = gmodel = None
        if mode == "gemini":
            gkey = st.text_input(T("rep_key"), type="password", help=T("rep_key_help"))
            gmodel = st.text_input(T("rep_model"), value="gemini-2.5-flash")
            st.caption(T("rep_key_help"))
        if st.button(T("rep_btn"), type="primary", key="gen_report"):
            if mode == "gemini" and not gkey:
                st.error(T("rep_need_key"))
            else:
                lang = L()
                with st.spinner(T("rep_working")):
                    blocks, gerr = rep.make_report(con, chart, rp, horizon, lang, st.session_state.get("name", ""),
                                                   st.session_state.get("place", ""), mode, gkey, gmodel)
                    pdf, perr = None, None
                    try:
                        pdf = rep.render_pdf(blocks, lang)
                    except Exception as e:
                        perr = str(e)
                    st.session_state["report"] = dict(lang=lang, blocks=blocks, pdf=pdf, perr=perr, gerr=gerr,
                                                      html=rep.render_html(blocks, lang), who=title)
        R_ = st.session_state.get("report")
        if R_:
            if R_["lang"] != L():
                st.warning(T("rep_stale"))
            else:
                if R_["gerr"]:
                    st.warning(T("rep_err_gemini", e=R_["gerr"]))
                st.success(T("rep_ready"))
                d1, d2 = st.columns(2)
                fn = f"KP_{R_['who']}_{R_['lang']}".replace(" ", "_")
                if R_["pdf"]:
                    d1.download_button(T("rep_dl_pdf"), R_["pdf"], file_name=fn + ".pdf", mime="application/pdf")
                else:
                    st.error(T("rep_err_pdf", e=R_["perr"]))
                d2.download_button(T("rep_dl_html"), R_["html"], file_name=fn + ".html", mime="text/html")
                with st.expander(T("rep_preview")):
                    st.markdown(rep.blocks_to_streamlit_md(R_["blocks"]))