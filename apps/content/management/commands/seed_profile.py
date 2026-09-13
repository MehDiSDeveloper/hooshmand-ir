"""
Seed the site with Roya Hooshmand's real content in all three languages.

This is the counterpart to `seed_demo`: same shape, but every string here is
true and traceable to the two documents she supplied — her résumé (June 2026)
and the Namasa case study. It is the reproducible record of what the live site
says, so a claim can be changed in one reviewed place rather than in an admin
form nobody can diff.

    python manage.py seed_profile           # upsert, keeps the database
    python manage.py seed_profile --wipe    # replace projects/skills/roles

── Rules this file follows ────────────────────────────────────────────────
Every number in a case study can be read off an Instagram Insights screenshot
in the case study: 8,270,863 views, a 19.1% skip rate against a typical 42.8%,
3,065 follows; 193,744 views, 146,094 accounts reached, 6,057 follows.

Three claims are left out because nothing on the page backs them:
"more than 7 years of experience" (the timeline shows the dates instead, and
this project has no years-of-experience field on purpose), "close to 5 million
unique users" (no screenshot shows reach for that Reel), and "99.9% of traffic
from Reels and Explore" (the screenshot shows 68.4% + 30.8%, so the site says
"over 99%").

Experience dates are Jalali years on the résumé. Each is stored as 1 Farvardin
of that year, which is what a Persian reader sees rendered back. The résumé
runs the Namasa role to 1405; since then Roya has been Social Media Strategist
at Dokhan Atigh Parsian (دخان عتیق پارسیان), which is the current role. Its
start is stored as 1405 by the same year-only rule, and it has no description
yet because nothing she supplied describes the work there.

Education is absent from the timeline, not from the site: the résumé names the
degree (Master of Architectural Engineering, Damavand University) but not the
years, and a timeline row needs a start date. The bio carries it instead.

Nothing private is here: the birth date and the phone number on the résumé are
both left out. The site is public and indexed, and a mobile number on it is an
invitation to spam; email is the contact channel. The Instagram and LinkedIn
handles are empty until she confirms which ones to publish.

Everything that came over from montazeri-ir when this repository was copied —
Mahdi Montazeri's projects, roles, skill groups and tags — is deleted by
`_retire_inherited`, so running this without --wipe leaves no trace of it.
"""

from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from apps.content.models import (
    Experience,
    Post,
    Profile,
    Project,
    Skill,
    SkillGroup,
    Tag,
)

# Her portrait, cropped from the résumé. data/ is not in git, so a fresh clone
# has no file and every template falls back to the initials.
_AVATAR_FILES = ("profile/roya-hooshmand.jpg", "profile/roya-hooshmand.png")


class Command(BaseCommand):
    help = "Fill the database with Roya's real content, in fa/en/de."

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Delete projects, skills, tags and roles first. Posts are only unpublished.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["wipe"]:
            for model in (Project, Experience, Skill, SkillGroup, Tag):
                model.objects.all().delete()
            self.stdout.write(self.style.WARNING("wiped projects, skills, tags and roles"))

        self._retire_inherited()
        self._profile()
        tags = self._tags()
        self._skills()
        self._projects(tags)
        self._experience()
        self._retire_demo_posts()
        self.stdout.write(self.style.SUCCESS("seeded — real content, fa/en/de"))

    # ── profile ───────────────────────────────────────────────────────────
    def _profile(self):
        p = Profile.load()

        p.full_name_fa = "رویا هوشمند"
        p.full_name_en = "Roya Hooshmand"
        p.full_name_de = "Roya Hooshmand"

        p.headline_fa = "استراتژیست شبکه‌های اجتماعی و محتوا — روایت برند، سناریونویسی و ریلزهایی که بر پایه‌ی داده ساخته می‌شوند و دیده می‌شوند."
        p.headline_en = "Social media & content strategist — brand storytelling, scenario writing and Reels that get watched."
        p.headline_de = "Social Media & Content Strategist — Markenstorytelling, Drehbücher und Reels, die gesehen werden."

        p.intro_fa = (
            "ریلزی که برای آجر نماچین ساختیم، بدون یک ریال هزینه‌ی تبلیغاتی از ۸ میلیون بازدید "
            "گذشت و بیش از ۳ هزار فالوور هدفمند آورد — آن هم در صنعتی که محتوایش معمولاً خشک "
            "و بی‌روح است. کار من همین است: استراتژی محتوا، سناریونویسی و تحلیل داده‌ی "
            "اینستاگرام، برای برندهایی که می‌خواهند دیده شوند و مخاطبشان را به مشتری تبدیل کنند."
        )
        p.intro_en = (
            "I help brands build a social media presence that gets watched and turns an "
            "audience into customers — from content strategy and scenario writing to Instagram "
            "data analysis. At Namasa, for Namachin facade bricks, in an industry known for "
            "lifeless content, we made Reels that travelled: one passed 8 million views and "
            "brought more than 3,000 targeted followers without a rial of ad spend."
        )
        p.intro_de = (
            "Ich helfe Marken, in sozialen Medien so präsent zu sein, dass sie gesehen werden "
            "und aus Publikum Kundschaft wird — von der Content-Strategie über Drehbücher bis "
            "zur Instagram-Datenanalyse. Bei Namasa entstanden für Namachin-Fassadenziegel, in "
            "einer Branche mit notorisch leblosem Content, Reels mit großer Reichweite: Eines "
            "überschritt 8 Millionen Aufrufe und brachte über 3.000 zielgerichtete Follower — "
            "ganz ohne Werbebudget."
        )

        p.bio_fa = _BIO_FA
        p.bio_en = _BIO_EN
        p.bio_de = _BIO_DE

        p.location_fa = "تهران، ایران"
        p.location_en = "Tehran, Iran"
        p.location_de = "Teheran, Iran"

        p.now_fa = "استراتژیست شبکه‌های اجتماعی در شرکت دخان عتیق پارسیان — با همان سؤال همیشگی: چرا یک ریلز دیده می‌شود و دیگری نه؟"
        p.now_en = "Social Media Strategist at Dokhan Atigh Parsian — still working out why one Reel travels and another does not."
        p.now_de = "Social Media Strategist bei Dokhan Atigh Parsian — und weiter der Frage auf der Spur, warum ein Reel weit trägt und ein anderes nicht."

        p.languages_fa = "فارسی زبان مادری · انگلیسی مسلط · آلمانی متوسط"
        p.languages_en = "Persian native · English fluent · German intermediate"
        p.languages_de = "Persisch Muttersprache · Englisch fließend · Deutsch Mittelstufe"

        p.availability_fa = "آماده‌ی همکاری — حضوری، دورکاری یا پروژه‌ای"
        p.availability_en = "Open to collaboration — on-site, remote or per project"
        p.availability_de = "Offen für Zusammenarbeit — vor Ort, remote oder projektweise"

        p.email = "roya.hooshmand87@gmail.com"
        p.phone = ""
        # Her own handles go here; each icon appears on the site once it is set.
        p.instagram = ""
        p.linkedin = ""
        p.telegram = ""
        p.github = ""
        p.twitter = ""
        p.website = "https://hooshmand.ir"
        p.is_available = True
        p.avatar = next(
            (name for name in _AVATAR_FILES if (Path(settings.MEDIA_ROOT) / name).exists()), ""
        )

        p.save()

    # ── tags ──────────────────────────────────────────────────────────────
    def _tags(self) -> dict[str, Tag]:
        rows = [
            ("instagram", "اینستاگرام", "Instagram", "Instagram"),
            ("content-strategy", "استراتژی محتوا", "Content strategy", "Content-Strategie"),
            ("storytelling", "داستان‌سرایی", "Storytelling", "Storytelling"),
            ("video", "ویدیو مارکتینگ", "Video marketing", "Videomarketing"),
            ("analytics", "تحلیل داده", "Analytics", "Analyse"),
            ("b2b", "صنعتی و B2B", "Industrial & B2B", "Industrie & B2B"),
        ]
        out = {}
        for slug, fa, en, de in rows:
            tag, _ = Tag.objects.update_or_create(
                slug=slug, defaults={"name_fa": fa, "name_en": en, "name_de": de}
            )
            out[slug] = tag
        return out

    # ── skills ────────────────────────────────────────────────────────────
    def _skills(self):
        # The résumé's own list, grouped. The first primary skill of each group
        # floats beside the portrait, so the order inside a group matters.
        groups = [
            (
                ("استراتژی", "Strategy", "Strategie"),
                [
                    ("Social media strategy", True),
                    ("Content strategy", True),
                    ("Social media management", True),
                    ("Social media marketing", False),
                    ("Digital campaign design", False),
                ],
            ),
            (
                ("محتوا و روایت", "Content & storytelling", "Content & Storytelling"),
                [
                    ("Scenario writing", True),
                    ("Brand storytelling", True),
                    ("Copywriting", True),
                    ("Instagram Reels", False),
                    ("Video marketing", False),
                ],
            ),
            (
                ("داده و سنجش", "Data & measurement", "Daten & Messung"),
                [
                    ("Instagram data analysis", True),
                    ("Social media measurement", True),
                    ("Instagram Insights", False),
                    ("Google Analytics", False),
                ],
            ),
            (
                ("ابزارها", "Tools", "Tools"),
                [
                    ("Canva", True),
                    ("CapCut", True),
                    ("ICDL", False),
                ],
            ),
            (
                ("رهبری و مدیریت", "Leadership & management", "Führung & Management"),
                [
                    ("Team leadership", False),
                    ("Project management", False),
                    ("Time management", False),
                    ("Communication", False),
                    ("Client relationships", False),
                ],
            ),
        ]

        for gi, ((fa, en, de), skills) in enumerate(groups):
            group, _ = SkillGroup.objects.update_or_create(
                name_en=en, defaults={"name_fa": fa, "name_de": de, "order": gi}
            )
            group.skills.all().delete()
            for si, (name, primary) in enumerate(skills):
                Skill.objects.create(group=group, name=name, order=si, is_primary=primary)

    # ── projects ──────────────────────────────────────────────────────────
    def _projects(self, tags):
        self._upsert_project(
            slug="namasa-content-strategy",
            year=2025,
            order=0,
            stack="Instagram, Reels, Content strategy, Scenario writing, Brand storytelling, Instagram Insights",
            tag_slugs=("content-strategy", "instagram", "b2b"),
            tags=tags,
            fa=dict(
                title="نماسا — استراتژی محتوای ویدیومحور برای یک برند مصالح ساختمانی",
                summary=(
                    "چطور محتوای آجر نماچین و نمایندگی‌اش نماسا را از کلیشه‌ی محتوای خشک صنعتی بیرون "
                    "آوردیم — با سه ستون: داستان‌سرایی، آموزش و نمایش پروژه‌های واقعی."
                ),
                role="استراتژیست محتوا — طراحی استراتژی، سناریونویسی و تحلیل داده",
                problem=_P1_PROBLEM_FA,
                body=_P1_BODY_FA,
                outcome=(
                    "ریلزهایی با ۱۱ هزار تا ۸٫۲ میلیون بازدید، و بیش از ۹ هزار فالوور جدید تنها از "
                    "دو ویدیوی شاخص."
                ),
            ),
            en=dict(
                title="Namasa — a video-first content strategy for a building-materials brand",
                summary=(
                    "For Namachin facade bricks and their representative Namasa, a content strategy "
                    "built to break the cliché of lifeless industrial content — on three pillars: "
                    "storytelling, education and real projects."
                ),
                role="Content strategist — strategy, scenario writing and data analysis",
                problem=_P1_PROBLEM_EN,
                body=_P1_BODY_EN,
                outcome=(
                    "Reels from 11K to 8.2M views, and more than 9,000 new followers from the two "
                    "standout videos alone."
                ),
            ),
            de=dict(
                title="Namasa — eine videobasierte Content-Strategie für eine Baustoffmarke",
                summary=(
                    "Für Namachin-Fassadenziegel und die Vertretung Namasa: eine Content-Strategie "
                    "gegen leblosen Industrie-Content — auf drei Säulen: Storytelling, Wissen und "
                    "echte Projekte."
                ),
                role="Content Strategist — Strategie, Drehbücher und Datenanalyse",
                problem=_P1_PROBLEM_DE,
                body=_P1_BODY_DE,
                outcome=(
                    "Reels von 11.000 bis 8,2 Millionen Aufrufen — und über 9.000 neue Follower "
                    "allein aus den zwei stärksten Videos."
                ),
            ),
        )

        self._upsert_project(
            slug="brick-vs-stone-reel",
            year=2025,
            order=1,
            stack="Instagram Reels, Scenario writing, Expert persona, Instagram Insights",
            tag_slugs=("storytelling", "video", "b2b"),
            tags=tags,
            fa=dict(
                title="آجر یا سنگ؟ — ریلزی که بحث به پا کرد",
                summary=(
                    "آموزش فنی به‌علاوه‌ی یک ادعای چالش‌برانگیز، در یک ریلز یک‌ونیم‌دقیقه‌ای: ۱۹۳ هزار "
                    "بازدید، ۶۰۲ کامنت، ۶٫۶ هزار اشتراک‌گذاری و بیش از ۶ هزار فالوور جدید."
                ),
                role="سناریونویس و استراتژیست محتوا",
                problem=_P2_PROBLEM_FA,
                body=_P2_BODY_FA,
                outcome=(
                    "۱۹۳٬۷۴۴ بازدید و ۱۴۶٬۰۹۴ حساب دیده‌شده؛ ۹۷٫۷٪ بیننده‌ها دنبال‌کننده‌ی صفحه "
                    "نبودند و ۶٬۰۵۷ نفر پس از دیدنش صفحه را دنبال کردند."
                ),
            ),
            en=dict(
                title="Brick versus stone — a Reel built to start an argument",
                summary=(
                    "A Reel of about a minute and a half that paired technical knowledge with a claim "
                    "built to be argued with: 193K views, 602 comments, 6.6K shares and more than "
                    "6,000 new followers."
                ),
                role="Scenario writer and content strategist",
                problem=_P2_PROBLEM_EN,
                body=_P2_BODY_EN,
                outcome=(
                    "193,744 views and 146,094 accounts reached; 97.7% of viewers did not follow the "
                    "page, and 6,057 people followed it afterwards."
                ),
            ),
            de=dict(
                title="Ziegel gegen Naturstein — ein Reel, das eine Debatte auslöst",
                summary=(
                    "Ein Reel von anderthalb Minuten, das technisches Wissen mit einer streitbaren "
                    "Behauptung verbindet: 193.000 Aufrufe, 602 Kommentare, 6.600 Shares und über "
                    "6.000 neue Follower."
                ),
                role="Drehbuch und Content-Strategie",
                problem=_P2_PROBLEM_DE,
                body=_P2_BODY_DE,
                outcome=(
                    "193.744 Aufrufe und 146.094 erreichte Konten; 97,7 % der Zuschauer folgten der "
                    "Seite nicht — 6.057 Menschen taten es danach."
                ),
            ),
        )

        self._upsert_project(
            slug="drilling-reel-8m-views",
            year=2025,
            order=2,
            stack="Instagram Reels, Curiosity gap, Dynamic editing, Audience targeting, Instagram Insights",
            tag_slugs=("video", "analytics", "instagram"),
            tags=tags,
            fa=dict(
                title="۱۷ ثانیه، ۸ میلیون بازدید — ریلز «چرا آجر را سوراخ می‌کنیم؟»",
                summary=(
                    "یک سؤال ساده در سه ثانیه‌ی اول، و مخاطبی که تا آخر ماند: نرخ اسکیپ ۱۹٫۱٪ در برابر "
                    "میانگین ۴۲٫۸٪ صفحه، و بیش از ۸٫۲ میلیون بازدید برای یک ریلز آموزشی."
                ),
                role="سناریونویسی، ساختار تدوین و هدف‌گیری مخاطب",
                problem=_P3_PROBLEM_FA,
                body=_P3_BODY_FA,
                outcome=(
                    "۸٬۲۷۰٬۸۶۳ بازدید، نرخ تکمیل نزدیک به ۹۵٪ و ۳٬۰۶۵ فالوور هدفمند — کاملاً ارگانیک، "
                    "بدون یک ریال هزینه‌ی تبلیغاتی."
                ),
            ),
            en=dict(
                title="17 seconds, 8.2 million views — the “why are we drilling this brick?” Reel",
                summary=(
                    "An educational Reel that held viewers to the end with one simple question in its "
                    "first three seconds: a 19.1% skip rate against the page's typical 42.8%, and "
                    "more than 8.2 million views."
                ),
                role="Scenario, edit structure and audience targeting",
                problem=_P3_PROBLEM_EN,
                body=_P3_BODY_EN,
                outcome=(
                    "8,270,863 views, close to 95% completion and 3,065 targeted followers — with no "
                    "ad spend."
                ),
            ),
            de=dict(
                title="17 Sekunden, 8,2 Millionen Aufrufe — das Reel „Warum bohren wir in diesen Ziegel?“",
                summary=(
                    "Ein Erklär-Reel, das mit einer einfachen Frage in den ersten drei Sekunden bis zum "
                    "Ende fesselt: 19,1 % Skip-Rate gegenüber sonst 42,8 % — und über 8,2 Millionen "
                    "Aufrufe."
                ),
                role="Drehbuch, Schnittstruktur und Zielgruppenansprache",
                problem=_P3_PROBLEM_DE,
                body=_P3_BODY_DE,
                outcome=(
                    "8.270.863 Aufrufe, fast 95 % Abschlussrate und 3.065 zielgerichtete Follower — "
                    "ohne Werbebudget."
                ),
            ),
        )

    def _upsert_project(
        self, *, slug, year, order, stack, tag_slugs, tags, fa, en, de, demo_url="", featured=True
    ):
        # `featured` is what the home page shows, and it shows three — which is
        # all three case studies.
        defaults = {
            "year": year,
            "order": order,
            "stack": stack,
            "demo_url": demo_url,
            "is_featured": featured,
            "is_published": True,
        }
        for code, values in (("fa", fa), ("en", en), ("de", de)):
            for field, value in values.items():
                defaults[f"{field}_{code}"] = value
        project, _ = Project.objects.update_or_create(slug=slug, defaults=defaults)
        project.tags.set([tags[s] for s in tag_slugs])

    # ── experience ────────────────────────────────────────────────────────
    def _experience(self):
        # Jalali years from the résumé, each stored as 1 Farvardin of that year.
        tehran = dict(location_fa="تهران", location_en="Tehran", location_de="Teheran")
        rows = [
            dict(
                order=0,
                start=date(2026, 3, 21),  # 1405
                end=None,
                org_fa="شرکت دخان عتیق پارسیان",
                org_en="Dokhan Atigh Parsian",
                org_de="Dokhan Atigh Parsian",
                role_fa="استراتژیست شبکه‌های اجتماعی",
                role_en="Social Media Strategist",
                role_de="Social Media Strategist",
                description_fa="",
                description_en="",
                description_de="",
                **tehran,
            ),
            dict(
                order=1,
                start=date(2024, 3, 20),  # 1403
                end=date(2026, 3, 21),  # 1405
                org_fa="نماسا (نمایندگی آجر نماچین)",
                org_en="Namasa (Namachin Brick)",
                org_de="Namasa (Namachin-Ziegel)",
                role_fa="استراتژیست محتوا",
                role_en="Content Strategist",
                role_de="Content Strategist",
                description_fa=_E_NAMASA_FA,
                description_en=_E_NAMASA_EN,
                description_de=_E_NAMASA_DE,
                **tehran,
            ),
            dict(
                order=1,
                start=date(2021, 3, 21),  # 1400
                end=date(2024, 3, 20),  # 1403
                org_fa="شرکت ایده آفرین",
                org_en="Idea Afarin",
                org_de="Idea Afarin",
                role_fa="سرپرست تیم تولید محتوا",
                role_en="Content Production Team Lead",
                role_de="Team Lead Content-Produktion",
                description_fa=_E_IDEA_FA,
                description_en=_E_IDEA_EN,
                description_de=_E_IDEA_DE,
                **tehran,
            ),
            dict(
                order=2,
                start=date(2020, 3, 20),  # 1399
                end=date(2021, 3, 21),  # 1400
                org_fa="مستقل",
                org_en="Freelance",
                org_de="Freiberuflich",
                role_fa="کارشناس اینستاگرام",
                role_en="Instagram Specialist",
                role_de="Instagram Specialist",
                location_fa="دورکاری · پروژه‌ای",
                location_en="Remote · project-based",
                location_de="Remote · projektbasiert",
                description_fa="همکاری پروژه‌ای و دورکاری به‌عنوان کارشناس اینستاگرام.",
                description_en="Project-based, remote work as an Instagram specialist.",
                description_de="Projektbasierte Remote-Arbeit als Instagram Specialist.",
            ),
            dict(
                order=3,
                start=date(2013, 3, 21),  # 1392
                end=date(2017, 3, 21),  # 1396
                org_fa="شرکت نمایشگاهی خورشید",
                org_en="Khorshid Exhibitions",
                org_de="Khorshid Exhibitions",
                role_fa="بازاریاب دفتری",
                role_en="Office Marketer",
                role_de="Office Marketer",
                description_fa="بازاریابی برای یک شرکت نمایشگاهی.",
                description_en="Marketing for an exhibitions company.",
                description_de="Marketing für ein Ausstellungsunternehmen.",
                **tehran,
            ),
            dict(
                order=4,
                start=date(2010, 3, 21),  # 1389
                end=date(2013, 3, 21),  # 1392
                org_fa="شرکت آدنا گستر",
                org_en="Adna Gostar",
                org_de="Adna Gostar",
                role_fa="کارشناس فروش و بازاریابی",
                role_en="Sales and Marketing Expert",
                role_de="Sales & Marketing Expert",
                description_fa="فروش و بازاریابی، در ارتباط مستقیم با مشتری.",
                description_en="Sales and marketing, working directly with customers.",
                description_de="Vertrieb und Marketing im direkten Kundenkontakt.",
                **tehran,
            ),
            dict(
                order=5,
                start=date(2008, 3, 20),  # 1387
                end=date(2009, 3, 21),  # 1388
                org_fa="شرکت معماری صنعتی ایران",
                org_en="Iran Industrial Architecture Co.",
                org_de="Iran Industrial Architecture Co.",
                role_fa="معمار",
                role_en="Architect",
                role_de="Architect",
                description_fa="فعالیت معماری در یک شرکت معماری صنعتی؛ نقطه‌ی شروع مسیری که بعد به بازاریابی رسید.",
                description_en="Architectural work at an industrial architecture firm, before moving into marketing.",
                description_de="Architekturarbeit in einem Büro für Industriearchitektur, vor dem Wechsel ins Marketing.",
                **tehran,
            ),
        ]
        # Order is the position in the list above, so a new role is one insert.
        for position, row in enumerate(rows):
            row["order"] = position
            Experience.objects.update_or_create(
                org_en=row["org_en"],
                role_en=row["role_en"],
                defaults={"kind": Experience.Kind.WORK, **row},
            )

    # ── clean-up ──────────────────────────────────────────────────────────
    def _retire_inherited(self):
        """Delete what came over from montazeri-ir when this repo was copied.

        By exact identifier, so nothing written for Roya can be caught by it.
        Unlike a post, none of these has a URL worth preserving.
        """
        projects, _ = Project.objects.filter(
            slug__in=(
                "customer-club-platform",
                "sql-server-at-scale",
                "actpact",
                "rechnungskit",
                "webhook-gateway",
                "tenantforge",
                "montazeri-ir",
                "challenge-app",
            )
        ).delete()
        roles, _ = Experience.objects.filter(
            Q(org_en="Smart X", role_en=".NET Developer")
            | Q(org_en="Independent", role_en="Backend Developer (freelance)")
            | Q(org_en="bala24", role_en="Senior Software Developer, full-stack (part-time)")
        ).delete()
        groups, _ = SkillGroup.objects.filter(
            name_en__in=("Backend & .NET", "Python", "Data & performance", "Architecture & delivery")
        ).delete()
        tags, _ = Tag.objects.filter(
            slug__in=("dotnet", "python", "django", "architecture", "performance", "databases", "fastapi", "security")
        ).delete()
        if projects or roles or groups or tags:
            self.stdout.write(self.style.WARNING("removed content inherited from montazeri-ir"))

    def _retire_demo_posts(self):
        """Unpublish the placeholder posts rather than delete them.

        They are hidden because Roya did not write them. The blog link, the
        palette entry and the home section all stay away until a real post is
        published.
        """
        hidden = Post.objects.filter(
            slug__in=(
                "permissions-are-a-query",
                "sqlite-in-production",
                "hook-in-three-seconds",
                "saves-over-likes",
            )
        ).update(is_published=False)
        if hidden:
            self.stdout.write(self.style.WARNING(f"unpublished {hidden} placeholder post(s)"))


# ── long copy ──────────────────────────────────────────────────────────────
# Kept at the bottom so the command reads as structure, not as prose.

_BIO_FA = """\
استراتژیست شبکه‌های اجتماعی و محتوا هستم و کارم سه قدم دارد: تصمیم می‌گیرم یک برند
در فضای آنلاین چه بگوید، سناریوی گفتنش را می‌نویسم، و بعد عددها را بی‌تعارف می‌خوانم
تا معلوم شود محتوای بعدی چه باید باشد. در حال حاضر استراتژیست شبکه‌های اجتماعی شرکت
دخان عتیق پارسیان هستم.

### چه کاری از من برمی‌آید

- **استراتژی محتوا** برای افزایش تعامل و تبدیل مخاطب به مشتری — بر پایه‌ی داده‌ی
  همان صفحه، نه نسخه‌ای که برای صفحه‌ی دیگری جواب داده.
- **سناریونویسی** برای ریلز و کمپین‌های تبلیغاتی، و نظارت بر کیفیت اجرای آن‌ها.
- **رهبری تیم تولید محتوا**، طوری که همه‌ی خروجی‌های تیم با صدای یک برند حرف بزنند.
- **تحلیل داده‌ی اینستاگرام و سنجش شبکه‌های اجتماعی**: دسترسی، نرخ اسکیپ، نرخ تکمیل،
  ذخیره و اشتراک‌گذاری — و اینکه هر عدد واقعاً چه می‌گوید.
- **همکاری با تیم‌های طراحی و توسعه** برای نیازسنجی دقیق بازار، تا محتوا به نیازی
  پاسخ بدهد که پیش‌تر سنجیده شده.

### چرا برندهای صنعتی

نمونه‌کارهای این سایت برای آجر نماچین و نمایندگی‌اش، نماسا، است؛ صنعتی که محتوایش
معمولاً آن‌قدر خشک است که کسی تا آخر نمی‌بیندش. من دقیقاً همین‌جا را برای کار ترجیح
می‌دهم. نسخه‌اش ساده به نظر می‌رسد اما اجرایش دقت می‌خواهد: یک قلاب در سه ثانیه‌ی
اول، مخاطبی مشخص، ادعایی که بشود سرش بحث کرد، و متخصصی که از زبان برند حرف بزند.
وقتی این‌ها درست کنار هم بنشینند، حتی یک ویدیوی هفده‌ثانیه‌ای درباره‌ی آجر هم از
هشت میلیون بازدید می‌گذرد.

### از معماری به بازاریابی

معماری خوانده‌ام، کارشناسی ارشد مهندسی معماری را از دانشگاه دماوند دارم و مسیر
حرفه‌ای‌ام را در شرکت معماری صنعتی ایران شروع کردم. پس از آن چند سال در فروش و
بازاریابی کار کردم؛ در آدنا گستر و شرکت نمایشگاهی خورشید. حاصل این مسیر دو چیز است:
با معماران، سازندگان و طراحان به زبان خودشان حرف می‌زنم، و محتوا را با این معیار
می‌سنجم که در نهایت چه کسی خرید می‌کند.

### دوره‌ها و گواهی‌نامه‌ها

- طراحی کمپین بازاریابی دیجیتال، اینستاگرام مارکتینگ، ویدیو مارکتینگ، لینکدین
  مارکتینگ، بازاریابی شبکه‌های اجتماعی، کپی‌رایتینگ، و مبانی دیجیتال مارکتینگ و
  E-Commerce — مکتب‌خونه
- بازاریابی محتوا، و دوره‌ی جامع کسب درآمد آنلاین — رسانه تجارت نوین
- آموزش جامع اینستاگرام — معین فرجی
- دوره‌ی جامع جادوی فروش — احمد کلاته
- دوره‌ی جامع ICDL — فنی و حرفه‌ای

### همکاری

ساکن تهرانم و برای همکاری حضوری، دورکاری یا پروژه‌ای آماده‌ام. به زبان انگلیسی
مسلطم و آلمانی را در سطح متوسط می‌دانم.
"""

_BIO_EN = """\
I am a social media and content strategist. My work is deciding what a brand
should say online, writing the scenario for how it says it, and then reading the
numbers honestly enough to know what to make next. I am currently Social Media
Strategist at Dokhan Atigh Parsian.

### What the work is

- Content strategies that raise engagement and turn an audience into customers —
  built on the data of the page itself, not on what worked for someone else.
- Scenario writing for Reels and advertising campaigns, and overseeing the
  quality of how they are made.
- Leading content production teams so that everything they make still sounds
  like one brand.
- Instagram data analysis and social media measurement: reach, skip rate,
  completion, saves and shares — and what each of them is actually saying.
- Working with design and development teams on market research, so the content
  answers a need that has been checked.

### Industrial brands, on purpose

The case studies on this site are for Namachin facade bricks and their
representative, Namasa — an industry whose content is usually dry enough that
nobody watches it to the end. That is where I like to work. A hook in the first
three seconds, one clearly chosen audience, a claim bold enough to argue with,
and an expert who speaks for the brand: built carefully, a seventeen-second
video about a brick can pass eight million views.

### Before social media

I studied architecture and hold a Master of Architectural Engineering from
Damavand University, and my career began at Iran Industrial Architecture Co.
Several years in sales and marketing followed, at Adna Gostar and at Khorshid
Exhibitions. That is why architects, builders and designers are an audience I
can talk to in their own language, and why I judge content by who ends up
buying.

### Courses and certificates

- Digital marketing campaign design, Instagram marketing, video marketing,
  LinkedIn marketing, social media marketing, copywriting, and digital marketing
  and e-commerce fundamentals — Maktabkhooneh
- Content marketing, and a comprehensive course on earning online — Resaneh
  Tejarat Novin
- Comprehensive Instagram training — Moein Faraji
- "The Magic of Selling", a comprehensive sales course — Ahmad Kalateh
- ICDL — Iran's Technical and Vocational Training Organization

### Practicalities

I am based in Tehran and open to on-site, remote or project-based work. My
English is fluent and my German is at an intermediate level.
"""

_BIO_DE = """\
Ich bin Social Media & Content Strategist. Meine Arbeit besteht darin zu
entscheiden, was eine Marke online sagen soll, das Drehbuch dafür zu schreiben
und die Zahlen danach ehrlich genug zu lesen, um zu wissen, was als Nächstes
entsteht. Derzeit bin ich Social Media Strategist bei Dokhan Atigh Parsian.

### Woraus die Arbeit besteht

- Content-Strategien, die Interaktion steigern und aus Publikum Kundschaft
  machen — gestützt auf die Daten der eigenen Seite, nicht auf das, was bei
  anderen funktioniert hat.
- Drehbücher für Reels und Werbekampagnen sowie die Qualitätskontrolle bei
  ihrer Umsetzung.
- Führung von Content-Produktionsteams, damit alles, was entsteht, nach einer
  Marke klingt.
- Instagram-Datenanalyse und Social-Media-Messung: Reichweite, Skip-Rate,
  Abschlussrate, Speicherungen und Shares — und was jede Zahl tatsächlich sagt.
- Zusammenarbeit mit Design- und Entwicklungsteams bei der Marktanalyse, damit
  Content einen geprüften Bedarf beantwortet.

### Industriemarken, mit Absicht

Die Fallstudien auf dieser Seite entstanden für Namachin-Fassadenziegel und
deren Vertretung Namasa — eine Branche, deren Content meist so trocken ist, dass
ihn niemand bis zum Ende ansieht. Genau dort arbeite ich gern. Ein Hook in den
ersten drei Sekunden, eine klar gewählte Zielgruppe, eine Behauptung, über die
man streiten kann, und eine Fachperson, die für die Marke spricht: Sorgfältig
gebaut, erreicht auch ein siebzehnsekündiges Video über einen Ziegel mehr als
acht Millionen Aufrufe.

### Vor Social Media

Ich habe Architektur studiert und einen Master in Architekturingenieurwesen der
Damavand-Universität; meine Laufbahn begann bei Iran Industrial Architecture Co.
Danach folgten einige Jahre in Vertrieb und Marketing, bei Adna Gostar und bei
Khorshid Exhibitions. Deshalb sind Architektur-, Bau- und Planungsprofis ein
Publikum, mit dem ich in seiner eigenen Sprache sprechen kann — und deshalb
messe ich Content daran, wer am Ende kauft.

### Kurse und Zertifikate

- Kampagnendesign im digitalen Marketing, Instagram-Marketing, Videomarketing,
  LinkedIn-Marketing, Social-Media-Marketing, Copywriting sowie Grundlagen des
  digitalen Marketings und E-Commerce — Maktabkhooneh
- Content-Marketing und ein umfassender Kurs zu Online-Einkommen — Resaneh
  Tejarat Novin
- Umfassendes Instagram-Training — Moein Faraji
- „Die Magie des Verkaufens“, ein umfassender Vertriebskurs — Ahmad Kalateh
- ICDL — staatliche Berufsbildungsorganisation Irans

### Praktisches

Ich lebe in Teheran und bin offen für Arbeit vor Ort, remote oder projektweise.
Englisch spreche ich fließend, Deutsch auf mittlerem Niveau.
"""

# ── case study 1: the Namasa strategy ─────────────────────────────────────
_P1_PROBLEM_FA = """\
بازاریابی دیجیتال در صنایع سنگین و مصالح ساختمانی، از جمله آجر نما، تقریباً همیشه به
یک مانع می‌خورد: محتوای خشک و بی‌روحی که نه مخاطب عام را جذب می‌کند و نه مخاطب متخصص
را.

آجر نماچین، از طریق نمایندگی‌اش نماسا، به حضوری در اینستاگرام نیاز داشت که معماران،
سازندگان و طراحان واقعاً برایش دست از اسکرول بکشند؛ و آن‌قدر نگهشان دارد که تا
ثانیه‌ی آخر ویدیو بمانند — تا الگوریتم دلیلی داشته باشد که آن را به آدم‌های بیشتری
نشان بدهد.
"""

_P1_BODY_FA = """\
استراتژی ما شکستن این کلیشه بود، نه بزک کردنش: محتوایی که جدا از جذابیت بصری،
کنجکاوی مخاطب را آن‌قدر برانگیزد که بماند. این استراتژی بر سه ستون استوار شد.

**۱. داستان‌سرایی.** نمایش پشت صحنه‌ی تولید و کنترل کیفیت، برای ساختن اعتماد پیش از
آنکه چیزی از مخاطب خواسته شود. یک ریلز داستان‌محور در اردیبهشت ۱۴۰۴ به ۱۹۳٬۷۴۴
بازدید رسید و دو ریلز دیگر به ۳۲٬۲۳۵ و ۱۱٬۰۷۷ بازدید.

**۲. محتوای آموزشی.** نکات فنی، روش‌های نصب و مزایای کاربردی — به زبان متخصص و معمار،
نه به زبان بروشور. یک ریلز آموزشی ۱۷ ثانیه‌ای در خرداد ۱۴۰۴ از مرز ۸٫۲ میلیون بازدید
گذشت و ریلز آموزشی دیگری در تیر به ۱۱۴٬۵۴۰ بازدید رسید.

**۳. نمایش پروژه‌های واقعی.** کاربرد نهایی مصالح در پروژه‌های تکمیل‌شده، تا کیفیت در
عمل دیده شود و فقط ادعا نباشد. دو ریلز این ستون به ۳۰٬۵۸۷ و ۱۴٬۴۱۵ بازدید رسیدند و
یک پست مشترک با Radis Group به ۱۵۹٬۳۵۴ بازدید و ۸۷٬۰۶۱ حساب.

**چرخه‌ی سنجش.** هر محتوا بعد از انتشار سنجیده شد — بازدید، دسترسی، نرخ اسکیپ،
ذخیره، اشتراک‌گذاری و فالو — و سناریوی بعدی از دل همین عددها نوشته شد. دو ریلز شاخص
این استراتژی، هر کدام در همین سایت کیس استادی مستقلی دارند.
"""

_P1_PROBLEM_EN = """\
Digital marketing for heavy industry and building materials — facade bricks among
them — tends to hit the same wall: content with no life in it, which neither the
general public nor the specialist audience finds worth watching.

Namachin facade bricks, through their representative Namasa, needed an Instagram
presence that architects, builders and designers would actually stop for — and
one that held them to the last second of a video, so the algorithm had a reason
to show it to more people.
"""

_P1_BODY_EN = """\
The strategy was to break that cliché rather than decorate it: content that is
visually strong, but that also makes the viewer curious enough to stay. It rested
on three pillars.

**Storytelling.** Behind the scenes — how the bricks are made and how their
quality is checked — to build trust before asking for anything. A storytelling
Reel from May 2025 reached 193,744 views; two others reached 32,235 and 11,077.

**Educational content.** Technical tips, installation methods and practical
benefits, written for specialists and architects rather than for a brochure. A
17-second educational Reel from June 2025 passed 8.2 million views; another, from
July, reached 114,540.

**Real projects.** The materials in finished buildings, so quality is shown in
use instead of claimed. Two Reels in this pillar reached 30,587 and 14,415 views,
and a collaboration post with Radis Group reached 159,354 views and 87,061
accounts.

Every piece was measured after it went out — views, reach, skip rate, saves,
shares and follows — and the next scenario was written from what those numbers
said. The two standout Reels each have a case study of their own on this site.
"""

_P1_PROBLEM_DE = """\
Digitales Marketing für Schwerindustrie und Baustoffe — Fassadenziegel
eingeschlossen — stößt fast immer auf dasselbe Problem: lebloser Content, den
weder das breite Publikum noch das Fachpublikum sehenswert findet.

Namachin-Fassadenziegel brauchten über ihre Vertretung Namasa eine
Instagram-Präsenz, bei der Architektur-, Bau- und Planungsprofis tatsächlich
innehalten — und die sie bis zur letzten Sekunde eines Videos hält, damit der
Algorithmus einen Grund hat, es mehr Menschen zu zeigen.
"""

_P1_BODY_DE = """\
Die Strategie war, das Klischee zu brechen statt es zu dekorieren: Content, der
visuell stark ist, aber vor allem neugierig genug macht, um dranzubleiben. Sie
ruhte auf drei Säulen.

**Storytelling.** Blicke hinter die Kulissen — Herstellung und
Qualitätskontrolle —, um Vertrauen aufzubauen, bevor etwas verlangt wird. Ein
Storytelling-Reel aus dem Mai 2025 erreichte 193.744 Aufrufe, zwei weitere 32.235
und 11.077.

**Wissensinhalte.** Technische Tipps, Verlegemethoden und praktische Vorteile,
geschrieben für Fachleute und Architekturbüros statt für eine Broschüre. Ein
17-sekündiges Erklär-Reel aus dem Juni 2025 überschritt 8,2 Millionen Aufrufe,
ein weiteres aus dem Juli erreichte 114.540.

**Echte Projekte.** Die Materialien in fertigen Gebäuden, damit Qualität im
Einsatz sichtbar wird statt nur behauptet. Zwei Reels dieser Säule erreichten
30.587 und 14.415 Aufrufe, ein Kooperationsbeitrag mit Radis Group 159.354
Aufrufe und 87.061 Konten.

Jeder Beitrag wurde nach der Veröffentlichung gemessen — Aufrufe, Reichweite,
Skip-Rate, Speicherungen, Shares und Follows —, und das nächste Drehbuch entstand
aus dem, was diese Zahlen sagten. Die beiden stärksten Reels haben jeweils eine
eigene Fallstudie auf dieser Seite.
"""

# ── case study 2: brick versus stone ──────────────────────────────────────
_P2_PROBLEM_FA = """\
مخاطب هدف آجر نما — معماران، سازندگان و طراحان — جمعی کوچک، متخصص و سخت‌پسند است، و
محتوای صنعتی به‌ندرت دلیلی به او می‌دهد که کامنت بگذارد یا ویدیو را برای کسی بفرستد.
هدف، ویدیویی بود که دیده‌شدنش را از مسیر تعامل به دست بیاورد: محتوایی که مخاطب به
خاطر اطلاعاتش ذخیره کند، در کامنت‌ها سرش بحث کند و برای همکارانش بفرستد.
"""

_P2_BODY_FA = """\
یک ریلز حدوداً یک‌ونیم‌دقیقه‌ای، منتشرشده در اردیبهشت ۱۴۰۴، که بر چهار اصل کلیدی
ساخته شد.

**۱. قلاب تخصصی و نیازسنجی (The Expert Hook).** ویدیو با پرسش مجری از مسئول فنی
درباره‌ی تنوع، کاربرد و مقاومت آجرهای رویال آغاز می‌شود. این شروع محترمانه و تخصصی،
مخاطب هدف را جذب می‌کند و از همان ابتدا چیزی برای آموختن به او می‌دهد — عاملی که سهم
بزرگی در ۴٫۵ هزار ذخیره‌ی ویدیو داشت.

**۲. محرک جنجال و ایجاد دوقطبی (The Controversy Trigger).** جسورانه‌ترین بخش سناریو،
آجر را مستقیماً با رقیب سنتی‌اش، سنگ، مقایسه می‌کند و آجر را برنده اعلام می‌کند. این
ادعا با باور رایج بازار ساختمان درمی‌افتد و دوقطبی‌ای جذاب می‌سازد؛ همان کاتالیزوری
که ۶۰۲ کامنت را رقم زد و سنگ‌کاران و طرفداران آجر را در بخش نظرات به بحث کشاند.

**۳. اعتباربخشی فنی (Authority & Trust).** پاسخ‌ها از زبان مسئول فنی برند نماچین
شنیده می‌شود، نه یک بلاگر معمولی؛ و همین به ادعای جنجالی وزن و اعتبار علمی می‌بخشد.
مخاطبان ویدیو را برای همکاران و کارفرمایانشان فرستادند تا ادعا را تأیید یا رد کنند:
۶٫۶ هزار اشتراک‌گذاری.

**۴. سیگنال به الگوریتم و تسخیر اکسپلور (The Algorithm Hack).** کامنت‌های پرشمار و
نرخ بالای اشتراک‌گذاری، قوی‌ترین سیگنال‌ها را به الگوریتم اینستاگرام فرستادند. ویدیو
به‌سرعت به اکسپلور راه یافت — ۹۷٫۷٪ بازدیدها از سوی کسانی بود که صفحه را دنبال
نمی‌کردند — و در نهایت بیش از ۶ هزار نفر را به دنبال‌کنندگان صفحه اضافه کرد.

**در یک نگاه:** ۱۹۳٬۷۴۴ بازدید و ۱۴۶٬۰۹۴ حساب دیده‌شده؛ ۸٫۲ هزار لایک، ۶۰۲ کامنت، ۶٫۶
هزار اشتراک‌گذاری و ۴٫۵ هزار ذخیره؛ میانگین تماشای ۲۱ ثانیه؛ بازدید از فید (۴۵٫۵٪)،
تب ریلز (۳۲٫۴٪) و اکسپلور (۱۶٫۶٪)؛ و ۶٬۰۵۷ فالو.
"""

_P2_PROBLEM_EN = """\
The target audience for facade bricks — architects, builders and designers — is
small, specialist and hard to impress, and industrial content rarely gives them a
reason to comment or share. The aim was a video that would earn its reach through
engagement: something the audience would save for the information, argue about
in the comments and send to colleagues.
"""

_P2_BODY_EN = """\
A Reel of about a minute and a half, published in May 2025, built on four
principles.

**1. The Expert Hook.** The video opens with the host putting a question to the
brand's technical lead about the variety, uses and strength of Royal bricks. A
respectful, specialist opening draws in the target audience and gives them
something to learn — which is where much of the 4.5K saves came from.

**2. The Controversy Trigger.** The boldest part of the scenario compares brick
directly with its traditional rival, stone, and declares brick the winner. The
claim cuts against what much of the construction market believes, and that
polarity was the catalyst for 602 comments, with stone workers and brick
advocates debating each other under the video.

**3. Authority and trust.** The answers come from Namachin's technical lead, not
from an ordinary blogger, which gives the controversial claim real weight.
Viewers sent the video to colleagues and employers to have it confirmed or
refuted: 6.6K shares.

**4. The Algorithm Hack.** Heavy activity in the comments and a high share rate
are the strongest signals Instagram reads. The Reel moved into Explore quickly —
97.7% of its views came from people who did not follow the page — and in the end
brought more than 6,000 people to follow it.

**By the numbers:** 193,744 views and 146,094 accounts reached; 8.2K likes, 602
comments, 6.6K shares and 4.5K saves; an average watch time of 21 seconds; views
from the feed (45.5%), the Reels tab (32.4%) and Explore (16.6%); and 6,057
follows.
"""

_P2_PROBLEM_DE = """\
Die Zielgruppe für Fassadenziegel — Architektur-, Bau- und Planungsprofis — ist
klein, fachkundig und schwer zu beeindrucken, und Industrie-Content gibt ihr
selten einen Grund, zu kommentieren oder zu teilen. Ziel war ein Video, das seine
Reichweite über Interaktion verdient: etwas, das man wegen der Information
speichert, in den Kommentaren diskutiert und an Kollegen schickt.
"""

_P2_BODY_DE = """\
Ein Reel von rund anderthalb Minuten, veröffentlicht im Mai 2025, gebaut auf vier
Prinzipien.

**1. The Expert Hook.** Das Video beginnt mit der Frage der Moderation an die
technische Leitung der Marke — zu Vielfalt, Einsatz und Festigkeit der
Royal-Ziegel. Der respektvolle, fachliche Einstieg holt die Zielgruppe ab und
gibt ihr etwas zu lernen; ein großer Teil der 4.500 Speicherungen geht darauf
zurück.

**2. The Controversy Trigger.** Der mutigste Teil des Drehbuchs vergleicht Ziegel
direkt mit dem traditionellen Rivalen Naturstein und erklärt den Ziegel zum
Sieger. Die Behauptung widerspricht dem, was große Teile des Baumarkts glauben,
und genau diese Polarisierung löste 602 Kommentare aus, in denen Steinverarbeiter
und Ziegel-Fans miteinander stritten.

**3. Authority & Trust.** Die Antworten kommen von der technischen Leitung der
Marke Namachin, nicht von einem beliebigen Blog — das gibt der streitbaren
Behauptung fachliches Gewicht. Zuschauer schickten das Video an Kollegen und
Auftraggeber, um die Aussage bestätigen oder widerlegen zu lassen: 6.600 Shares.

**4. The Algorithm Hack.** Viel Aktivität in den Kommentaren und eine hohe
Share-Rate sind die stärksten Signale, die Instagram auswertet. Das Reel landete
schnell in Explore — 97,7 % der Aufrufe kamen von Menschen, die der Seite nicht
folgten — und brachte am Ende über 6.000 Menschen dazu, ihr zu folgen.

**In Zahlen:** 193.744 Aufrufe und 146.094 erreichte Konten; 8.200 Likes, 602
Kommentare, 6.600 Shares und 4.500 Speicherungen; durchschnittlich 21 Sekunden
Wiedergabezeit; Aufrufe aus dem Feed (45,5 %), dem Reels-Tab (32,4 %) und Explore
(16,6 %); 6.057 Follows.
"""

# ── case study 3: the 17-second Reel ──────────────────────────────────────
_P3_PROBLEM_FA = """\
محتوای فنی به‌راحتی اسکیپ می‌شود. ویدیویی درباره‌ی سوراخ کردن آجر فقط حدود سه ثانیه
فرصت دارد تا پیش از رد شدن انگشت مخاطب، کنجکاوی‌اش را برانگیزد؛ و در اینستاگرام،
ریلزی که تا آخر دیده نشود به آدم‌های زیادی نمی‌رسد. این ویدیو باید از لحظه‌ی اول توجه
را می‌گرفت و آن‌قدر کوتاه می‌بود که تا آخر دیده شود.
"""

_P3_BODY_FA = """\
یک ریلز آموزشی ۱۷ ثانیه‌ای، منتشرشده در خرداد ۱۴۰۴، که بر سه اصل کلیدی ساخته شد.

**۱. شکاف کنجکاوی (Curiosity Gap) در قاب اول.** تیتر و قاب اول — «اینجا داریم روی
آجر سوراخ‌کاری می‌کنیم، اما چرا؟» — در همان سه ثانیه‌ی اول یک سؤال فنی ساده در ذهن
مخاطب می‌کارد، و تنها راه رسیدن به جواب، ماندن تا آخر ویدیوست.

**۲. ریتم سریع و زمان‌بندی طلایی (Dynamic Editing).** ویدیو در کوتاه‌ترین زمانی که
روایت اجازه می‌داد — ۱۷ ثانیه — تدوین شد تا نرخ تکمیل (Completion Rate) به حداکثر
برسد.

**۳. هدف‌گیری دقیق مخاطب (Target Audience).** سناریو برای مخاطب اصلی برند نوشته شد:
معماران، سازندگان و آقایان فعال در صنعت ساختمان. نتیجه: ۸۳٫۲٪ مخاطبان این ویدیو مرد
بودند.

**عددها چه می‌گویند؟**

- **نرخ اسکیپ ۱۹٫۱٪** در برابر میانگین معمول ۴۲٫۸٪ صفحه؛ یعنی ویدیو در ثانیه‌های اول
  بیش از دو برابر ویدیوهای معمول صفحه مخاطب را نگه داشت.
- **میانگین تماشای ۱۶ ثانیه** برای ویدیویی ۱۷ ثانیه‌ای؛ یعنی نرخ تکمیلی نزدیک به ۹۵٪ —
  عددی بسیار قوی برای یک ریلز.
- **۳٬۰۶۵ فالوور هدفمند**، کاملاً ارگانیک و بدون یک ریال هزینه‌ی تبلیغاتی.
- **بیش از ۹۹٪ بازدیدها از تب ریلز (۶۸٫۴٪) و اکسپلور (۳۰٫۸٪)**؛ همان توزیعی که
  الگوریتم به محتوایی می‌دهد که تصمیم گرفته به آن میدان بدهد.

**در یک نگاه:** ۸٬۲۷۰٬۸۶۳ بازدید، ۲۶٬۲۷۱ لایک، ۱٬۱۸۴ ذخیره، ۹۸۴ اشتراک‌گذاری و ۲۸۹
کامنت؛ ۹۹٫۹٪ بیننده‌ها دنبال‌کننده‌ی صفحه نبودند؛ و مجموع زمان تماشا بیش از دو سال و
نیم.
"""

_P3_PROBLEM_EN = """\
Technical content is easy to skip. A video about drilling into a brick has about
three seconds to make someone curious before the thumb moves on, and on
Instagram a Reel that is not watched to the end is not shown to many more
people. This one had to earn attention immediately and be short enough to
finish.
"""

_P3_BODY_EN = """\
An educational Reel of 17 seconds, published in June 2025, built on three
principles.

**The curiosity gap.** The title and the opening frame — “Here we're drilling
into a brick… but why?” — put a simple technical question in the viewer's head in
the first three seconds, and the only way to the answer is to keep watching.

**Dynamic editing.** The video was cut to the shortest length that still told
the story — 17 seconds — to push the completion rate as high as it would go.

**A precise audience.** The scenario was written for the people who matter to
the brand: architects, builders and the men who make up most of the construction
trade. 83.2% of the audience was male.

**What the numbers show.**

- **A skip rate of 19.1%**, against the page's typical 42.8% — the video held
  people through the opening more than twice as well as usual.
- **An average watch time of 16 seconds** on a 17-second video: a completion rate
  close to 95%, a very strong figure for a Reel.
- **3,065 targeted followers**, entirely organic, without a rial spent on
  advertising.
- **Over 99% of views from the Reels tab (68.4%) and Explore (30.8%)** — the
  distribution the algorithm gives content it has decided to push.

**By the numbers:** 8,270,863 views, 26,271 likes, 1,184 saves, 984 shares and
289 comments; 99.9% of viewers were not following the page; and more than two and
a half years of total watch time.
"""

_P3_PROBLEM_DE = """\
Technischer Content wird leicht übersprungen. Ein Video über das Bohren in einen
Ziegel hat etwa drei Sekunden, um neugierig zu machen, bevor der Daumen
weiterwischt — und auf Instagram wird ein Reel, das nicht zu Ende gesehen wird,
kaum weiteren Menschen gezeigt. Dieses Video musste sofort Aufmerksamkeit
gewinnen und kurz genug sein, um bis zum Schluss gesehen zu werden.
"""

_P3_BODY_DE = """\
Ein 17-sekündiges Erklär-Reel, veröffentlicht im Juni 2025, gebaut auf drei
Prinzipien.

**Curiosity Gap im ersten Bild.** Titel und Eröffnungsbild — „Hier bohren wir in
einen Ziegel … aber warum?“ — setzen in den ersten drei Sekunden eine einfache
technische Frage in den Kopf, und die Antwort gibt es nur, wenn man dranbleibt.

**Dynamic Editing.** Das Video wurde auf die kürzeste Länge geschnitten, die die
Geschichte noch trägt — 17 Sekunden —, um die Abschlussrate (Completion Rate) so
hoch wie möglich zu treiben.

**Präzise Zielgruppe.** Das Drehbuch richtete sich an die Menschen, auf die es
der Marke ankommt: Architektur-, Bau- und Planungsprofis in einer stark männlich
geprägten Branche. Das Publikum war zu 83,2 % männlich.

**Was die Zahlen zeigen.**

- **Skip-Rate 19,1 %** gegenüber den sonst üblichen 42,8 % der Seite — das Video
  hielt die Menschen in den ersten Sekunden mehr als doppelt so gut.
- **Durchschnittlich 16 Sekunden Wiedergabe** bei 17 Sekunden Länge: eine
  Abschlussrate von fast 95 %, für ein Reel ein sehr starker Wert.
- **3.065 zielgerichtete Follower**, vollständig organisch, ohne einen Rial
  Werbebudget.
- **Über 99 % der Aufrufe aus dem Reels-Tab (68,4 %) und Explore (30,8 %)** — die
  Verteilung, die der Algorithmus Inhalten gibt, die er pushen will.

**In Zahlen:** 8.270.863 Aufrufe, 26.271 Likes, 1.184 Speicherungen, 984 Shares
und 289 Kommentare; 99,9 % der Zuschauer folgten der Seite nicht; insgesamt mehr
als zweieinhalb Jahre Wiedergabezeit.
"""

# ── experience descriptions ────────────────────────────────────────────────
_E_NAMASA_FA = """\
- طراحی و اجرای استراتژی‌های محتوایی برای افزایش تعامل کاربران و جذب مشتری
- مدیریت پروژه‌های تولید محتوا
- تحلیل داده‌های کاربران و به‌کارگیری نتایجش برای ارتقای کیفیت محتوا
- همکاری با تیم‌های طراحی و توسعه برای نیازسنجی دقیق بازار
- طراحی استراتژی ویدیومحور اینستاگرام؛ همان استراتژی‌ای که کیس استادی‌های این سایت، از
  جمله ریلزی با بیش از ۸ میلیون بازدید، حاصل آن است
"""

_E_NAMASA_EN = """\
- Developed and ran content strategies to raise user engagement and win customers
- Managed content production projects
- Analysed user data to raise the quality of the content
- Worked with the design and development teams on precise market research
- Built the video-first Instagram strategy behind the case studies on this site
"""

_E_NAMASA_DE = """\
- Entwicklung und Umsetzung von Content-Strategien für mehr Interaktion und Neukundschaft
- Leitung von Content-Produktionsprojekten
- Analyse von Nutzerdaten, um die Qualität der Inhalte zu steigern
- Zusammenarbeit mit Design- und Entwicklungsteams für eine präzise Marktanalyse
- Aufbau der videobasierten Instagram-Strategie hinter den Fallstudien auf dieser Seite
"""

_E_IDEA_FA = """\
- رهبری تیم تولید محتوا در خلق محتوای خلاقانه و هم‌راستا با هویت برند
- ایده‌پردازی و سناریونویسی کمپین‌های تبلیغاتی، و نظارت بر کیفیت اجرای آن‌ها
"""

_E_IDEA_EN = """\
- Led the content production team in creating creative content consistent with each brand's identity
- Developed ideas and wrote scenarios for advertising campaigns, and oversaw the quality of their execution
"""

_E_IDEA_DE = """\
- Führung des Content-Produktionsteams bei kreativen Inhalten im Einklang mit der Markenidentität
- Ideenentwicklung und Drehbücher für Werbekampagnen sowie Qualitätssicherung bei der Umsetzung
"""
