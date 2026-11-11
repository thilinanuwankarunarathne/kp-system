"""Sinhala / English text for the KP app.
Usage:  T("key")  -> text in the selected language   (app.py sets st.session_state["lang"] = "si" | "en")
        pn(planet), sn(sign), nn(nakshatra), place_name(p), topic_name(k)  -> translated names
To change a wording, edit the "en" / "si" text below."""
import streamlit as st


def L():
    return st.session_state.get("lang", "si")


def T(key, **kw):
    s = TR[key][L()]
    return s.format(**kw) if kw else s


def _m(d, x):
    return d.get(x, x) if L() == "si" else x


PLANET_SI = {"Sun": "සූර්ය", "Moon": "චන්ද්‍ර", "Mars": "කුජ (අඟහරු)", "Mercury": "බුධ", "Jupiter": "ගුරු",
             "Venus": "සිකුරු", "Saturn": "සෙනසුරු", "Rahu": "රාහු", "Ketu": "කේතු"}
PLANET_ABBR = {"en": dict(Sun="Su", Moon="Mo", Mars="Ma", Mercury="Me", Jupiter="Ju", Venus="Ve",
                          Saturn="Sa", Rahu="Ra", Ketu="Ke"),
               "si": dict(Sun="සූ", Moon="ච", Mars="කු", Mercury="බු", Jupiter="ගු", Venus="සි",
                          Saturn="සෙ", Rahu="රා", Ketu="කේ")}
SIGN_SI = {"Aries": "මේෂ", "Taurus": "වෘෂභ", "Gemini": "මිථුන", "Cancer": "කටක", "Leo": "සිංහ",
           "Virgo": "කන්‍යා", "Libra": "තුලා", "Scorpio": "වෘශ්චික", "Sagittarius": "ධනු",
           "Capricorn": "මකර", "Aquarius": "කුම්භ", "Pisces": "මීන"}
NAK_SI = {"Ashwini": "අශ්විනි", "Bharani": "භරණි", "Krittika": "කෘත්තිකා", "Rohini": "රෝහිණී",
          "Mrigashira": "මුගසිරස", "Ardra": "ආර්ද්‍රා", "Punarvasu": "පුනර්වසු", "Pushya": "පුෂ්‍ය",
          "Ashlesha": "ආශ්ලේෂා", "Magha": "මඝ", "Purva Phalguni": "පූර්ව ඵල්ගුනී",
          "Uttara Phalguni": "උත්තර ඵල්ගුනී", "Hasta": "හස්ත", "Chitra": "චිත්‍රා", "Swati": "ස්වාති",
          "Vishakha": "විශාඛා", "Anuradha": "අනුරාධා", "Jyeshtha": "ජ්‍යෙෂ්ඨා", "Mula": "මූල",
          "Purva Ashadha": "පූර්වාෂාඪ", "Uttara Ashadha": "උත්තරාෂාඪ", "Shravana": "ශ්‍රවණ",
          "Dhanishta": "ධනිෂ්ඨා", "Shatabhisha": "ශතභිෂා", "Purva Bhadrapada": "පූර්වභද්‍රපද",
          "Uttara Bhadrapada": "උත්තරභද්‍රපද", "Revati": "රේවතී"}
PLACE_SI = {"Colombo": "කොළඹ", "Negombo": "මීගමුව", "Kandy": "මහනුවර", "Galle": "ගාල්ල", "Matara": "මාතර",
            "Jaffna": "යාපනය", "Kurunegala": "කුරුණෑගල", "Anuradhapura": "අනුරාධපුරය", "Ratnapura": "රත්නපුර",
            "Batticaloa": "මඩකලපුව", "Chennai": "චෙන්නායි", "Mumbai": "මුම්බායි", "Delhi": "දිල්ලි",
            "Custom": "වෙනත් (පහත ඇතුළත් කරන්න)"}
TOPIC_SI = {"marriage": "විවාහය", "children": "දරුවන්", "job": "රැකියාව", "business": "ව්‍යාපාරය",
            "wealth": "ධනය", "education": "අධ්‍යාපනය", "property": "දේපළ / නිවාස", "vehicle": "වාහන",
            "foreign": "විදේශ ගමන්", "health": "සෞඛ්‍යය", "litigation": "නඩු කටයුතු"}
TOPIC_EN = {"marriage": "Marriage", "children": "Children", "job": "Job", "business": "Business",
            "wealth": "Wealth", "education": "Education", "property": "Property / Home", "vehicle": "Vehicle",
            "foreign": "Foreign travel", "health": "Health", "litigation": "Court case"}
RP_SI = {"Day lord": "දින අධිපති", "Lagna sign lord": "ලග්න රාශි අධිපති", "Lagna star lord": "ලග්න නැකත් අධිපති",
         "Lagna sub lord": "ලග්න උප අධිපති", "Moon sign lord": "චන්ද්‍ර රාශි අධිපති",
         "Moon star lord": "චන්ද්‍ර නැකත් අධිපති", "Moon sub lord": "චන්ද්‍ර උප අධිපති"}


def pn(x): return _m(PLANET_SI, x)
def sn(x): return _m(SIGN_SI, x)
def nn(x): return _m(NAK_SI, x)
def place_name(x): return _m(PLACE_SI, x)
def rp_name(x): return _m(RP_SI, x)
def topic_name(k): return TOPIC_SI[k] if L() == "si" else TOPIC_EN[k]
def abbr(p): return PLANET_ABBR[L()][p]


TR = {
    # ---------------- app / menu
    "lang": {"en": "Language / භාෂාව", "si": "Language / භාෂාව"},
    "menu": {"en": "Menu", "si": "මෙනුව"},
    "m_horo": {"en": "🔮 Horoscope Reading", "si": "🔮 කේ.පී. පලාපල බැලීම"},
    "m_books": {"en": "📚 Books", "si": "📚 පොත්"},
    "m_upload": {"en": "⬆️ PDF Upload", "si": "⬆️ PDF උඩුගත කිරීම"},
    "m_search": {"en": "🔎 Search", "si": "🔎 සෙවීම"},
    "m_review": {"en": "🛠️ Pages to review", "si": "🛠️ පරීක්ෂා කළ යුතු පිටු"},
    "m_sub": {"en": "🔢 Sub-Lord table", "si": "🔢 Sub-Lord වගුව"},
    "upload_pdf": {"en": "KP PDF book", "si": "KP PDF පොත"},
    "book_title": {"en": "Book title", "si": "පොතේ නම"},
    "ingest_btn": {"en": "Add to database", "si": "Database එකට ඇතුළත් කරන්න"},
    "reading_pages": {"en": "Reading pages... (large books may take a few minutes)",
                      "si": "පිටු කියවමින්... (විශාල පොත් වලට විනාඩි කිහිපයක් යා හැක)"},
    "done_books": {"en": "Done! See the Books menu.", "si": "අවසන්! '📚 පොත්' මෙනුවෙන් බලන්න."},
    "search_words": {"en": "Search words (English)", "si": "සෙවුම් වචන (English)"},
    "search_err": {"en": "Search error: {e}", "si": "සෙවුම් දෝෂයකි: {e}"},
    "results": {"en": "Results: {n}", "si": "ප්‍රතිඵල: {n}"},
    "page": {"en": "page", "si": "පිටුව"},
    "review_caption": {"en": "Showing {n} pages (max 50)", "si": "පෙන්වන පිටු {n} (උපරිම 50)"},
    "save": {"en": "Save", "si": "සුරකින්න"},
    "sign_filter": {"en": "Sign", "si": "රාශිය"},
    "sublord_filter": {"en": "Sub-lord", "si": "Sub-lord"},
    "all": {"en": "All", "si": "සියල්ල"},

    # ---------------- horoscope page
    "title": {"en": "🔮 KP Horoscope Reading", "si": "🔮 කේ.පී. පලාපල බැලීම (KP Horoscope)"},
    "guide_title": {"en": "📖 How to use this page (guide)", "si": "📖 භාවිතා කරන ආකාරය (මාර්ගෝපදේශය)"},
    "sec_birth": {"en": "1️⃣ Birth details", "si": "1️⃣ උපත පිළිබඳ තොරතුරු"},
    "load_saved": {"en": "Load saved person", "si": "සුරකින ලද පුද්ගලයා තෝරන්න"},
    "load": {"en": "Load", "si": "පූරණය කරන්න"},
    "name": {"en": "Name", "si": "නම"},
    "dob": {"en": "Date of birth", "si": "උපන් දිනය"},
    "tob": {"en": "Time of birth", "si": "උපන් වේලාව"},
    "place": {"en": "Birth place", "si": "උපන් ස්ථානය"},
    "lat": {"en": "Latitude (N +)", "si": "අක්ෂාංශය (උතුර +)"},
    "lon": {"en": "Longitude (E +)", "si": "දේශාංශය (නැගෙනහිර +)"},
    "tz": {"en": "Time zone (UTC +)", "si": "වේලා කලාපය (UTC +)"},
    "calc": {"en": "✨ Calculate horoscope", "si": "✨ කේන්දරය ගණනය කරන්න"},
    "save_person": {"en": "💾 Save this person", "si": "💾 මෙම පුද්ගලයා සුරකින්න"},
    "saved_ok": {"en": "Saved.", "si": "සුරකින ලදී."},
    "fill_info": {"en": "Fill in the details and press **Calculate horoscope**.",
                  "si": "තොරතුරු පුරවා **'කේන්දරය ගණනය කරන්න'** බොත්තම ඔබන්න."},
    "native": {"en": "Native", "si": "ජාතකයා"},
    "summary": {"en": "{name} · born {dt} · Lagna: {lagna} · Moon: {nak} · KP ayanamsa {ay}",
                "si": "{name} · උපත {dt} · ලග්නය: {lagna} · චන්ද්‍රයා: {nak} · KP අයනාංශය {ay}"},
    "look_ahead": {"en": "Look ahead (years)", "si": "ඉදිරි වසර ගණන"},
    "tab_chart": {"en": "🪐 Chart", "si": "🪐 කේන්දරය"},
    "tab_sig": {"en": "🔗 Significators", "si": "🔗 කාරක ග්‍රහයන්"},
    "tab_dasha": {"en": "⏳ Dasha", "si": "⏳ දශා"},
    "tab_life": {"en": "🎯 Life Areas", "si": "🎯 ජීවිත ක්ෂේත්‍ර"},
    "tab_book": {"en": "📚 Book references", "si": "📚 පොත් යොමු"},
    "tab_rp": {"en": "🧭 Ruling Planets", "si": "🧭 පාලක ග්‍රහයන්"},

    # chart tab
    "rasi": {"en": "Rasi chart", "si": "රාශි චක්‍රය"},
    "asc": {"en": "Asc", "si": "ලග්න"},
    "planets": {"en": "Planets", "si": "ග්‍රහයෝ"},
    "cusps": {"en": "House cusps (Placidus, KP)", "si": "භාව සන්ධි (Placidus, KP)"},
    "c_planet": {"en": "Planet", "si": "ග්‍රහයා"},
    "c_pos": {"en": "Position", "si": "පිහිටීම"},
    "c_nak": {"en": "Nakshatra", "si": "නැකත"},
    "c_star": {"en": "Star lord", "si": "නැකත් අධිපති"},
    "c_sub": {"en": "Sub lord", "si": "උප අධිපති (Sub)"},
    "c_subsub": {"en": "Sub-sub", "si": "උප-උප"},
    "c_house": {"en": "House", "si": "භාවය"},
    "c_retro": {"en": "R", "si": "ව"},
    "c_signlord": {"en": "Sign lord", "si": "රාශි අධිපති"},

    # significators tab
    "sig_caption": {"en": "L1 = house occupied by the star lord (strongest) · L2 = planet's own house · "
                          "L3 = houses owned by the star lord · L4 = houses owned by the planet",
                    "si": "L1 = නැකත් අධිපතියා සිටින භාවය (ශක්තිමත්ම) · L2 = ග්‍රහයා සිටින භාවය · "
                          "L3 = නැකත් අධිපතියා අයිති භාව · L4 = ග්‍රහයා අයිති භාව"},
    "all_houses": {"en": "All houses", "si": "සියලු භාව"},
    "house_wise": {"en": "House-wise signifiers", "si": "භාව අනුව කාරක ග්‍රහයන්"},
    "c_planets": {"en": "Planets", "si": "ග්‍රහයන්"},

    # dasha tab
    "now": {"en": "Now", "si": "දැන්"},
    "md": {"en": "Mahadasha", "si": "මහා දශාව"},
    "ad": {"en": "Antardasha", "si": "අන්තර් දශාව"},
    "pd": {"en": "Pratyantar", "si": "ප්‍රත්‍යන්තර"},
    "from": {"en": "From", "si": "සිට"},
    "to": {"en": "To", "si": "දක්වා"},
    "md_sig": {"en": "MD signifies", "si": "මහා දශා කාරක භාව"},
    "ad_sig": {"en": "AD signifies", "si": "අන්තර් දශා කාරක භාව"},

    # life areas tab
    "overview": {"en": "Overview – all areas", "si": "සාරාංශය – සියලු ක්ෂේත්‍ර"},
    "area": {"en": "Area", "si": "ක්ෂේත්‍රය"},
    "cusp": {"en": "Cusp", "si": "සන්ධිය"},
    "cusp_sub": {"en": "Cusp sub lord", "si": "සන්ධි උප අධිපති"},
    "signifies": {"en": "Signifies houses", "si": "කාරක භාව"},
    "promise": {"en": "Promise", "si": "පොරොන්දුව"},
    "next_window": {"en": "Next good period", "si": "ඊළඟ හොඳ කාලය"},
    "choose_area": {"en": "Choose an area for details", "si": "විස්තර සඳහා ක්ෂේත්‍රයක් තෝරන්න"},
    "promise_h": {"en": "Promise: {lvl}", "si": "පොරොන්දුව: {lvl}"},
    "cusp_line": {"en": "Sub lord of cusp {n} = **{sub}** (star lord {star}) signifies houses **{h}**",
                  "si": "{n} වන භාව සන්ධියේ උප අධිපති = **{sub}** (නැකත් අධිපති {star}) කාරක වන භාව: **{h}**"},
    "fav_line": {"en": "Favourable houses needed: {need} → matched: **{m}**",
                 "si": "අවශ්‍ය හිතකර භාව: {need} → ගැළපෙන: **{m}**"},
    "deny_line": {"en": "Blocking houses: {need} → present: **{m}**",
                  "si": "බාධක භාව: {need} → ඇති: **{m}**"},
    "none": {"en": "none", "si": "නැත"},
    "fav_periods": {"en": "⏳ Favourable periods", "si": "⏳ හිතකර කාල"},
    "weak_warn": {"en": "The cusp sub lord does not promise this strongly – the periods below are less reliable.",
                  "si": "සන්ධි උප අධිපති මෙය ශක්තිමත්ව පොරොන්දු නොවේ – පහත කාල අඩු විශ්වාසදායක වේ."},
    "strength": {"en": "Strength", "si": "ශක්තිය"},
    "dasha_bhukti": {"en": "Dasha-Bhukti", "si": "දශා-භුක්ති"},
    "md_match": {"en": "MD matches", "si": "මහා දශා ගැළපීම"},
    "ad_match": {"en": "AD matches", "si": "අන්තර් දශා ගැළපීම"},
    "rp_match": {"en": "Ruling-planet match", "si": "පාලක ග්‍රහ ගැළපීම"},
    "no_windows": {"en": "No favourable dasha-bhukti in this period. Increase 'Look ahead'.",
                   "si": "මෙම කාලයේ හිතකර දශා-භුක්තියක් නැත. 'ඉදිරි වසර ගණන' වැඩි කරන්න."},
    "lvl_Strong": {"en": "Strong", "si": "ශක්තිමත්"},
    "lvl_Moderate": {"en": "Moderate", "si": "මධ්‍යම"},
    "lvl_Medium": {"en": "Medium", "si": "මධ්‍යම"},
    "lvl_Weak": {"en": "Weak", "si": "දුර්වල"},

    # book tab
    "topic": {"en": "Topic", "si": "මාතෘකාව"},
    "rules_h": {"en": "Extracted rules (✅ = verified against the book)",
                "si": "උපුටා ගත් නීති (✅ = පොත සමඟ සත්‍යාපිත)"},
    "no_rules": {"en": "No rules yet. Run `python extract_rules.py <book_id>`.",
                 "si": "තවම නීති නැත. `python extract_rules.py <book_id>` ධාවනය කරන්න."},
    "pages_h": {"en": "Matching book pages", "si": "ගැළපෙන පොත් පිටු"},
    "no_pages": {"en": "No pages found. Upload books from the PDF Upload menu.",
                 "si": "පිටු හමු නොවීය. 'PDF උඩුගත කිරීම' මෙනුවෙන් පොත් ඇතුළත් කරන්න."},
    "page_no": {"en": "page", "si": "පිටුව"},

    # ruling planets tab
    "rp_caption": {"en": "Ruling planets for now ({now}) at the birth place.",
                   "si": "දැන් ({now}) සඳහා පාලක ග්‍රහයන් (උපන් ස්ථානය අනුව)."},
    "rp_source": {"en": "Source", "si": "මූලාශ්‍රය"},
    "rp_combined": {"en": "Combined set:", "si": "සමස්ත කට්ටලය:"},

    # ---------------- guide
    "guide": {"en": """
**Step by step**
1. **Enter birth details** – date, exact time (to the minute) and place. KP sub lords can change within minutes, so the birth time must be accurate.
2. **Check the time zone** – Sri Lanka is +5.5. (Between 1996 and 2006 Sri Lanka used +6:00 / +6:30 for a period – check for births in those years.)
3. Press **Calculate horoscope**.
4. **🪐 Chart** – planets, house cusps, and the star lord and sub lord of each.
5. **🔗 Significators** – which houses each planet signifies (KP 4-level method).
6. **🎯 Life Areas** – choose Marriage / Job / Children etc.
   - **Promise**: the *sub lord of the relevant cusp* must signify the favourable houses (e.g. marriage = 7th cusp sub lord → houses 2, 7, 11).
   - **Timing**: both the *Dasha and Bhukti* lords must signify those houses. 🟢 = strong, 🟡 = medium.
7. **🧭 Ruling Planets** – planets ruling the moment of query; periods that match them are more reliable.
8. **📚 Book references** – pages from your KP books on the same topic, so every rule can be verified.

**Tip:** Promise 🟢 + time window 🟢 + ruling-planet match = good confirmation. If the promise is 🔴 the result is unlikely whatever the dasha.

*The rules used are in `kp_engine.TOPICS` – edit the house lists to match your books. Astrology is guidance, not certainty; do not rely on it alone for health, legal or financial decisions.*
""",
              "si": """
**පියවරෙන් පියවර**
1. **උපත් තොරතුරු ඇතුළත් කරන්න** – උපන් දිනය, නිවැරදි වේලාව (මිනිත්තුවට) සහ උපන් ස්ථානය. KP ක්‍රමයේ උප අධිපති (sub lord) මිනිත්තු කිහිපයකින් වෙනස් විය හැකි නිසා උපන් වේලාව නිවැරදි විය යුතුය.
2. **වේලා කලාපය පරීක්ෂා කරන්න** – ශ්‍රී ලංකාව +5.5 වේ. (1996 – 2006 අතර කාලයේ ශ්‍රී ලංකාව +6:00 / +6:30 භාවිතා කළ බැවින් එම වසරවල උපත් සඳහා පරීක්ෂා කරන්න.)
3. **'කේන්දරය ගණනය කරන්න'** බොත්තම ඔබන්න.
4. **🪐 කේන්දරය** – ග්‍රහයන්, භාව සන්ධි, සහ ඒවායේ නැකත් අධිපති හා උප අධිපති බලන්න.
5. **🔗 කාරක ග්‍රහයන්** – සෑම ග්‍රහයෙක්ම කිනම් භාවවලට කාරකද යන්න (KP මට්ටම් 4 ක්‍රමය).
6. **🎯 ජීවිත ක්ෂේත්‍ර** – විවාහය / රැකියාව / දරුවන් ආදිය තෝරන්න.
   - **පොරොන්දුව (Promise)**: අදාළ භාව සන්ධියේ *උප අධිපතියා* හිතකර භාවවලට කාරක විය යුතුය (උදා: විවාහය = 7 වන සන්ධියේ උප අධිපති → 2, 7, 11).
   - **කාලය (Timing)**: *දශා සහ භුක්ති* අධිපතියන් දෙදෙනාම එම භාවවලට කාරක විය යුතුය. 🟢 = ශක්තිමත්, 🟡 = මධ්‍යම.
7. **🧭 පාලක ග්‍රහයන්** – ප්‍රශ්න වේලාවේ පාලක ග්‍රහයන්; ඔවුන් සමඟ ගැළපෙන කාල වඩා විශ්වාසදායකය.
8. **📚 පොත් යොමු** – එම මාතෘකාවට අදාළ ඔබේ KP පොත් වල පිටු; සෑම නීතියක්ම පොත සමඟ සසඳා බලන්න.

**උපදෙස:** පොරොන්දුව 🟢 + කාලය 🟢 + පාලක ග්‍රහ ගැළපීම = හොඳ තහවුරුවකි. පොරොන්දුව 🔴 නම් දශාව කුමක් වුවත් එම ප්‍රතිඵලය අඩුය.

*භාවිතා වන නීති `kp_engine.TOPICS` හි ඇත – ඔබේ පොත් වලට අනුව භාව ලැයිස්තු සංස්කරණය කරන්න. ජ්‍යොතිෂය මගපෙන්වීමක් පමණි; සෞඛ්‍ය, නීතිමය හෝ මූල්‍ය තීරණ සඳහා තනිවම මෙය මත රඳා නොසිටින්න.*
"""},
}