"""Extra Sinhala/English strings (report, download, Gemini). Imported by app.py after i18n.
R(key, lang, **kw) gives text in an explicit language (used by the report builder)."""
import i18n


def R(key, lang, **kw):
    s = i18n.TR[key][lang]
    return s.format(**kw) if kw else s


HOUSE_MEANING = {
    "en": ["self, body, personality", "family, speech, accumulated wealth", "courage, siblings, short journeys",
           "home, mother, property, vehicles, education", "children, intellect, speculation",
           "service, debts, disease, enemies", "marriage, spouse, partnerships",
           "obstacles, longevity, sudden events", "fortune, higher learning, long journeys",
           "career, status, profession", "gains, fulfilment of desires", "losses, expenses, foreign lands, isolation"],
    "si": ["ස්වයං, ශරීරය, පෞරුෂය", "පවුල, කථනය, රැස්කළ ධනය", "ධෛර්යය, සහෝදරයන්, කෙටි ගමන්",
           "නිවස, මව, දේපළ, වාහන, අධ්‍යාපනය", "දරුවන්, බුද්ධිය, සමපේක්ෂණ",
           "සේවය, ණය, රෝග, සතුරන්", "විවාහය, කලත්‍රයා, හවුල්කාරිත්ව",
           "බාධක, ආයුෂ, හදිසි සිදුවීම්", "වාසනාව, උසස් අධ්‍යාපනය, දුර ගමන්",
           "වෘත්තිය, තත්ත්වය, රැකියාව", "ලාභ, ආශා ඉටුවීම", "පාඩු, වියදම්, විදේශ, හුදෙකලාව"],
}

i18n.TR.update({
    # ---- UI
    "custom": {"en": "Custom (enter below)", "si": "වෙනත් (පහත ඇතුළත් කරන්න)"},
    "tab_report": {"en": "📄 Full report (PDF)", "si": "📄 සම්පූර්ණ වාර්තාව (PDF)"},
    "rep_intro": {"en": "Create a complete KP analysis of this horoscope in the selected language and download it.",
                  "si": "තෝරාගත් භාෂාවෙන් මෙම කේන්දරයේ සම්පූර්ණ KP විශ්ලේෂණයක් සාදා බාගත කරන්න."},
    "rep_mode": {"en": "Report writer", "si": "වාර්තාව සකසන ක්‍රමය"},
    "rep_mode_rules": {"en": "KP rules engine + database (offline)", "si": "KP නීති එන්ජිම + database (අන්තර්ජාලය අවශ්‍ය නැත)"},
    "rep_mode_gemini": {"en": "Gemini AI (more detailed, needs API key)", "si": "Gemini AI (වඩා විස්තරාත්මක, API key අවශ්‍යයි)"},
    "rep_key": {"en": "Gemini API key", "si": "Gemini API key"},
    "rep_key_help": {"en": "Used only in this session, never saved. Birth details and chart facts are sent to Google.",
                     "si": "මෙම සැසිය තුළ පමණක් භාවිතා වේ, සුරැකෙන්නේ නැත. උපත් තොරතුරු සහ කේන්දර දත්ත Google වෙත යැවේ."},
    "rep_model": {"en": "Gemini model", "si": "Gemini මාදිලිය"},
    "rep_btn": {"en": "📄 Generate report", "si": "📄 වාර්තාව සාදන්න"},
    "rep_working": {"en": "Preparing report...", "si": "වාර්තාව සකසමින්..."},
    "rep_ready": {"en": "Report ready.", "si": "වාර්තාව සූදානම්."},
    "rep_dl_pdf": {"en": "⬇️ Download PDF", "si": "⬇️ PDF බාගන්න"},
    "rep_dl_html": {"en": "⬇️ Download HTML (print to PDF in browser)", "si": "⬇️ HTML බාගන්න (browser එකෙන් PDF ලෙස print කළ හැක)"},
    "rep_err_pdf": {"en": "PDF could not be created: {e}", "si": "PDF සෑදීමට නොහැකි විය: {e}"},
    "rep_err_gemini": {"en": "Gemini failed ({e}). A rule-based report was created instead.",
                       "si": "Gemini අසාර්ථකයි ({e}). ඒ වෙනුවට KP නීති මත පදනම් වාර්තාවක් සාදන ලදී."},
    "rep_stale": {"en": "This report was made in another language. Press Generate again.",
                  "si": "මෙම වාර්තාව වෙනත් භාෂාවකින් සාදා ඇත. නැවත 'සාදන්න' ඔබන්න."},
    "rep_need_key": {"en": "Enter the Gemini API key.", "si": "Gemini API key ඇතුළත් කරන්න."},
    "rep_preview": {"en": "Preview", "si": "පෙරදසුන"},
    "rep_nofont": {"en": "No Sinhala font found. Put NotoSansSinhala-Regular.ttf in the 'fonts' folder (or install Iskoola Pota).",
                   "si": "සිංහල font නැත. NotoSansSinhala-Regular.ttf 'fonts' folder එකට දමන්න (හෝ Iskoola Pota ස්ථාපනය කරන්න)."},
    "rep_nolatin": {"en": "No Latin font found. Put DejaVuSans.ttf in the 'fonts' folder.",
                    "si": "ඉංග්‍රීසි font නැත. DejaVuSans.ttf 'fonts' folder එකට දමන්න."},

    # ---- report text
    "r_title": {"en": "KP Horoscope Analysis Report", "si": "කේ.පී. කේන්දර විශ්ලේෂණ වාර්තාව"},
    "r_basic": {"en": "Birth details", "si": "උපත් තොරතුරු"},
    "r_basic_line": {"en": "Name: {name} | Born: {dt} | Place: {place} (lat {lat}, lon {lon}, UTC {tz})",
                     "si": "නම: {name} | උපත: {dt} | ස්ථානය: {place} (අක්ෂාංශ {lat}, දේශාංශ {lon}, UTC {tz})"},
    "r_asc_line": {"en": "Lagna: {lagna}, star lord {star}, sub lord {sub}. Moon in {msign}, nakshatra {nak}. KP ayanamsa {ay}.",
                   "si": "ලග්නය: {lagna}, නැකත් අධිපති {star}, උප අධිපති {sub}. චන්ද්‍රයා {msign} රාශියේ, {nak} නැකතේ. KP අයනාංශය {ay}."},
    "r_method_h": {"en": "Method used", "si": "භාවිතා කළ ක්‍රමය"},
    "r_method": {"en": "Krishnamurti Paddhati (KP): Placidus house cusps, Krishnamurti ayanamsa, star lord / sub lord / sub-sub lord, "
                       "4-level significators, Vimshottari dasha-bhukti and ruling planets. All judgements below follow this method only.",
                 "si": "කෘෂ්ණමූර්ති පද්ධතිය (KP): Placidus භාව සන්ධි, කෘෂ්ණමූර්ති අයනාංශය, නැකත් / උප / උප-උප අධිපති, "
                       "මට්ටම් 4 කාරක ක්‍රමය, විංශෝත්තරී දශා-භුක්ති සහ පාලක ග්‍රහයන්. පහත සියලු තීරණ මෙම ක්‍රමය අනුව පමණි."},
    "r_chart_h": {"en": "Planet positions", "si": "ග්‍රහ පිහිටීම්"},
    "r_cusp_h": {"en": "House cusps", "si": "භාව සන්ධි"},
    "r_sig_h": {"en": "Significators (KP 4 levels)", "si": "කාරක ග්‍රහයන් (KP මට්ටම් 4)"},
    "r_dasha_h": {"en": "Dasha periods", "si": "දශා කාල"},
    "r_dasha_now": {"en": "Running period: Mahadasha {md}, Antardasha {ad}, Pratyantar {pd} ({a} to {b}).",
                    "si": "දැනට පවතින කාලය: මහා දශාව {md}, අන්තර් දශාව {ad}, ප්‍රත්‍යන්තරය {pd} ({a} සිට {b} දක්වා)."},
    "r_summary_h": {"en": "Summary of life areas", "si": "ජීවිත ක්ෂේත්‍ර සාරාංශය"},
    "r_rp_h": {"en": "Ruling planets (at the time of report)", "si": "පාලක ග්‍රහයන් (වාර්තාව සෑදූ මොහොතේ)"},
    "r_detail_h": {"en": "Detailed analysis by life area", "si": "ජීවිත ක්ෂේත්‍ර අනුව සවිස්තර විශ්ලේෂණය"},
    "r_topic_intro": {"en": "Cusp {n} ({topic}) has sub lord {sub}, placed in the star of {star}. {sub} signifies houses: {h}.",
                      "si": "{n} වන භාව සන්ධිය ({topic}) හි උප අධිපති {sub} වන අතර ඔහු {star} ගේ නැකතේ සිටී. {sub} කාරක වන භාව: {h}."},
    "r_fav": {"en": "Favourable houses needed {need}: matched {m}.", "si": "අවශ්‍ය හිතකර භාව {need}: ගැළපෙන භාව {m}."},
    "r_deny": {"en": "Blocking houses {need}: present {m}.", "si": "බාධක භාව {need}: ඇති භාව {m}."},
    "r_hm": {"en": "House meanings: {t}.", "si": "භාව අර්ථ: {t}."},
    "r_verdict_Strong": {"en": "Verdict: strongly promised. When a favourable dasha-bhukti runs, the result can be expected.",
                         "si": "නිගමනය: ශක්තිමත්ව පොරොන්දු වේ. හිතකර දශා-භුක්තියක් පවතින විට ප්‍රතිඵලය බලාපොරොත්තු විය හැක."},
    "r_verdict_Moderate": {"en": "Verdict: partly promised. The result comes with delay or effort, mostly in the strongest periods.",
                           "si": "නිගමනය: අර්ධ වශයෙන් පොරොන්දු වේ. ප්‍රමාදයක් හෝ උත්සාහයක් සමඟ, බොහෝවිට ශක්තිමත්ම කාලවලදී ලැබේ."},
    "r_verdict_Weak": {"en": "Verdict: weakly promised. The result is unlikely or very difficult whatever the dasha.",
                       "si": "නිගමනය: දුර්වලව පොරොන්දු වේ. දශාව කුමක් වුවත් ප්‍රතිඵලය අඩු හෝ ඉතා දුෂ්කර ය."},
    "r_windows_h": {"en": "Favourable periods (next {y} years)", "si": "හිතකර කාල (ඉදිරි වසර {y})"},
    "r_window_item": {"en": "{lvl}: {a} to {b} ({md}-{ad}){rp}", "si": "{lvl}: {a} සිට {b} දක්වා ({md}-{ad}){rp}"},
    "r_rp_suffix": {"en": " - ruling planet match: {x}", "si": " - පාලක ග්‍රහ ගැළපීම: {x}"},
    "r_no_windows": {"en": "No favourable dasha-bhukti in this period.", "si": "මෙම කාලයේ හිතකර දශා-භුක්තියක් නැත."},
    "r_now_in": {"en": "The running dasha-bhukti ({md}-{ad}) is favourable for this area.",
                 "si": "දැනට පවතින දශා-භුක්තිය ({md}-{ad}) මෙම ක්ෂේත්‍රයට හිතකරයි."},
    "r_now_out": {"en": "The running dasha-bhukti ({md}-{ad}) is not specially favourable for this area.",
                  "si": "දැනට පවතින දශා-භුක්තිය ({md}-{ad}) මෙම ක්ෂේත්‍රයට විශේෂයෙන් හිතකර නොවේ."},
    "r_book_h": {"en": "Book references (database)", "si": "පොත් යොමු (database)"},
    "r_no_book": {"en": "No book reference found in the database for this topic.", "si": "මෙම මාතෘකාවට database හි පොත් යොමු නොමැත."},
    "r_ai_h": {"en": "Detailed interpretation (AI-written from the KP facts above)",
               "si": "සවිස්තර අර්ථකථනය (ඉහත KP දත්ත මත AI මගින් ලියන ලදී)"},
    "r_disc": {"en": "Astrology is guidance, not certainty. Do not rely on it alone for health, legal or financial decisions.",
               "si": "ජ්‍යොතිෂය මගපෙන්වීමක් පමණි. සෞඛ්‍ය, නීතිමය හෝ මූල්‍ය තීරණ සඳහා තනිවම මෙය මත රඳා නොසිටින්න."},
})