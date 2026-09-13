"""
Project and post views.

Filtering is deliberately client-side: a personal site has tens of projects,
not thousands, so the whole list is rendered once and the tag chips hide rows
instantly with no request. The server still honours ?tag= so a filtered list is
a shareable URL and a crawler sees real pages.
"""

from __future__ import annotations

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Post, Project, Tag


def _tags_for(relation: str):
    """Tags in use by published rows of `relation`, each carrying its count `n`.

    The count is what the filter chip shows, so a reader knows before clicking
    whether a tag holds one project or five.
    """
    published = Q(**{f"{relation}__is_published": True})
    return Tag.objects.annotate(n=Count(relation, filter=published, distinct=True)).filter(n__gt=0)


def project_list(request):
    projects = Project.objects.filter(is_published=True).prefetch_related("tags")
    return render(
        request,
        "projects/list.html",
        {"projects": projects, "tags": _tags_for("projects"), "active_tag": request.GET.get("tag", "")},
    )


def project_detail(request, slug: str):
    project = get_object_or_404(
        Project.objects.prefetch_related("tags"), slug=slug, is_published=True
    )
    published = list(Project.objects.filter(is_published=True).values_list("slug", flat=True))
    index = published.index(slug)
    next_index = (index + 1) % len(published) if len(published) > 1 else None
    next_project = (
        Project.objects.prefetch_related("tags").filter(slug=published[next_index]).first()
        if next_index is not None
        else None
    )
    return render(
        request,
        "projects/detail.html",
        {
            "project": project,
            "project_index": index + 1,
            "next_project": next_project,
            # The number on the next card is that project's place in the list,
            # so it matches the card it had on /projects/.
            "next_index": (next_index or 0) + 1,
        },
    )


def post_list(request):
    posts = Post.objects.filter(is_published=True).prefetch_related("tags")
    return render(
        request,
        "blog/list.html",
        {"posts": posts, "tags": _tags_for("posts"), "active_tag": request.GET.get("tag", "")},
    )


def post_detail(request, slug: str):
    post = get_object_or_404(Post.objects.prefetch_related("tags"), slug=slug, is_published=True)
    return render(request, "blog/detail.html", {"post": post})
