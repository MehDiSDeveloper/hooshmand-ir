"""
Seed the site with placeholder content in all three languages.

Idempotent: it upserts by slug, so running it twice changes nothing. It exists
so a fresh clone renders a complete site instead of an empty shell — every
string it writes is a placeholder. Roya's real content is `seed_profile`, and
running this on a live database overwrites her profile.

    python manage.py seed_demo
    python manage.py seed_demo --wipe   # start over
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.content.models import (
    Experience,
    Post,
    Profile,
    Project,
    Skill,
    SkillGroup,
    Tag,
)


class Command(BaseCommand):
    help = "Fill the database with three-language placeholder content."

    def add_arguments(self, parser):
        parser.add_argument("--wipe", action="store_true", help="Delete existing content first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["wipe"]:
            for model in (Project, Post, Experience, Skill, SkillGroup, Tag):
                model.objects.all().delete()
            self.stdout.write(self.style.WARNING("wiped existing content"))

        self._profile()
        tags = self._tags()
        self._skills()
        self._projects(tags)
        self._experience()
        self._posts(tags)
        self.stdout.write(self.style.SUCCESS("seeded — every string here is a placeholder"))

    # ── profile ───────────────────────────────────────────────────────────
    def _profile(self):
        p = Profile.load()
        p.full_name_fa = "رویا هوشمند"
        p.full_name_en = "Roya Hooshmand"
        p.full_name_de = "Roya Hooshmand"

        p.headline_fa = "استراتژیست شبکه‌های اجتماعی و محتوا"
        p.headline_en = "Social media & content strategist"
        p.headline_de = "Social Media & Content Strategist"

        p.intro_fa = (
            "به برندها کمک می‌کنم در شبکه‌های اجتماعی دیده شوند — از استراتژی محتوا و "
            "سناریونویسی تا تحلیل داده. *این متن نمونه است.*"
        )
        p.intro_en = (
            "I help brands get seen on social media — from content strategy and scenario "
            "writing to data analysis. *Placeholder text.*"
        )
        p.intro_de = (
            "Ich helfe Marken, in sozialen Medien gesehen zu werden — von der Content-Strategie "
            "bis zur Datenanalyse. *Platzhaltertext.*"
        )

        p.bio_fa = (
            "### چطور کار می‌کنم\n\n"
            "با یک مخاطب مشخص شروع می‌کنم، نه با یک ترند. اول می‌فهمم چه کسی باید ببیند و چرا "
            "باید تا آخر بماند؛ سناریو از همان‌جا بیرون می‌آید.\n\n"
            "*این متن نمونه است و باید با روایت خودتان جایگزین شود.*"
        )
        p.bio_en = (
            "### How I work\n\n"
            "I start from a concrete audience, not from a trend. First I work out who needs to see "
            "it and why they would stay to the end; the scenario falls out of that.\n\n"
            "*Placeholder text — replace with your own.*"
        )
        p.bio_de = (
            "### Wie ich arbeite\n\n"
            "Ich beginne bei einer konkreten Zielgruppe, nicht bei einem Trend.\n\n"
            "*Platzhaltertext — bitte ersetzen.*"
        )

        p.location_fa, p.location_en, p.location_de = "تهران، ایران", "Tehran, Iran", "Teheran, Iran"
        p.now_fa = "روی استراتژی محتوای یک برند صنعتی کار می‌کنم."
        p.now_en = "Working on the content strategy of an industrial brand."
        p.now_de = "Ich arbeite an der Content-Strategie einer Industriemarke."
        p.availability_fa, p.availability_en, p.availability_de = "آمادهٔ همکاری", "Open to work", "Offen für Projekte"

        p.email = "hello@hooshmand.ir"
        p.instagram = ""
        p.github = ""
        p.linkedin = ""
        p.telegram = ""
        p.is_available = True
        p.save()

    # ── tags ──────────────────────────────────────────────────────────────
    def _tags(self) -> dict[str, Tag]:
        rows = [
            ("instagram", "اینستاگرام", "Instagram", "Instagram"),
            ("content-strategy", "استراتژی محتوا", "Content strategy", "Content-Strategie"),
            ("video", "ویدیو مارکتینگ", "Video marketing", "Videomarketing"),
            ("analytics", "تحلیل داده", "Analytics", "Analyse"),
            ("notes", "یادداشت", "Notes", "Notizen"),
            ("brand", "برند", "Brand", "Marke"),
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
        groups = [
            (("استراتژی", "Strategy", "Strategie"), 0,
             [("Social media strategy", True), ("Content strategy", True), ("Campaign planning", False)]),
            (("محتوا", "Content", "Content"), 1,
             [("Scenario writing", True), ("Copywriting", False), ("Video editing", False)]),
            (("داده و ابزار", "Data & tools", "Daten & Tools"), 2,
             [("Instagram Insights", True), ("Google Analytics", False), ("Canva", False)]),
        ]
        for (fa, en, de), order, skills in groups:
            group, _ = SkillGroup.objects.update_or_create(
                name_fa=fa, defaults={"name_en": en, "name_de": de, "order": order}
            )
            group.skills.all().delete()
            for i, (name, primary) in enumerate(skills):
                Skill.objects.create(group=group, name=name, order=i, is_primary=primary)

    # ── projects ──────────────────────────────────────────────────────────
    def _projects(self, tags):
        rows = [
            ("sample-campaign", "Instagram Reels, Scenario writing", ["instagram", "video"],
             ("کمپین نمونه", "Sample campaign", "Beispielkampagne")),
            ("sample-content-strategy", "Content strategy, Content calendar", ["content-strategy", "brand"],
             ("استراتژی محتوای نمونه", "Sample content strategy", "Beispiel-Content-Strategie")),
            ("sample-analytics-report", "Instagram Insights, Google Analytics", ["analytics"],
             ("گزارش تحلیلی نمونه", "Sample analytics report", "Beispiel-Analysebericht")),
        ]
        placeholder = {
            "fa": ("شرح این نمونه‌کار را در پنل مدیریت بنویسید.", "نتیجه را در یک خط بنویسید.", "*این متن نمونه است.*"),
            "en": ("Write this case study in the admin.", "The result, in one line.", "*Placeholder text.*"),
            "de": ("Beschreiben Sie diese Arbeit im Admin.", "Das Ergebnis in einer Zeile.", "*Platzhaltertext.*"),
        }
        for order, (slug, stack, tag_slugs, titles) in enumerate(rows):
            defaults = {
                "year": 2025,
                "stack": stack,
                "is_featured": True,
                "is_published": True,
                "order": order,
            }
            for code, title in zip(("fa", "en", "de"), titles):
                summary, outcome, body = placeholder[code]
                defaults[f"title_{code}"] = title
                defaults[f"summary_{code}"] = summary
                defaults[f"outcome_{code}"] = outcome
                defaults[f"body_{code}"] = body
            project, _ = Project.objects.update_or_create(slug=slug, defaults=defaults)
            project.tags.set([tags[s] for s in tag_slugs])

    # ── experience ────────────────────────────────────────────────────────
    def _experience(self):
        rows = [
            {
                "kind": Experience.Kind.WORK,
                "start": date(2024, 3, 20),
                "end": None,
                "fa": ("نام شرکت", "استراتژیست محتوا", "تهران", "شرح این نقش را در پنل مدیریت بنویسید."),
                "en": ("Company name", "Content strategist", "Tehran", "Write this role in the admin."),
                "de": ("Firmenname", "Content Strategist", "Teheran", ""),
            },
            {
                "kind": Experience.Kind.WORK,
                "start": date(2021, 3, 21),
                "end": date(2024, 3, 20),
                "fa": ("نام شرکت", "سرپرست تیم تولید محتوا", "تهران", ""),
                "en": ("Company name", "Content production lead", "Tehran", ""),
                "de": ("Firmenname", "Team Lead Content-Produktion", "Teheran", ""),
            },
            {
                "kind": Experience.Kind.EDUCATION,
                "start": date(2016, 9, 1),
                "end": date(2020, 7, 1),
                "fa": ("نام دانشگاه", "نام مدرک", "", ""),
                "en": ("University name", "Degree", "", ""),
                "de": ("Universität", "Abschluss", "", ""),
            },
        ]
        for order, row in enumerate(rows):
            defaults = {"kind": row["kind"], "start": row["start"], "end": row["end"], "order": order}
            for code in ("fa", "en", "de"):
                org, role, loc, desc = row[code]
                defaults[f"org_{code}"] = org
                defaults[f"role_{code}"] = role
                defaults[f"location_{code}"] = loc
                defaults[f"description_{code}"] = desc
            Experience.objects.update_or_create(
                org_fa=row["fa"][0], start=row["start"], defaults=defaults
            )

    # ── posts ─────────────────────────────────────────────────────────────
    def _posts(self, tags):
        rows = [
            {
                "slug": "hook-in-three-seconds",
                "tags": ["video", "notes"],
                "days": 6,
                "fa": (
                    "سه ثانیهٔ اول",
                    "ریلزی که در سه ثانیهٔ اول سؤالی نسازد، معمولاً تا آخر دیده نمی‌شود.",
                    "مخاطب پیش از آنکه تصمیم بگیرد بماند، فقط یک قاب و یک جمله می‌بیند.\n\n*این نوشتهٔ نمونه است.*",
                ),
                "en": (
                    "The first three seconds",
                    "A Reel that does not open a question in its first three seconds is rarely watched to the end.",
                    "Before a viewer decides to stay, they see one frame and one line.\n\n*Placeholder post.*",
                ),
                "de": (
                    "Die ersten drei Sekunden",
                    "Ein Reel ohne Frage in den ersten drei Sekunden wird selten zu Ende gesehen.",
                    "*Platzhalterbeitrag.*",
                ),
            },
            {
                "slug": "saves-over-likes",
                "tags": ["analytics", "notes"],
                "days": 21,
                "fa": (
                    "ذخیره، مهم‌تر از لایک",
                    "لایک یعنی «دیدم»؛ ذخیره یعنی «به کارم می‌آید».",
                    "در محتوای آموزشی، نسبت ذخیره به بازدید گویاتر از تعداد لایک است.\n\n*این نوشتهٔ نمونه است.*",
                ),
                "en": (
                    "Saves over likes",
                    "A like says “I saw it”; a save says “I will need this”.",
                    "For educational content, saves per view say more than the like count.\n\n*Placeholder post.*",
                ),
                "de": (
                    "Speichern schlägt Liken",
                    "Ein Like sagt „gesehen“, ein Speichern sagt „brauche ich noch“.",
                    "*Platzhalterbeitrag.*",
                ),
            },
        ]

        for row in rows:
            defaults = {
                "published_at": timezone.now() - timezone.timedelta(days=row["days"]),
                "is_published": True,
            }
            for code in ("fa", "en", "de"):
                title, excerpt, body = row[code]
                defaults[f"title_{code}"] = title
                defaults[f"excerpt_{code}"] = excerpt
                defaults[f"body_{code}"] = body
            post, _ = Post.objects.update_or_create(slug=row["slug"], defaults=defaults)
            post.tags.set([tags[s] for s in row["tags"]])
