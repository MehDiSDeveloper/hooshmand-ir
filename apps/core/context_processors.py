"""Everything every template needs, resolved once per request."""

from __future__ import annotations

from django.conf import settings
from django.urls import translate_url
from django.utils.translation import get_language

from django.urls import reverse

from apps.content.models import Post, Profile, Project

from .i18n import t

RTL_LANGUAGES = {"fa", "ar", "he"}


def _has_writing() -> bool:
    """Whether the writing section is worth offering at all.

    An empty blog behind a nav link reads worse than no blog: a reader who
    clicks "Writing" and lands on nothing concludes the site is unfinished.
    The link, the palette entry and the section come back on their own the
    moment a post is published.
    """
    return Post.objects.filter(is_published=True).exists()


def _command_index() -> list[dict]:
    """What Ctrl+K can jump to. Ships inside the page, so opening costs nothing.

    Two small queries per request. If this site ever grows past a few hundred
    rows, the answer is to cache this list, not to make the palette fetch.
    """
    # "i" is the icon id in templates/partials/icons.html, without the "i-".
    pages = [
        ("nav.home", "home", "home"),
        ("nav.projects", "project_list", "grid"),
        ("nav.resume", "resume", "doc"),
        ("nav.about", "about", "user"),
        ("nav.contact", "contact", "mail"),
        ("nav.card", "card", "qr"),
    ]
    index = [{"t": t(key), "u": reverse(name), "k": "", "i": icon} for key, name, icon in pages]
    if _has_writing():
        index.insert(4, {"t": t("nav.writing"), "u": reverse("post_list"), "k": "", "i": "pen"})
    for project in Project.objects.filter(is_published=True):
        index.append({"t": project.tr("title"), "u": project.get_absolute_url(), "k": t("projects.title"), "i": "target"})
    for post in Post.objects.filter(is_published=True)[:30]:
        index.append({"t": post.tr("title"), "u": post.get_absolute_url(), "k": t("blog.title"), "i": "pen"})
    return index


def site(request):
    lang = (get_language() or settings.LANGUAGE_CODE).split("-")[0]
    path = request.get_full_path()
    return {
        "profile": Profile.load(),
        "has_writing": _has_writing(),
        "cmdk_index": _command_index(),
        "lang": lang,
        "text_dir": "rtl" if lang in RTL_LANGUAGES else "ltr",
        "site_url": settings.SITE_URL,
        # One entry per language, each pointing at *this* page in that language,
        # so switching never dumps the reader back on the home page.
        "language_links": [
            {
                "code": code,
                "label": label,
                "native": {"fa": "فارسی", "en": "English", "de": "Deutsch"}.get(code, label),
                "url": translate_url(path, code),
                "is_active": code == lang,
            }
            for code, label in settings.LANGUAGES
        ],
    }
