"""
UI strings, in the three languages, as one Python dict.

Why not Django's gettext catalogues: those need .po files compiled by the
`msgfmt` binary, which turns "add a word to a button" into a build step that
has to run on Windows, in CI and inside the image. This site's UI vocabulary is
about a hundred short strings that only ever change when a feature changes, so
a dict costs one import and no toolchain, and an agent can add a language by
adding a column here.

Everything a *visitor* reads that is not chrome — a project title, a post, a
bio — lives in the database instead (see apps/content/models.py). This file is
only the furniture: buttons, labels, section headings.

Read it from a template with {% t "nav.projects" %}.
"""

from __future__ import annotations

from django.conf import settings
from django.utils.translation import get_language

DEFAULT_LANG = settings.LANGUAGE_CODE

STRINGS: dict[str, dict[str, str]] = {
    # ── chrome ────────────────────────────────────────────────────────────
    "nav.home": {"fa": "خانه", "en": "Home", "de": "Start"},
    "nav.projects": {"fa": "نمونه‌کارها", "en": "Work", "de": "Arbeiten"},
    "nav.writing": {"fa": "نوشته‌ها", "en": "Writing", "de": "Blog"},
    "nav.about": {"fa": "درباره", "en": "About", "de": "Über mich"},
    "nav.contact": {"fa": "تماس", "en": "Contact", "de": "Kontakt"},
    "nav.resume": {"fa": "رزومه", "en": "Résumé", "de": "Lebenslauf"},
    "nav.card": {"fa": "کارت", "en": "Card", "de": "Karte"},
    "nav.menu": {"fa": "منو", "en": "Menu", "de": "Menü"},
    "nav.close": {"fa": "بستن", "en": "Close", "de": "Schließen"},
    "nav.skip": {"fa": "پرش به محتوا", "en": "Skip to content", "de": "Zum Inhalt springen"},
    "nav.language": {"fa": "زبان", "en": "Language", "de": "Sprache"},
    "nav.theme": {"fa": "تم", "en": "Theme", "de": "Design"},
    "theme.system": {"fa": "سیستم", "en": "System", "de": "System"},
    "theme.light": {"fa": "روشن", "en": "Light", "de": "Hell"},
    "theme.dark": {"fa": "تاریک", "en": "Dark", "de": "Dunkel"},

    # ── home ──────────────────────────────────────────────────────────────
    "home.available": {"fa": "آمادهٔ همکاری", "en": "Open to work", "de": "Offen für Projekte"},
    "home.view_work": {"fa": "دیدن نمونه‌کارها", "en": "See my work", "de": "Arbeiten ansehen"},
    "home.contact_me": {"fa": "تماس با من", "en": "Get in touch", "de": "Kontakt aufnehmen"},
    "home.download_resume": {"fa": "دانلود رزومه", "en": "Download résumé", "de": "Lebenslauf laden"},
    "home.now": {"fa": "این روزها", "en": "Right now", "de": "Gerade jetzt"},
    "home.selected_work": {"fa": "کارهای منتخب", "en": "Selected work", "de": "Ausgewählte Projekte"},
    "home.all_projects": {"fa": "همهٔ نمونه‌کارها", "en": "All work", "de": "Alle Arbeiten"},
    "home.skills": {"fa": "مهارت‌ها و ابزارها", "en": "Skills and tools", "de": "Kompetenzen und Tools"},
    "home.experience": {"fa": "مسیر کاری", "en": "Career", "de": "Werdegang"},
    "home.full_resume": {"fa": "رزومهٔ کامل", "en": "Full résumé", "de": "Ganzer Lebenslauf"},
    "home.writing": {"fa": "نوشته‌ها", "en": "Writing", "de": "Aus dem Blog"},
    "home.all_writing": {"fa": "همهٔ نوشته‌ها", "en": "All posts", "de": "Alle Beiträge"},
    "home.cta_title": {"fa": "برندی دارید که باید دیده شود؟", "en": "Have a brand that should be seen?", "de": "Soll Ihre Marke gesehen werden?"},
    "home.cta_body": {
        "fa": "برای یک موقعیت شغلی، استراتژی محتوا، سناریوی کمپین یا مشاورهٔ شبکه‌های اجتماعی، همین حالا پیام بدهید.",
        "en": "For a content strategy, a campaign scenario or social media advice, send a message.",
        "de": "Für Content-Strategie, Kampagnen-Drehbuch oder Social-Media-Beratung — schreiben Sie mir.",
    },

    # ── projects ──────────────────────────────────────────────────────────
    "projects.title": {"fa": "نمونه‌کارها", "en": "Work", "de": "Arbeiten"},
    "projects.lede": {
        "fa": "کمپین‌ها و استراتژی‌های محتوایی که اجرا کرده‌ام، همراه با عددهای واقعی‌شان — مستقیم از اینسایتس اینستاگرام.",
        "en": "Campaigns and content strategies I have run, and the numbers they left behind.",
        "de": "Kampagnen und Content-Strategien, die ich umgesetzt habe — und die Zahlen, die sie hinterlassen haben.",
    },
    "projects.filter_all": {"fa": "همه", "en": "All", "de": "Alle"},
    "projects.empty": {"fa": "چیزی با این فیلتر پیدا نشد.", "en": "Nothing matches this filter.", "de": "Nichts gefunden."},
    "projects.role": {"fa": "نقش", "en": "Role", "de": "Rolle"},
    "projects.year": {"fa": "سال", "en": "Year", "de": "Jahr"},
    "projects.stack": {"fa": "کانال‌ها و ابزارها", "en": "Channels and tools", "de": "Kanäle und Tools"},
    "projects.problem": {"fa": "چالش", "en": "The challenge", "de": "Die Herausforderung"},
    "projects.outcome": {"fa": "نتیجه", "en": "Outcome", "de": "Ergebnis"},
    "projects.repo": {"fa": "منبع", "en": "Source", "de": "Quelle"},
    "projects.demo": {"fa": "دیدن محتوا", "en": "View the content", "de": "Inhalt ansehen"},
    "projects.next": {"fa": "نمونه‌کار بعدی", "en": "Next case study", "de": "Nächste Fallstudie"},
    "projects.back": {"fa": "بازگشت به نمونه‌کارها", "en": "Back to work", "de": "Zurück zu den Arbeiten"},

    # ── writing ───────────────────────────────────────────────────────────
    "blog.title": {"fa": "نوشته‌ها", "en": "Writing", "de": "Blog"},
    "blog.lede": {
        "fa": "یادداشت‌هایی دربارهٔ محتوا، شبکه‌های اجتماعی و چیزهایی که هر کمپین به من یاد می‌دهد.",
        "en": "Notes on content, social media, and what each campaign teaches me.",
        "de": "Notizen über Content, soziale Medien und das, was mir jede Kampagne beibringt.",
    },
    "blog.read_time": {"fa": "دقیقه مطالعه", "en": "min read", "de": "Min. Lesezeit"},
    "blog.back": {"fa": "بازگشت به نوشته‌ها", "en": "Back to writing", "de": "Zurück zum Blog"},
    "blog.empty": {"fa": "هنوز چیزی منتشر نشده.", "en": "Nothing published yet.", "de": "Noch nichts veröffentlicht."},
    "blog.share": {"fa": "اشتراک‌گذاری", "en": "Share", "de": "Teilen"},

    # ── about ─────────────────────────────────────────────────────────────
    "about.title": {"fa": "درباره من", "en": "About", "de": "Über mich"},
    "about.work": {"fa": "سابقهٔ کاری", "en": "Experience", "de": "Berufserfahrung"},
    "about.education": {"fa": "تحصیلات", "en": "Education", "de": "Ausbildung"},
    "about.present": {"fa": "اکنون", "en": "Present", "de": "Heute"},

    # ── contact ───────────────────────────────────────────────────────────
    "contact.title": {"fa": "تماس", "en": "Contact", "de": "Kontakt"},
    "contact.lede": {
        "fa": "از هر کدام از راه‌های زیر می‌توانید با من در تماس باشید. برای پیام مفصل‌تر، فرم پایین سریع‌ترین راه است.",
        "en": "Any of these reaches me. For anything longer, the form below is quickest.",
        "de": "Jeder dieser Wege erreicht mich. Für Längeres ist das Formular am schnellsten.",
    },
    "contact.direct": {"fa": "راه‌های مستقیم", "en": "Direct channels", "de": "Direkte Wege"},
    "contact.form": {"fa": "پیام بفرستید", "en": "Send a message", "de": "Nachricht senden"},
    "contact.name": {"fa": "نام", "en": "Name", "de": "Name"},
    "contact.email": {"fa": "ایمیل", "en": "Email", "de": "E-Mail"},
    "contact.subject": {"fa": "موضوع", "en": "Subject", "de": "Betreff"},
    "contact.message": {"fa": "پیام", "en": "Message", "de": "Nachricht"},
    "contact.send": {"fa": "ارسال پیام", "en": "Send message", "de": "Absenden"},
    "contact.sent": {
        "fa": "پیام شما رسید. به‌زودی جواب می‌دهم.",
        "en": "Your message arrived. I will get back to you shortly.",
        "de": "Ihre Nachricht ist angekommen. Ich melde mich in Kürze.",
    },
    "contact.too_fast": {
        "fa": "یک پیام همین الان فرستادید. کمی صبر کنید.",
        "en": "You just sent one. Give it a minute.",
        "de": "Sie haben gerade eine gesendet. Einen Moment bitte.",
    },
    "contact.copy": {"fa": "کپی", "en": "Copy", "de": "Kopieren"},
    "contact.copied": {"fa": "کپی شد", "en": "Copied", "de": "Kopiert"},

    # ── card ──────────────────────────────────────────────────────────────
    "card.title": {"fa": "کارت ویزیت", "en": "Business card", "de": "Visitenkarte"},
    "card.add_contact": {"fa": "افزودن به مخاطبین", "en": "Add to contacts", "de": "Zu Kontakten"},
    "card.scan": {"fa": "این کد را اسکن کنید", "en": "Scan this code", "de": "Diesen Code scannen"},
    "card.share": {"fa": "اشتراک‌گذاری لینک", "en": "Share link", "de": "Link teilen"},
    "card.open_site": {"fa": "دیدن سایت کامل", "en": "Open full site", "de": "Ganze Website"},

    # ── resume ────────────────────────────────────────────────────────────
    "resume.title": {"fa": "رزومه", "en": "Résumé", "de": "Lebenslauf"},
    "resume.print": {"fa": "چاپ / PDF", "en": "Print / PDF", "de": "Drucken / PDF"},
    "resume.languages": {"fa": "زبان‌ها", "en": "Languages", "de": "Sprachen"},

    # ── errors and footer ─────────────────────────────────────────────────
    "err.404_title": {"fa": "این صفحه پیدا نشد", "en": "Page not found", "de": "Seite nicht gefunden"},
    "err.404_body": {
        "fa": "شاید نشانی عوض شده باشد. از خانه دوباره شروع کنید.",
        "en": "The address may have changed. Start again from the home page.",
        "de": "Die Adresse hat sich vielleicht geändert. Beginnen Sie auf der Startseite.",
    },
    "err.500_title": {"fa": "چیزی از سمت ما خراب شد", "en": "Something broke on our side", "de": "Auf unserer Seite ging etwas schief"},
    "err.500_body": {
        "fa": "خطا ثبت شد. کمی بعد دوباره تلاش کنید.",
        "en": "The error was logged. Please try again shortly.",
        "de": "Der Fehler wurde protokolliert. Bitte später erneut versuchen.",
    },
    "err.home": {"fa": "بازگشت به خانه", "en": "Back home", "de": "Zur Startseite"},
    "footer.rights": {"fa": "همهٔ حقوق محفوظ است.", "en": "All rights reserved.", "de": "Alle Rechte vorbehalten."},
    "footer.built": {"fa": "ساخته‌شده با جنگو", "en": "Built with Django", "de": "Gebaut mit Django"},

    # ── command palette ───────────────────────────────────────────────────
    "cmd.open": {"fa": "جست‌وجو", "en": "Search", "de": "Suche"},
    "cmd.placeholder": {"fa": "صفحه یا نمونه‌کار…", "en": "Page or case study…", "de": "Seite oder Fallstudie…"},
    "cmd.empty": {"fa": "نتیجه‌ای نبود", "en": "No results", "de": "Keine Treffer"},
    "cmd.pages": {"fa": "صفحه‌ها", "en": "Pages", "de": "Seiten"},
    "cmd.actions": {"fa": "میان‌برها", "en": "Shortcuts", "de": "Aktionen"},
    "cmd.move": {"fa": "جابه‌جایی", "en": "move", "de": "wählen"},
    "cmd.go": {"fa": "باز کردن", "en": "open", "de": "öffnen"},

    # ── furniture added with the 2026 redesign ────────────────────────────
    # Labels and tooltips only. Nothing here says anything about Roya; every
    # value these labels sit next to still comes from the database.
    "nav.breadcrumb": {"fa": "مسیر صفحه", "en": "Breadcrumb", "de": "Brotkrümelpfad"},
    "tip.open": {"fa": "باز کردن", "en": "Open", "de": "Öffnen"},
    "tip.new_tab": {"fa": "در زبانهٔ جدید باز می‌شود", "en": "Opens in a new tab", "de": "Öffnet in neuem Tab"},
    "tip.filter": {"fa": "نمونه‌کارهای همین برچسب", "en": "Work with this tag", "de": "Arbeiten mit diesem Tag"},
    "home.at_a_glance": {"fa": "در یک نگاه", "en": "At a glance", "de": "Auf einen Blick"},
    "facts.location": {"fa": "موقعیت", "en": "Location", "de": "Standort"},
    "facts.availability": {"fa": "وضعیت همکاری", "en": "Availability", "de": "Verfügbarkeit"},
    "facts.latest_role": {"fa": "آخرین نقش", "en": "Latest role", "de": "Letzte Position"},
    "facts.core_stack": {"fa": "مهارت‌های اصلی", "en": "Core skills", "de": "Kernkompetenzen"},
    "skills.primary": {"fa": "مهارت اصلی", "en": "Core skill", "de": "Kernkompetenz"},
    "projects.read_case": {"fa": "خواندن کیس استادی", "en": "Read the case study", "de": "Zur Fallstudie"},
    "exp.duration": {"fa": "مدت", "en": "Duration", "de": "Dauer"},
    "dur.year": {"fa": "سال", "en": "yr", "de": "J."},
    "dur.years": {"fa": "سال", "en": "yrs", "de": "J."},
    "dur.month": {"fa": "ماه", "en": "mo", "de": "Mon."},
    "dur.months": {"fa": "ماه", "en": "mos", "de": "Mon."},
    "dur.and": {"fa": " و ", "en": " ", "de": " "},
    "resume.profile": {"fa": "خلاصه", "en": "Profile", "de": "Profil"},
    "resume.skills": {"fa": "مهارت‌ها", "en": "Skills", "de": "Kenntnisse"},
    "channel.email": {"fa": "ایمیل", "en": "Email", "de": "E-Mail"},
    "channel.instagram": {"fa": "اینستاگرام", "en": "Instagram", "de": "Instagram"},
    "channel.telegram": {"fa": "تلگرام", "en": "Telegram", "de": "Telegram"},
    "channel.github": {"fa": "گیت‌هاب", "en": "GitHub", "de": "GitHub"},
    "channel.linkedin": {"fa": "لینکدین", "en": "LinkedIn", "de": "LinkedIn"},
    "channel.phone": {"fa": "تلفن", "en": "Phone", "de": "Telefon"},
    "card.vcf": {"fa": "فایل vCard", "en": "vCard file", "de": "vCard-Datei"},
    "footer.explore": {"fa": "گشت‌وگذار", "en": "Explore", "de": "Entdecken"},
    "footer.career": {"fa": "کارنامه", "en": "Career", "de": "Karriere"},
    "footer.connect": {"fa": "ارتباط", "en": "Connect", "de": "Vernetzen"},
    "footer.sitemap": {"fa": "نقشهٔ سایت", "en": "Sitemap", "de": "Sitemap"},
    "footer.top": {"fa": "بازگشت به بالا", "en": "Back to top", "de": "Nach oben"},
}


def t(key: str, lang: str | None = None) -> str:
    """Look one string up. An unknown key returns the key, loudly and visibly."""
    code = (lang or get_language() or DEFAULT_LANG).split("-")[0]
    entry = STRINGS.get(key)
    if entry is None:
        return key
    return entry.get(code) or entry.get(DEFAULT_LANG) or key
