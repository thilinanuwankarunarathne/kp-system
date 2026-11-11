"""KP engine: chart, cusps, star/sub lords, significators, Vimshottari dasha,
life-area judgement and ruling planets.   Needs:  pip install pyswisseph
(Uses the built-in Moshier ephemeris, so no extra ephemeris files are needed.)"""
from datetime import timedelta
import swisseph as swe
from setup_db import DASHA, NAKSHATRAS, SIGNS, SIGN_LORDS

NAK = 360 / 27            # one nakshatra = 13°20'
YEAR = 365.25             # days per dasha year
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
_SWE = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE}
WEEKDAY = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]   # Mon..Sun

# ---------------------------------------------------------------- life areas
# fav  = houses that give the result      deny = houses that block it
# EDIT these to match your KP Reader books (that is what the Book tab is for).
TOPICS = {
    "marriage":  dict(label="Marriage (විවාහය)",        cusp=7,  fav=[2, 7, 11],  deny=[1, 6, 10],     kw=["marriage", "7th", "sub lord"]),
    "children":  dict(label="Children (දරුවන්)",       cusp=5,  fav=[2, 5, 11],  deny=[1, 4, 10],     kw=["children", "5th", "sub lord"]),
    "job":       dict(label="Job (රැකියාව)",           cusp=10, fav=[2, 6, 10, 11], deny=[5, 8, 9],   kw=["job", "10th", "sub lord"]),
    "business":  dict(label="Business (ව්‍යාපාරය)",    cusp=10, fav=[2, 7, 10, 11], deny=[5, 8, 12],  kw=["business", "10th", "sub lord"]),
    "wealth":    dict(label="Wealth (ධනය)",            cusp=2,  fav=[2, 6, 11],  deny=[5, 8, 12],     kw=["wealth", "2nd", "sub lord"]),
    "education": dict(label="Education (අධ්‍යාපනය)",  cusp=4,  fav=[4, 9, 11],  deny=[3, 8, 12],     kw=["education", "4th", "sub lord"]),
    "property":  dict(label="Property/Home (දේපළ)",    cusp=4,  fav=[4, 11, 12], deny=[3, 5, 10],     kw=["property", "4th", "sub lord"]),
    "vehicle":   dict(label="Vehicle (වාහන)",          cusp=4,  fav=[4, 11],     deny=[3, 12],        kw=["vehicle", "4th", "sub lord"]),
    "foreign":   dict(label="Foreign travel (විදේශ ගමන්)", cusp=12, fav=[3, 9, 12], deny=[2, 4, 11],  kw=["foreign", "12th", "sub lord"]),
    "health":    dict(label="Health (සෞඛ්‍යය)",         cusp=1,  fav=[1, 5, 11],  deny=[6, 8, 12],     kw=["health", "1st", "sub lord"]),
    "litigation": dict(label="Court case (නඩු)",       cusp=6,  fav=[6, 11],     deny=[5, 8, 12],     kw=["litigation", "6th", "sub lord"]),
}


# ---------------------------------------------------------------- lords
def _sub_of(within, span, first_idx):
    """Find sub-division lord inside a span, sequence starts at DASHA[first_idx]."""
    pos = 0.0
    for k in range(9):
        idx = (first_idx + k) % 9
        ln = span * DASHA[idx][1] / 120
        if within < pos + ln or k == 8:
            return DASHA[idx][0], idx, within - pos, ln
        pos += ln


def lords(lon):
    lon %= 360
    n = int(lon // NAK)
    star_idx = n % 9
    sub, sidx, rem, ln = _sub_of(lon - n * NAK, NAK, star_idx)
    subsub = _sub_of(rem, ln, sidx)[0]
    s = int(lon // 30)
    return dict(sign=SIGNS[s], sign_lord=SIGN_LORDS[s], nakshatra=NAKSHATRAS[n],
                star=DASHA[star_idx][0], sub=sub, subsub=subsub)


def dms(lon):
    x = lon % 30
    d = int(x); m = int((x - d) * 60); s = int(round((((x - d) * 60) - m) * 60))
    if s == 60: s, m = 0, m + 1
    return f"{d}°{m:02d}'{s:02d}\""


def house_of(lon, cusps):
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if (lon - a) % 360 < (b - a) % 360:
            return i + 1
    return 1


# ---------------------------------------------------------------- chart
def build_chart(local_dt, tz, lat, lon):
    """local_dt = naive datetime in local time, tz = hours east of UTC (Sri Lanka 5.5)."""
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    ut = local_dt - timedelta(hours=tz)
    jd = swe.julday(ut.year, ut.month, ut.day, ut.hour + ut.minute / 60 + ut.second / 3600)
    ay = swe.get_ayanamsa_ut(jd)
    fl = swe.FLG_MOSEPH | swe.FLG_SPEED

    ct, _ = swe.houses(jd, lat, lon, b"P")                 # Placidus (KP standard)
    ct = list(ct[1:] if len(ct) == 13 else ct)
    cusp_lon = [(c - ay) % 360 for c in ct]

    raw = {}
    for p, code in _SWE.items():
        x = swe.calc_ut(jd, code, fl)[0]
        raw[p] = ((x[0] - ay) % 360, x[3] < 0)
    raw["Rahu"] = (raw["Rahu"][0], True)                   # mean node (as in KP ephemeris)
    raw["Ketu"] = ((raw["Rahu"][0] + 180) % 360, True)

    planets = {}
    for p, (l, retro) in raw.items():
        d = lords(l)
        d.update(lon=l, retro=retro, house=house_of(l, cusp_lon))
        planets[p] = d
    cusps = [dict(house=i + 1, lon=c, **lords(c)) for i, c in enumerate(cusp_lon)]

    owns = {p: [] for p in PLANETS}                        # houses owned (by cusp sign)
    for c in cusps:
        owns[c["sign_lord"]].append(c["house"])

    sig = {}
    for p in PLANETS:                                      # KP 4-level significators
        star = planets[p]["star"]
        lv = [[planets[star]["house"]], [planets[p]["house"]], owns[star], owns[p]]
        order = []
        for l in lv:
            for h in l:
                if h not in order:
                    order.append(h)
        sig[p] = dict(levels=lv, houses=order)

    chart = dict(planets=planets, cusps=cusps, owns=owns, sig=sig, birth=local_dt,
                 tz=tz, lat=lat, lon=lon, ayanamsa=ay)
    chart["dasha"] = vimshottari(planets["Moon"]["lon"], local_dt)
    return chart


# ---------------------------------------------------------------- dasha
def vimshottari(moon_lon, birth):
    n = int(moon_lon // NAK)
    idx = n % 9
    frac = (moon_lon - n * NAK) / NAK
    t = birth - timedelta(days=DASHA[idx][1] * frac * YEAR)   # theoretical start of 1st dasha
    out = []
    for k in range(12):
        mi = (idx + k) % 9
        md, y = DASHA[mi]
        s = t
        for j in range(9):
            ad, ay_ = DASHA[(mi + j) % 9]
            e = s + timedelta(days=y * ay_ / 120 * YEAR)
            if e > birth:
                out.append(dict(md=md, ad=ad, start=max(s, birth), end=e))
            s = e
        t += timedelta(days=y * YEAR)
    return out


def current_period(chart, at):
    for p in chart["dasha"]:
        if p["start"] <= at < p["end"]:
            return p


def pratyantars(p):
    names = [d[0] for d in DASHA]
    idx = names.index(p["ad"])
    total = p["end"] - p["start"]
    s, out = p["start"], []
    for j in range(9):
        l, y = DASHA[(idx + j) % 9]
        e = s + total * y / 120
        out.append(dict(lord=l, start=s, end=e))
        s = e
    return out


# ---------------------------------------------------------------- judgement
def promise(chart, t):
    """Is the event promised? Cusp sub-lord must signify the favourable houses."""
    cs = chart["cusps"][t["cusp"] - 1]
    sub = cs["sub"]
    sg = set(chart["sig"][sub]["houses"])
    fav = sorted(sg & set(t["fav"]))
    den = sorted(sg & set(t["deny"]))
    primary = t["cusp"] in sg
    if primary and len(fav) >= 2 and len(den) < len(fav):
        level = "Strong"
    elif len(fav) >= 2 and len(den) <= len(fav):
        level = "Moderate"
    else:
        level = "Weak"
    return dict(sub=sub, star=chart["planets"][sub]["star"], houses=chart["sig"][sub]["houses"],
                fav=fav, deny=den, level=level)


def _score(chart, planet, F, D):
    sg = set(chart["sig"][planet]["houses"])
    return len(sg & F), len(sg & D), sorted(sg & F)


def windows(chart, t, start, end, rp=None):
    """Dasha-Bhukti periods in which both lords signify the favourable houses."""
    F, D = set(t["fav"]), set(t["deny"])
    rp = set(rp or [])
    out = []
    for p in chart["dasha"]:
        if p["end"] < start or p["start"] > end:
            continue
        fa, da, ha = _score(chart, p["md"], F, D)
        fb, db, hb = _score(chart, p["ad"], F, D)
        if fa >= 2 and fb >= 2 and da < fa and db < fb:
            level = "Strong"
        elif fa >= 1 and fb >= 1 and fa + fb >= 3 and da <= fa and db <= fb:
            level = "Medium"
        else:
            continue
        out.append(dict(start=p["start"], end=p["end"], md=p["md"], ad=p["ad"], level=level,
                        md_houses=ha, ad_houses=hb,
                        rp=[x for x in (p["md"], p["ad"]) if x in rp]))
    return out


def ruling_planets(now_local, tz, lat, lon):
    """Ruling planets for the moment of query (confirmation tool in KP)."""
    c = build_chart(now_local, tz, lat, lon)
    m, a = c["planets"]["Moon"], c["cusps"][0]
    rp = {"Day lord": WEEKDAY[now_local.weekday()],
          "Lagna sign lord": a["sign_lord"], "Lagna star lord": a["star"], "Lagna sub lord": a["sub"],
          "Moon sign lord": m["sign_lord"], "Moon star lord": m["star"], "Moon sub lord": m["sub"]}
    return rp