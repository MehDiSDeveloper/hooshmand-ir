"""
The sitemap, in all three languages.

`i18n = True` writes one <url> per language — /, /en/ and /de/ — and
`alternates` links each to its siblings with xhtml:link hreflang, which is
what gets the German pages found by someone searching in German. x_default
is the unprefixed URL, matching the hreflang in base.html: it is the one that
picks a language by country.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.content.models import Post, Project


class _Multilingual(Sitemap):
    i18n = True
    alternates = True
    x_default = True


class StaticSitemap(_Multilingual):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        pages = ["home", "project_list", "resume", "about", "contact", "card"]
        # An empty blog is not offered in the nav, so it is not offered here.
        if Post.objects.filter(is_published=True).exists():
            pages.append("post_list")
        return pages

    def location(self, item):
        return reverse(item)


class ProjectSitemap(_Multilingual):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Project.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class PostSitemap(_Multilingual):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    "static": StaticSitemap,
    "projects": ProjectSitemap,
    "posts": PostSitemap,
}
