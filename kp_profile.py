"""Personal profile (gender, education, siblings, work, marriage) + KP cross-check.
ask_profile(lang) -> dict (Streamlit form)       profile_blocks(chart, prof, lang) -> report blocks
profile_text(prof) -> English summary for Gemini
The house lists below are editable - match them to your KP Reader books."""
from datetime import timedelta
import streamlit as st
import kp_engine as kp
import kp_report as rep

MALE, FEMALE = {"Sun", "Mars", "Jupiter"}, {"Moon", "Venus"}      # others = neutral
SIB = dict(cusp=3, fav=[3, 11], deny=[2, 10])                     # 3 = younger, 11 = elder siblings
EDU_BASIC = dict(cusp=4, fav=[4, 9, 11], deny=[3, 8, 12])
EDU_HIGH = dict(cusp=9, fav=[4, 9, 11], deny=[3, 8, 12])

LBL = {  # key: (English, Sinhala)
    "male": ("Male", "පිරිමි"), "female": ("Female", "ගැහැණු"), "other": ("Other", "වෙනත්"),
    "ol": ("O/L", "සාමාන්‍ය පෙළ"), "al": ("A/L", "උසස් පෙළ"), "diploma": ("Diploma", "ඩිප්ලෝමා"),
    "degree": ("Degree", "උපාධිය"), "master": ("Postgraduate", "පශ්චාත් උපාධි"), "elo": ("Other", "වෙනත්"),
    "sci_math": ("Science - Maths", "විද්‍යා - ගණිත"), "sci_bio": ("Science - Biology", "විද්‍යා - ජීව"),
    "commerce": ("Commerce", "වාණිජ"), "arts": ("Arts", "කලා"), "tech": ("Technology / Engineering", "තාක්ෂණ / ඉංජිනේරු"),
    "other": ("Other / vocational", "වෙනත් / වෘත්තීය"), "na": ("Not applicable", "අදාළ නොවේ"),
    "job": ("Job (employee)", "රැකියාව (සේවකයා)"), "business": ("Business / self-employed", "ව්‍යාපාරය / ස්වයං රැකියා"),
    "both": ("Both", "දෙකම"), "student": ("Student", "ශිෂ්‍යයා"), "none": ("Not working", "රැකියාවක් නැත"),
    "single": ("Single", "අවිවාහක"), "engaged": ("Engaged / in relationship", "විවාහ ගිවිසුම / ප්‍රේම සම්බන්ධයක"),
    "married": ("Married", "විවාහක"), "divorced": ("Divorced / separated", "දික්කසාද / වෙන්වී"), "widowed": ("Widowed", "වැන්දඹු"),
    "arranged": ("Arranged", "සම්මත (මාපිය)"), "love": ("Love", "ප්‍රේම"), "unknown": ("Unknown", "නොදනී"),
}
STREAMS = {  # stream: planets that indicate it
    "sci_math": {"Mars", "Mercury", "Saturn", "Rahu"}, "sci_bio": {"Moon", "Mars", "Sun", "Jupiter"},
    "commerce": {"Mercury", "Jupiter", "Venus"}, "arts": {"Venus", "Moon", "Jupiter", "Mercury"},
    "tech": {"Saturn", "Mars", "Rahu", "Mercury"}, "other": {"Ketu", "Saturn", "Sun"},
}
WORK = {
    "Sun": ("government, administration, authority, medicine", "රජයේ සේවය, පරිපාලනය, අධිකාරිය, වෛද්‍ය"),
    "Moon": ("public dealing, food, nursing, hospitality, travel", "ජනතා සම්බන්ධ, ආහාර, හෙද සේවය, ආගන්තුක සත්කාර, ගමන්"),
    "Mars": ("engineering, police/military, surgery, construction, machinery", "ඉංජිනේරු, පොලිස්/හමුදා, ශල්‍ය වෛද්‍ය, ඉදිකිරීම්, යන්ත්‍ර"),
    "Mercury": ("trade, accounts, IT, communication, writing", "වෙළඳාම, ගිණුම්, IT, සන්නිවේදනය, ලිවීම"),
    "Jupiter": ("teaching, law, banking/finance, advisory, religion", "ඉගැන්වීම, නීතිය, බැංකු/මූල්‍ය, උපදේශන, ආගමික"),
    "Venus": ("arts, design, vehicles, beauty, hospitality, luxury goods", "කලා, සැලසුම්, වාහන, රූපලාවණ්‍ය, ආගන්තුක, සුඛෝපභෝගී භාණ්ඩ"),
    "Saturn": ("labour-intensive, agriculture, mining, construction, long-term service", "කම්කරු, කෘෂිකර්ම, ඛනිජ, ඉදිකිරීම්, දිගුකාලීන සේවය"),
    "Rahu": ("foreign links, technology, unconventional or sudden-gain work", "විදේශ සම්බන්ධ, තාක්ෂණ, සාම්ප්‍රදායික නොවන / හදිසි ලාභ"),
    "Ketu": ("research, software, spiritual or behind-the-scenes work", "පර්යේෂණ, මෘදුකාංග, ආධ්‍යාත්මික, තිරය පිටුපස වැඩ"),
}
NATURE = {
    "Sun": ("dignified, proud, authoritative", "ගරුත්වයෙන් යුත්, අභිමානී, අධිකාරී"),
    "Moon": ("gentle, caring, emotional, soft-faced", "මෘදු, සැලකිලිමත්, සංවේදී, මෘදු මුහුණක්"),
    "Mars": ("energetic, bold, quick-tempered, athletic", "ශක්තිමත්, නිර්භීත, ඉක්මන් කෝපී, ක්‍රීඩාශීලී"),
    "Mercury": ("youthful, intelligent, talkative, witty", "තරුණ පෙනුම, බුද්ධිමත්, කතාබහ කරන, දක්ෂ"),
    "Jupiter": ("wise, kind, ethical, well-built", "ප්‍රාඥ, කරුණාවන්ත, සදාචාර, හොඳ සිරුරක්"),
    "Venus": ("attractive, artistic, charming, loves comfort", "ආකර්ෂණීය, කලාත්මක, ආකර්ශනීය, සුවපහසු ප්‍රිය"),
    "Saturn": ("serious, mature, hardworking, reserved", "බරපතල, පරිණත, වෑයම් කරන, ආරක්ෂිත"),
    "Rahu": ("unconventional, ambitious, foreign or different background", "සාම්ප්‍රදායික නොවන, අභිලාෂී, විදේශ / වෙනස් පසුබිමක්"),
    "Ketu": ("detached, spiritual, private, quiet", "වෙන්වූ, ආධ්‍යාත්මික, පෞද්ගලික, නිහඬ"),
}


def lab(k, lang):
    return LBL[k][1 if lang == "si" else 0]


def _x(lang):
    return lambda en, si: si if lang == "si" else en


# ------------------------------------------------------------------ form
def ask_profile(lang):
    x = _x(lang)
    st.markdown("#### " + x("Personal details (for deeper, checked analysis)", "පෞද්ගලික තොරතුරු (වඩා ගැඹුරු, සත්‍යාපිත විශ්ලේෂණයට)"))
    st.caption(x("Answers are compared with the KP chart. Mismatches may mean the birth time needs checking.",
                 "පිළිතුරු KP කේන්දරය සමඟ සසඳනු ලැබේ. නොගැළපීම් උපන් වේලාව පරීක්ෂා කළ යුතු බව පෙන්විය හැක."))
    opt = lambda keys: dict(options=keys, format_func=lambda k: lab(k, lang))
    p = {}
    c1, c2 = st.columns(2)
    p["gender"] = c1.selectbox(x("Gender", "ස්ත්‍රී/පුරුෂ භාවය"), key="pf_gender", **opt(["male", "female", "other"]))
    c2.write("")
    st.markdown("**" + x("Education", "අධ්‍යාපනය") + "**")
    e1, e2, e3 = st.columns(3)
    p["edu_level"] = e1.selectbox(x("Highest level", "ඉහළම මට්ටම"), key="pf_el", **opt(["ol", "al", "diploma", "degree", "master", "elo"]))
    p["edu_stream"] = e2.selectbox(x("A/L stream studied", "උසස් පෙළ විෂය ධාරාව"), key="pf_es",
                                   **opt(["sci_math", "sci_bio", "commerce", "arts", "tech", "other", "na"]))
    p["edu_detail"] = e3.text_input(x("Degree / subject / institute", "උපාධිය / විෂය / ආයතනය"), key="pf_ed")
    p["edu_break"] = st.checkbox(x("Education was interrupted or the course changed", "අධ්‍යාපනය අතර නතර වූයේ හෝ පාඨමාලාව වෙනස් කළා"), key="pf_eb")
    st.markdown("**" + x("Brothers and sisters", "සහෝදර සහෝදරියන්") + "**")
    s1, s2, s3, s4 = st.columns(4)
    p["b_elder"] = s1.number_input(x("Elder brothers", "වැඩිමල් සහෝදරයන්"), 0, 15, 0, key="pf_be")
    p["s_elder"] = s2.number_input(x("Elder sisters", "වැඩිමල් සහෝදරියන්"), 0, 15, 0, key="pf_se")
    p["b_younger"] = s3.number_input(x("Younger brothers", "බාල සහෝදරයන්"), 0, 15, 0, key="pf_by")
    p["s_younger"] = s4.number_input(x("Younger sisters", "බාල සහෝදරියන්"), 0, 15, 0, key="pf_sy")
    st.markdown("**" + x("Work", "රැකියාව / ව්‍යාපාරය") + "**")
    w1, w2, w3 = st.columns(3)
    p["work_type"] = w1.selectbox(x("Job or business?", "රැකියාවද ව්‍යාපාරයද?"), key="pf_wt", **opt(["job", "business", "both", "student", "none"]))
    p["work_detail"] = w2.text_input(x("What exactly (field / post / business)", "කුමක්ද (ක්ෂේත්‍රය / තනතුර / ව්‍යාපාරය)"), key="pf_wd")
    p["first_job_age"] = w3.number_input(x("Age at first job/business (0 = unknown)", "පළමු රැකියාව/ව්‍යාපාරය ආරම්භ කළ වයස (0 = නොදනී)"), 0, 80, 0, key="pf_fj")
    st.markdown("**" + x("Marriage and partner", "විවාහය සහ සහකරු/සහකාරිය") + "**")
    m1, m2, m3 = st.columns(3)
    p["marital"] = m1.selectbox(x("Marital status", "විවාහක තත්ත්වය"), key="pf_ms", **opt(["single", "engaged", "married", "divorced", "widowed"]))
    p["marriage_age"] = m2.number_input(x("Age at marriage (0 = n/a)", "විවාහ වූ වයස (0 = අදාළ නැත)"), 0, 90, 0, key="pf_ma")
    p["marriage_type"] = m3.selectbox(x("How it happened", "සිදු වූ ආකාරය"), key="pf_mt", **opt(["arranged", "love", "unknown"]))
    q1, q2 = st.columns(2)
    p["spouse_work"] = q1.text_input(x("Partner's work / education", "සහකරුගේ/සහකාරියගේ රැකියාව / අධ්‍යාපනය"), key="pf_sw")
    p["spouse_notes"] = q2.text_input(x("Partner's nature, looks, from where", "ස්වභාවය, පෙනුම, පෙදෙස"), key="pf_sn")
    p["notes"] = st.text_area(x("Anything else (important events, health, concerns)", "වෙනත් තොරතුරු (වැදගත් සිදුවීම්, සෞඛ්‍යය, ගැටලු)"), key="pf_notes", height=80)
    return p


def profile_text(p):
    if not p:
        return "(no personal details given)"
    en = lambda k: LBL[p[k]][0]
    return "\n".join([
        f"Gender: {en('gender')}",
        f"Education: level {en('edu_level')}, stream {en('edu_stream')}, detail '{p['edu_detail']}', interrupted: {p['edu_break']}",
        f"Siblings: elder brothers {p['b_elder']}, elder sisters {p['s_elder']}, younger brothers {p['b_younger']}, younger sisters {p['s_younger']}",
        f"Work: {en('work_type')}, '{p['work_detail']}', age at first job/business {p['first_job_age'] or 'unknown'}",
        f"Marriage: {en('marital')}, age at marriage {p['marriage_age'] or 'n/a'}, {en('marriage_type')}, partner work '{p['spouse_work']}', partner notes '{p['spouse_notes']}'",
        f"Other notes: {p['notes']}"])


# ------------------------------------------------------------------ KP cross-check
def _sg(chart, p):
    return set(chart["sig"][p]["houses"])


def _at_age(chart, age, fav):
    """Dasha-bhukti running at that age and whether both lords touch the favourable houses."""
    if not age:
        return None
    dt = chart["birth"] + timedelta(days=365.25 * age)
    per = next((q for q in chart["dasha"] if q["start"] <= dt < q["end"]), None)
    if not per:
        return None
    ok = bool(_sg(chart, per["md"]) & set(fav)) and bool(_sg(chart, per["ad"]) & set(fav))
    return per, ok


def profile_blocks(chart, p, lang):
    if not p:
        return []
    x = _x(lang)
    pn, _, _ = rep._nm(lang)
    H = lambda hs: ", ".join(map(str, hs)) or x("none", "නැත")
    ok = lambda b: x("matches the chart", "කේන්දරයට ගැළපේ") if b else x("does not clearly match the chart", "කේන්දරයට පැහැදිලිව නොගැළපේ")
    B = [("h1", x("Personal profile cross-check (KP)", "පෞද්ගලික තොරතුරු KP සත්‍යාපනය"))]
    cu = chart["cusps"]

    # ---- education
    pr4, pr9 = kp.promise(chart, EDU_BASIC), kp.promise(chart, EDU_HIGH)
    ind = [pr4["sub"], chart["planets"][pr4["sub"]]["star"], pr9["sub"], chart["planets"][pr9["sub"]]["star"]]
    hits = {k: sum(i in pl for i in ind) for k, pl in STREAMS.items()}
    top = [k for k, v in sorted(hits.items(), key=lambda kv: -kv[1]) if v][:3]
    B.append(("h2", x("Education and stream", "අධ්‍යාපනය සහ විෂය ධාරාව")))
    B.append(("p", x(f"Cusp 4 sub lord {pn(pr4['sub'])} signifies houses {H(pr4['houses'])} (basic education: {pr4['level']}). "
                     f"Cusp 9 sub lord {pn(pr9['sub'])} signifies {H(pr9['houses'])} (higher education: {pr9['level']}).",
                     f"4 වන සන්ධි උප අධිපති {pn(pr4['sub'])} කාරක භාව {H(pr4['houses'])} (මූලික අධ්‍යාපනය: {pr4['level']}). "
                     f"9 වන සන්ධි උප අධිපති {pn(pr9['sub'])} කාරක භාව {H(pr9['houses'])} (උසස් අධ්‍යාපනය: {pr9['level']}).")))
    B.append(("p", x("Indicated streams: ", "කේන්දරය දක්වන ධාරා: ") + (", ".join(lab(k, lang) for k in top) or "-")
              + x(f". You studied: {lab(p['edu_stream'], lang)} - ", f". ඔබ ඉගෙන ගත්තේ: {lab(p['edu_stream'], lang)} - ")
              + (ok(p["edu_stream"] in top) if p["edu_stream"] in STREAMS else x("not checked", "පරීක්ෂා නොකළ"))))
    if p["edu_break"]:
        B.append(("p", x("Interrupted education fits sub lord links to houses 3, 8 or 12: ", "අධ්‍යාපනය නතර වීම 3, 8, 12 භාව සම්බන්ධයට ගැළපේ: ")
                  + H(pr4["deny"])))

    # ---- siblings
    ps = kp.promise(chart, SIB)
    yp = [q for q in kp.PLANETS if 3 in _sg(chart, q)]
    ep = [q for q in kp.PLANETS if 11 in _sg(chart, q)]
    cnt = lambda pl: (sum(q in MALE for q in pl), sum(q in FEMALE for q in pl), sum(q not in MALE | FEMALE for q in pl))
    ym, yf, yn = cnt(yp); em, ef, en_ = cnt(ep)
    sy, se = p["b_younger"] + p["s_younger"], p["b_elder"] + p["s_elder"]
    B.append(("h2", x("Brothers and sisters", "සහෝදර සහෝදරියන්")))
    B.append(("p", x(f"Cusp 3 sub lord {pn(ps['sub'])} signifies {H(ps['houses'])}; siblings promise: {ps['level']}. "
                     f"House 3 = younger siblings, house 11 = elder siblings.",
                     f"3 වන සන්ධි උප අධිපති {pn(ps['sub'])} කාරක භාව {H(ps['houses'])}; සහෝදර පොරොන්දුව: {ps['level']}. "
                     f"3 වන භාවය = බාල, 11 වන භාවය = වැඩිමල්.")))
    B.append(("ul", [
        x(f"Younger side - planets signifying 3: {', '.join(pn(q) for q in yp) or 'none'} (male {ym}, female {yf}, neutral {yn}). "
          f"You report: {p['b_younger']} brothers, {p['s_younger']} sisters.",
          f"බාල පැත්ත - 3 කාරක ග්‍රහයන්: {', '.join(pn(q) for q in yp) or 'නැත'} (පුරුෂ {ym}, ස්ත්‍රී {yf}, මධ්‍යස්ථ {yn}). "
          f"ඔබ කියන්නේ: සහෝදරයන් {p['b_younger']}, සහෝදරියන් {p['s_younger']}."),
        x(f"Elder side - planets signifying 11: {', '.join(pn(q) for q in ep) or 'none'} (male {em}, female {ef}, neutral {en_}). "
          f"You report: {p['b_elder']} brothers, {p['s_elder']} sisters.",
          f"වැඩිමල් පැත්ත - 11 කාරක ග්‍රහයන්: {', '.join(pn(q) for q in ep) or 'නැත'} (පුරුෂ {em}, ස්ත්‍රී {ef}, මධ්‍යස්ථ {en_}). "
          f"ඔබ කියන්නේ: සහෝදරයන් {p['b_elder']}, සහෝදරියන් {p['s_elder']}."),
        x("Planet counts are only an indication of numbers and gender mix - the sub lord's promise matters most in KP.",
          "ග්‍රහ ගණන් සංඛ්‍යා සහ ස්ත්‍රී/පුරුෂ මිශ්‍රණය පිළිබඳ ඉඟියක් පමණි - KP හි වැදගත්ම දේ උප අධිපතියාගේ පොරොන්දුවයි.")]))
    tot = sy + se
    B.append(("p", x("Siblings reported: ", "ඔබ කියන සහෝදර සංඛ්‍යාව: ") + str(tot) + " - "
              + (ok(ps["level"] != "Weak") if tot else x("chart shows " + ("weak" if ps["level"] == "Weak" else "some") + " sibling promise",
                                                          "කේන්දරයේ සහෝදර පොරොන්දුව " + ("දුර්වල" if ps["level"] == "Weak" else "ඇත")))))

    # ---- work
    c10 = cu[9]["sub"]; s10 = _sg(chart, c10); star10 = chart["planets"][c10]["star"]
    jb, bz = 6 in s10, 7 in s10
    kind = "both" if jb and bz else "job" if jb else "business" if bz else "unclear"
    kl = {"both": ("job and business both indicated", "රැකියාව සහ ව්‍යාපාරය දෙකම"), "job": ("job (service, house 6)", "රැකියාව (සේවය, 6 වන භාවය)"),
          "business": ("business (house 7)", "ව්‍යාපාරය (7 වන භාවය)"), "unclear": ("not clearly either", "පැහැදිලිව එකක් නොවේ")}[kind]
    B.append(("h2", x("Job or business", "රැකියාව හෝ ව්‍යාපාරය")))
    B.append(("p", x(f"Cusp 10 sub lord {pn(c10)} (star lord {pn(star10)}) signifies {H(sorted(s10))}. Indicated: {kl[0]}. "
                     f"Work fields: {WORK[c10][0]}; also {WORK[star10][0]}.",
                     f"10 වන සන්ධි උප අධිපති {pn(c10)} (නැකත් අධිපති {pn(star10)}) කාරක භාව {H(sorted(s10))}. දක්වන්නේ: {kl[1]}. "
                     f"ක්ෂේත්‍ර: {WORK[c10][1]}; තවද {WORK[star10][1]}.")))
    wt = p["work_type"]
    if wt in ("job", "business", "both"):
        match = kind == "both" or wt == "both" or kind == wt
        B.append(("p", x(f"You work as: {lab(wt, lang)} ({p['work_detail']}) - ", f"ඔබ කරන්නේ: {lab(wt, lang)} ({p['work_detail']}) - ") + ok(match)))
    chk = _at_age(chart, p["first_job_age"], [2, 6, 10, 11])
    if chk:
        per, good = chk
        B.append(("p", x(f"At age {p['first_job_age']} the running dasha-bhukti was {pn(per['md'])}-{pn(per['ad'])}: "
                         + ("both lords touch houses 2/6/10/11, supporting a start of work." if good else "not clearly linked to houses 2/6/10/11."),
                         f"වයස {p['first_job_age']} දී දශා-භුක්තිය {pn(per['md'])}-{pn(per['ad'])}: "
                         + ("දෙදෙනාම 2/6/10/11 භාවවලට සම්බන්ධයි, රැකියාව ආරම්භයට සහාය වේ." if good else "2/6/10/11 භාවවලට පැහැදිලිව සම්බන්ධ නැත."))))

    # ---- marriage and partner
    pm = kp.promise(chart, kp.TOPICS["marriage"])
    s7 = cu[6]["sub"]; star7 = chart["planets"][s7]["star"]; sl7 = cu[6]["sign_lord"]
    g = p["gender"]
    partner = x("wife", "බිරිඳ") if g == "male" else x("husband", "සැමියා") if g == "female" else x("partner", "සහකරු/සහකාරිය")
    B.append(("h2", x("Marriage and partner", "විවාහය සහ සහකරු/සහකාරිය")))
    B.append(("p", x(f"Cusp 7 sub lord {pn(s7)} (star lord {pn(star7)}, sign lord {pn(sl7)}) signifies {H(pm['houses'])}; marriage promise: {pm['level']}. "
                     f"Likely {partner}: {NATURE[s7][0]}; shaped also by {pn(star7)} ({NATURE[star7][0]}). "
                     f"Partner's likely field: {WORK[s7][0]}.",
                     f"7 වන සන්ධි උප අධිපති {pn(s7)} (නැකත් අධිපති {pn(star7)}, රාශි අධිපති {pn(sl7)}) කාරක භාව {H(pm['houses'])}; විවාහ පොරොන්දුව: {pm['level']}. "
                     f"{partner}: {NATURE[s7][1]}; {pn(star7)} ({NATURE[star7][1]}) ගේ බලපෑමද ඇත. "
                     f"සහකරුගේ/සහකාරියගේ ක්ෂේත්‍රය: {WORK[s7][1]}.")))
    if p["spouse_work"] or p["spouse_notes"]:
        B.append(("p", x(f"You describe your partner as: {p['spouse_work']} {p['spouse_notes']}", f"ඔබ සහකරු/සහකාරිය ගැන කියන්නේ: {p['spouse_work']} {p['spouse_notes']}")))
    if p["marital"] in ("married", "divorced", "widowed") and p["marriage_age"]:
        chk = _at_age(chart, p["marriage_age"], [2, 7, 11])
        if chk:
            per, good = chk
            B.append(("p", x(f"At marriage (age {p['marriage_age']}) the dasha-bhukti was {pn(per['md'])}-{pn(per['ad'])}: "
                             + ("both lords touch houses 2/7/11 - consistent with the chart." if good else "not clearly linked to 2/7/11 - birth time may need checking."),
                             f"විවාහයේදී (වයස {p['marriage_age']}) දශා-භුක්තිය {pn(per['md'])}-{pn(per['ad'])}: "
                             + ("දෙදෙනාම 2/7/11 භාවවලට සම්බන්ධයි - කේන්දරයට ගැළපේ." if good else "2/7/11 වලට පැහැදිලිව සම්බන්ධ නැත - උපන් වේලාව පරීක්ෂා කරන්න."))))
    elif p["marital"] in ("single", "engaged"):
        w = kp.windows(chart, kp.TOPICS["marriage"], chart["birth"].__class__.now(), chart["birth"].__class__.now() + timedelta(days=365.25 * 10))
        w = sorted(w, key=lambda r_: (r_["level"] != "Strong", r_["start"]))[:3]
        if w:
            B.append(("ul", [x("Marriage window: ", "විවාහ කාලය: ") + f"{rep.fmt(r_['start'])} - {rep.fmt(r_['end'])} ({pn(r_['md'])}-{pn(r_['ad'])}, {r_['level']})" for r_ in w]))
    return B