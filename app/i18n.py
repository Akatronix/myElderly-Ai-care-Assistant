"""Translations for the five supported languages.

Codes: en (English), yo (Yoruba), ig (Igbo), ha (Hausa), pcm (Nigerian Pidgin).
Missing keys fall back to English. Have a native speaker review these before
real-world use, especially the medical wording.
"""

LANGUAGES = [
    {"code": "en", "short": "EN", "name": "English", "html": "en"},
    {"code": "yo", "short": "YOR", "name": "Yorùbá", "html": "yo"},
    {"code": "ig", "short": "IG", "name": "Igbo", "html": "ig"},
    {"code": "ha", "short": "HA", "name": "Hausa", "html": "ha"},
    {"code": "pcm", "short": "PCM", "name": "Pidgin", "html": "en"},
]
CODES = [l["code"] for l in LANGUAGES]

# Language names used when instructing the LLM.
LLM_LANGUAGE_NAMES = {
    "en": "clear, simple English",
    "yo": "clear, natural Yoruba (with correct tone marks where possible)",
    "ig": "clear, natural Igbo",
    "ha": "clear, natural Hausa",
    "pcm": "natural Nigerian Pidgin English",
}


def _t(en, yo, ig, ha, pcm):
    return {"en": en, "yo": yo, "ig": ig, "ha": ha, "pcm": pcm}


TRANSLATIONS = {
    # navigation
    "nav_dashboard": _t("Dashboard", "Ojúlé Àkọ́kọ́", "Ibe Isi", "Shafin Farko", "Dashboard"),
    "nav_voice": _t("Voice Assistant", "Olùrànlọ́wọ́ Ohùn", "Onye Enyemaka Olu", "Mataimakin Murya", "Voice Assistant"),
    "nav_medicine": _t("Medicine", "Oògùn", "Ọgwụ", "Magani", "Medicine"),
    "nav_health": _t("Health", "Ìlera", "Ahụ ike", "Lafiya", "Health"),
    "nav_alert": _t("Alert", "Ìkìlọ̀", "Ịdọ aka ná ntị", "Faɗakarwa", "Alert"),
    "nav_alarm": _t("Alarm", "Aago Ìrántí", "Elekere Ncheta", "Ƙararrawa", "Alarm"),
    "nav_settings": _t("Settings", "Ètò", "Ntọala", "Saituna", "Settings"),
    "search_ph": _t("Search or ask...", "Wá tàbí béèrè...", "Chọọ ma ọ bụ jụọ...", "Nema ko ka tambaya...", "Search or ask..."),
    "online": _t("Online", "Intanẹẹti wà", "Ịntanetị dị", "Intanet na nan", "Internet dey"),
    "offline": _t("Offline", "Kò sí intanẹẹti", "Ịntanetị adịghị", "Babu intanet", "No internet"),
    "fullscreen": _t("Full screen", "Kún ojú-ìwé", "Ihuenyo zuru ezu", "Cikakken allo", "Full screen"),
    # dashboard
    "dashboard_title": _t("Dashboard", "Ojúlé Àkọ́kọ́", "Ibe Isi", "Shafin Farko", "Dashboard"),
    "dashboard_sub": _t(
        "Care overview for {name} today.",
        "Àkópọ̀ ìtọ́jú {name} fún òní.",
        "Nchịkọta nlekọta {name} taa.",
        "Taƙaitaccen kulawar {name} na yau.",
        "Na {name} care overview be dis for today.",
    ),
    "heartbeat": _t("Heartbeat", "Ìlù ọkàn", "Ụda obi", "Bugun zuciya", "Heartbeat"),
    "body_temp": _t("Body temperature", "Ooru ara", "Ọkụ ahụ́", "Zafin jiki", "Body temperature"),
    "normal": _t("Normal", "Déédé", "Ọ dị mma", "Daidai", "Normal"),
    "high": _t("High", "Ó ga jù", "Ọ dị elu", "Ya yi yawa", "High"),
    "low": _t("Low", "Ó kéré jù", "Ọ dị ala", "Ya yi ƙasa", "Low"),
    "medicine_level": _t("Medicine level (7 days)", "Ìwọ̀n oògùn (ọjọ́ méje)", "Ọkwa ịṅụ ọgwụ (ụbọchị 7)", "Matakin shan magani (kwanaki 7)", "Medicine level (7 days)"),
    "last_7_days": _t("Last 7 days", "Ọjọ́ méje tó kọjá", "Ụbọchị 7 gara aga", "Kwanaki 7 da suka wuce", "Last 7 days"),
    "health_trends": _t("Health Trends", "Ìṣesí Ìlera", "Ọnọdụ Ahụ ike", "Yanayin Lafiya", "Health Trends"),
    "last_24h": _t("Last 24 hours", "Wákàtí 24 tó kọjá", "Awa 24 gara aga", "Awanni 24 da suka wuce", "Last 24 hours"),
    "call_family": _t("Call family", "Pe ẹbí", "Kpọọ ezinụlọ", "Kira iyali", "Call family"),
    "talk": _t("Talk", "Sọ̀rọ̀", "Kwuo okwu", "Yi magana", "Talk"),
    "todays_medicine": _t("Today's medicine", "Oògùn òní", "Ọgwụ taa", "Magani na yau", "Today's medicine"),
    "recent_alerts": _t("Recent alerts", "Àwọn ìkìlọ̀ àìpẹ́", "Ọkwa ndị na-adịbeghị anya", "Faɗakarwar kwanan nan", "Recent alerts"),
    "view_all": _t("View all", "Wo gbogbo rẹ̀", "Lee ha niile", "Duba duka", "View all"),
    # voice
    "talk_title": _t("Talk to your assistant", "Bá olùrànlọ́wọ́ rẹ sọ̀rọ̀", "Gwa onye enyemaka gị okwu", "Yi magana da mataimakinka", "Talk to your assistant"),
    "tap_to_talk": _t("Tap to talk", "Tẹ̀ láti sọ̀rọ̀", "Pịa ka ị kwuo okwu", "Danna ka ka yi magana", "Press to talk"),
    "tap_to_stop": _t("Tap when you finish", "Tẹ̀ nígbà tí o bá parí", "Pịa mgbe ị kwusịrị", "Danna idan ka gama", "Press when you don finish"),
    "listening": _t("Listening...", "Mò ń gbọ́...", "Ana m ege ntị...", "Ina saurara...", "I dey listen..."),
    "thinking": _t("Thinking...", "Mò ń ronú...", "Ana m eche echiche...", "Ina tunani...", "I dey think..."),
    "speaking": _t("Speaking...", "Mò ń sọ̀rọ̀...", "Ana m ekwu okwu...", "Ina magana...", "I dey talk..."),
    "type_ph": _t("Type your message here...", "Kọ ọ̀rọ̀ rẹ síbí...", "Dee ozi gị ebe a...", "Rubuta saƙonka a nan...", "Type wetin you wan talk..."),
    "send": _t("Send", "Fi ranṣẹ́", "Ziga", "Aika", "Send"),
    "voice_hint": _t(
        "Try: \"Which medicine should I take now?\" or \"Wake me at 7 in the morning\".",
        "Gbìyànjú: \"Oògùn wo ni kí n mu báyìí?\" tàbí \"Jí mi ní aago méje òwúrọ̀\".",
        "Nwaa ịsị: \"Kedu ọgwụ m kwesịrị ịṅụ ugbu a?\" ma ọ bụ \"Kpọtee m n'elekere asaa nke ụtụtụ\".",
        "Gwada ka ce: \"Wane magani zan sha yanzu?\" ko \"Tashe ni da ƙarfe bakwai na safe\".",
        "Try talk: \"Which medicine I suppose take now?\" or \"Wake me by 7 for morning\".",
    ),
    "mic_error": _t(
        "Cannot use the microphone. Allow microphone access and open this page via localhost or HTTPS.",
        "Kò lè lo gbohùngbohùn. Gba ààyè gbohùngbohùn, kí o sì ṣí ojú-ìwé yìí lórí localhost tàbí HTTPS.",
        "Enweghị ike iji igwe ndekọ olu. Kwe ka ejiri ya ma mepee ibe a na localhost ma ọ bụ HTTPS.",
        "Ba a iya amfani da makirufo ba. Ba da izini kuma buɗe shafin ta localhost ko HTTPS.",
        "I no fit use microphone. Allow microphone and open dis page for localhost or HTTPS.",
    ),
    "no_speech": _t("I did not hear anything. Please try again.", "Mi ò gbọ́ nǹkan kan. Jọ̀wọ́ gbìyànjú lẹ́ẹ̀kan sí i.", "Anụghị m ihe ọ bụla. Biko nwaa ọzọ.", "Ban ji komai ba. Don Allah a sake gwadawa.", "I no hear anything. Abeg try again."),
    "assistant_error": _t("Sorry, something went wrong. Please try again.", "Ẹ máa bínú, nǹkan kan ṣẹlẹ̀. Jọ̀wọ́ gbìyànjú lẹ́ẹ̀kan sí i.", "Ndo, ihe ezighi ezi mere. Biko nwaa ọzọ.", "Yi haƙuri, an sami matsala. Don Allah a sake gwadawa.", "Sorry, something don happen. Abeg try again."),
    "you": _t("You", "Ìwọ", "Gị", "Kai", "You"),
    "assistant": _t("Assistant", "Olùrànlọ́wọ́", "Onye enyemaka", "Mataimaki", "Assistant"),
    "play_reply": _t("Play reply", "Gbọ́ èsì", "Gee ntị n'azịza", "Saurari amsa", "Play reply"),
    "action_set_alarm": _t("Alarm set for {time}", "A ṣètò aago fún {time}", "Edobere elekere maka {time}", "An saita ƙararrawa don {time}", "Alarm don set for {time}"),
    "action_medicine_taken": _t("{name} marked as taken", "A ti sàmì {name} pé a ti mú un", "Edepụtala na aṅụọla {name}", "An yi alamar an sha {name}", "{name} don mark as taken"),
    # medicine
    "mark_taken": _t("Taken", "Mo ti mú un", "Aṅụọla m ya", "Na sha", "I don take am"),
    "taken_at": _t("Taken at {time}", "Ti mú ní {time}", "Aṅụrụ n'oge {time}", "An sha da {time}", "Taken by {time}"),
    "due_now": _t("Due now", "Àsìkò ti tó", "Oge eruola", "Lokaci ya yi", "Time don reach"),
    "upcoming": _t("Upcoming", "Ó ń bọ̀", "Na-abịa", "Mai zuwa", "Wey dey come"),
    "missed": _t("Missed", "Ó ti kọjá", "Agafere", "An wuce", "Missed"),
    "no_medicine_today": _t("No medicine scheduled today.", "Kò sí oògùn fún òní.", "Enweghị ọgwụ taa.", "Babu magani a yau.", "No medicine for today."),
    "add_medicine": _t("Add medicine", "Fi oògùn kún", "Tinye ọgwụ", "Ƙara magani", "Add medicine"),
    "med_name": _t("Medicine name", "Orúkọ oògùn", "Aha ọgwụ", "Sunan magani", "Medicine name"),
    "med_dose": _t("Dose (e.g. 1 tablet)", "Ìwọ̀n (bíi káàpẹ́ẹ̀sù 1)", "Oke (dị ka mbadamba 1)", "Adadi (misali kwaya 1)", "Dose (e.g. 1 tablet)"),
    "med_times": _t("Times, 24h (e.g. 08:00, 20:00)", "Àkókò, 24h (bíi 08:00, 20:00)", "Oge, 24h (dị ka 08:00, 20:00)", "Lokuta, 24h (misali 08:00, 20:00)", "Time, 24h (e.g. 08:00, 20:00)"),
    "med_notes": _t("Notes (optional)", "Àkíyèsí (tí o bá fẹ́)", "Ndetu (ma ọ bụrụ na ịchọrọ)", "Bayani (zaɓi)", "Notes (optional)"),
    "save": _t("Save", "Fipamọ́", "Chekwaa", "Ajiye", "Save"),
    "cancel": _t("Cancel", "Fagilé", "Kagbuo", "Soke", "Cancel"),
    "delete": _t("Delete", "Pa rẹ́", "Hichapụ", "Share", "Delete"),
    "all_medicines": _t("All medicines", "Gbogbo oògùn", "Ọgwụ niile", "Dukan magunguna", "All medicines"),
    "no_medicines": _t("No medicines added yet.", "A kò tíì fi oògùn kankan kún.", "Etinyebeghị ọgwụ ọ bụla.", "Ba a ƙara magani ba tukuna.", "No medicine dey yet."),
    "med_safety": _t(
        "Sample medicines are only examples. Enter the real prescription from the doctor.",
        "Àwọn oògùn àpẹẹrẹ jẹ́ àpẹẹrẹ nìkan. Fi oògùn gidi tí dókítà kọ sílẹ̀.",
        "Ọgwụ ndị a bụ ọmụmaatụ naanị. Tinye ọgwụ ezi dọkịta dere.",
        "Magungunan misali ne kawai. Shigar da ainihin takardar likita.",
        "Sample medicine na example only. Put the real one wey doctor write.",
    ),
    # health
    "vitals_now": _t("Current readings", "Àwọn àmì ara báyìí", "Ihe ngosi ahụ ugbu a", "Karatun yanzu", "Current readings"),
    "normal_range": _t("Normal range", "Ìwọ̀n déédé", "Oke nkịtị", "Matsakaicin al'ada", "Normal range"),
    "simulated": _t(
        "Showing test data. Connect the sensor hardware to see real readings.",
        "Dátà àyẹ̀wò ni à ń fi hàn. So ẹ̀rọ sensọ pọ̀ láti rí òótọ́.",
        "Na-egosi data nnwale. Jikọọ ngwa sensọ ka ịhụ eziokwu.",
        "Ana nuna bayanan gwaji. Haɗa na'urar firikwensin don ganin ainihin karatu.",
        "Dem dey show test data. Connect the sensor hardware make you see real one.",
    ),
    "hardware_title": _t("Connect the sensor hardware", "So ẹ̀rọ sensọ pọ̀", "Jikọọ ngwa sensọ", "Haɗa na'urar firikwensin", "Connect the sensor hardware"),
    "hardware_desc": _t(
        "Your device can send readings to this endpoint:",
        "Ẹ̀rọ rẹ lè fi àwọn ìwọ̀n ránṣẹ́ sí ibí yìí:",
        "Ngwa gị nwere ike izipu ihe e gụrụ n'ebe a:",
        "Na'urarka na iya aika karatu zuwa wannan wuri:",
        "Your device fit send reading go dis place:",
    ),
    # alerts
    "no_alerts": _t("No alerts. All is well.", "Kò sí ìkìlọ̀. Ohun gbogbo dára.", "Enweghị ọkwa. Ihe niile dị mma.", "Babu faɗakarwa. Komai lafiya.", "No alert. Everything dey fine."),
    "acknowledge": _t("Acknowledge", "Gbà á", "Nabata", "Amince", "Okay"),
    "send_test_alert": _t("Send test alert", "Fi ìkìlọ̀ àyẹ̀wò ránṣẹ́", "Zipu ọkwa nnwale", "Aika gwajin faɗakarwa", "Send test alert"),
    "sms_call_soon": _t(
        "SMS and phone-call alerts: coming soon (hardware module).",
        "Ìkìlọ̀ SMS àti ìpè fóònù: ó ń bọ̀ láìpẹ́.",
        "Ọkwa SMS na ekwentị: na-abịa n'oge na-adịghị anya.",
        "Faɗakarwar SMS da kiran waya: ana nan zuwa.",
        "SMS and phone call alert: e go soon come.",
    ),
    "sos": _t("Emergency", "Ìrànlọ́wọ́ kíákíá", "Enyemaka ngwa ngwa", "Taimako na gaggawa", "Emergency"),
    "sos_confirm": _t("Send an emergency alert to the family?", "Ṣé kí n fi ìkìlọ̀ pàjáwìrì ránṣẹ́ sí ẹbí?", "Zipu ọkwa mberede nye ezinụlọ?", "A aika faɗakarwar gaggawa ga iyali?", "Make I send emergency alert to family?"),
    "yes_send": _t("Yes, send", "Bẹ́ẹ̀ni, fi ránṣẹ́", "Ee, zipu", "Ee, aika", "Yes, send"),
    "emergency_sent": _t("Emergency alert recorded.", "A ti ṣàkọsílẹ̀ ìkìlọ̀ pàjáwìrì.", "Edeela ọkwa mberede.", "An rubuta faɗakarwar gaggawa.", "Emergency alert don record."),
    "phone_not_impl": _t(
        "Phone calls are not implemented yet. Coming soon.",
        "A kò tíì ṣe ìpè fóònù. Ó ń bọ̀ láìpẹ́.",
        "Akwadobeghị ekwentị. Na-abịa n'oge na-adịghị anya.",
        "Ba a riga an kammala kiran waya ba. Ana nan zuwa.",
        "Phone call never ready yet. E go soon come.",
    ),
    "alert_hr_high": _t("Heart rate is high: {v} BPM", "Ìlù ọkàn ga jù: {v} BPM", "Ụda obi dị elu: {v} BPM", "Bugun zuciya ya yi yawa: {v} BPM", "Heartbeat don high: {v} BPM"),
    "alert_hr_low": _t("Heart rate is low: {v} BPM", "Ìlù ọkàn kéré jù: {v} BPM", "Ụda obi dị ala: {v} BPM", "Bugun zuciya ya yi ƙasa: {v} BPM", "Heartbeat don low: {v} BPM"),
    "alert_temp_high": _t("Body temperature is high: {v} °C", "Ooru ara ga jù: {v} °C", "Ọkụ ahụ́ dị elu: {v} °C", "Zafin jiki ya yi yawa: {v} °C", "Body temperature don high: {v} °C"),
    "alert_temp_low": _t("Body temperature is low: {v} °C", "Ooru ara kéré jù: {v} °C", "Ọkụ ahụ́ dị ala: {v} °C", "Zafin jiki ya yi ƙasa: {v} °C", "Body temperature don low: {v} °C"),
    "alert_test": _t("Test alert", "Ìkìlọ̀ àyẹ̀wò", "Ọkwa nnwale", "Gwajin faɗakarwa", "Test alert"),
    "alert_emergency": _t("Emergency button pressed", "A tẹ bọ́tìnì pàjáwìrì", "Pịa bọtịnụ mberede", "An danna maɓallin gaggawa", "Emergency button don press"),
    "alert_assistant": _t("Emergency requested through the voice assistant", "A béèrè ìrànlọ́wọ́ pàjáwìrì nípasẹ̀ olùrànlọ́wọ́ ohùn", "Arịọla enyemaka mberede site na onye enyemaka olu", "An nemi taimakon gaggawa ta mataimakin murya", "Emergency don request through voice assistant"),
    # alarm
    "new_alarm": _t("New alarm", "Aago tuntun", "Elekere ọhụrụ", "Sabuwar ƙararrawa", "New alarm"),
    "alarm_label": _t("Label", "Orúkọ", "Aha", "Suna", "Label"),
    "alarm_time": _t("Time", "Àkókò", "Oge", "Lokaci", "Time"),
    "repeat": _t("Repeat (empty = every day)", "Tún ṣe (òfo = ojoojúmọ́)", "Mee ọzọ (efu = kwa ụbọchị)", "Maimaita (fanko = kowace rana)", "Repeat (empty = every day)"),
    "every_day": _t("Every day", "Ojoojúmọ́", "Kwa ụbọchị", "Kowace rana", "Every day"),
    "add_alarm": _t("Add alarm", "Fi aago kún", "Tinye elekere", "Ƙara ƙararrawa", "Add alarm"),
    "alarm_ringing": _t("Alarm", "Aago ń dún", "Elekere na-ada", "Ƙararrawa na ƙara", "Alarm dey ring"),
    "dismiss": _t("Stop", "Pa á dákẹ́", "Kwụsị", "Kashe", "Stop am"),
    "snooze": _t("Remind me in 5 min", "Rán mi létí lẹ́yìn ìṣẹ́jú 5", "Cheta m n'ime nkeji 5", "Sake tuna min bayan minti 5", "Remind me after 5 min"),
    "medicine_time": _t("Time for your medicine", "Àsìkò oògùn rẹ ti tó", "Oge ọgwụ gị eruola", "Lokacin shan maganinka ya yi", "Time don reach to take your medicine"),
    "no_alarms": _t("No alarms yet.", "Kò sí aago kankan.", "Enweghị elekere ọ bụla.", "Babu ƙararrawa tukuna.", "No alarm yet."),
    "sound_hint": _t(
        "Tap anywhere once so the browser is allowed to play alarm sounds.",
        "Tẹ ibikíbi lẹ́ẹ̀kan kí aago lè dún.",
        "Pịa ebe ọ bụla otu ugboro ka elekere nwee ike ịda.",
        "Danna ko'ina sau ɗaya don ƙararrawa ta iya yin sauti.",
        "Tap anywhere once make alarm fit sound.",
    ),
    "test_sound": _t("Test sound", "Gbìyànjú ohùn", "Nwaa olu", "Gwada sauti", "Test sound"),
    # settings
    "elder_name": _t("Name of the person being cared for", "Orúkọ ẹni tí a ń tọ́jú", "Aha onye a na-elekọta", "Sunan wanda ake kulawa", "Name of person wey we dey take care"),
    "family_phone": _t("Family phone number", "Nọ́ńbà fóònù ẹbí", "Ọnụ ọgụgụ ekwentị ezinụlọ", "Lambar wayar iyali", "Family phone number"),
    "language": _t("Language", "Èdè", "Asụsụ", "Harshe", "Language"),
    "large_text": _t("Large text", "Ọ̀rọ̀ ńlá", "Mkpụrụedemede buru ibu", "Manyan rubutu", "Big text"),
    "saved": _t("Saved", "A ti fipamọ́", "Echekwara", "An ajiye", "Don save"),
    "coming_soon": _t("Coming soon", "Ó ń bọ̀ láìpẹ́", "Na-abịa n'oge na-adịghị anya", "Ana nan zuwa", "E go soon come"),
    "error_generic": _t("Something went wrong.", "Nǹkan kan ṣẹlẹ̀.", "Ihe ezighi ezi mere.", "An sami matsala.", "Something don happen."),
}

DAYS = {
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "yo": ["Ajé", "Ìsẹ́gun", "Ọjọ́rú", "Ọjọ́bọ", "Ẹtì", "Àbámẹ́ta", "Àìkú"],
    "ig": ["Mọnde", "Tiuzdee", "Wenezdee", "Tọọzdee", "Fraịdee", "Satọdee", "Sọnde"],
    "ha": ["Lit", "Tal", "Lar", "Alh", "Jum", "Asa", "Lah"],
    "pcm": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
}


def translate(key, lang="en", **kwargs):
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    text = entry.get(lang) or entry["en"]
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def js_bundle(lang):
    bundle = {k: (v.get(lang) or v["en"]) for k, v in TRANSLATIONS.items()}
    bundle["days"] = DAYS.get(lang, DAYS["en"])
    return bundle
