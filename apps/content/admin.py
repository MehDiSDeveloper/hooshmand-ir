"""
Stock Django admin — the interim way to edit content.

The custom lightweight panel is a later piece of work (see CLAUDE.md). Until it
exists this is what makes the database writable, and it costs nothing: the
per-language columns render as three plain inputs side by side.

Every file field goes through `UploadWidget`, because the stock input hides the
one thing that matters: a chosen file reaches the site only when «ذخیره» is
pressed.
"""

from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.shortcuts import redirect
from django.utils.html import format_html

from .models import LANG_CODES, Experience, Message, Post, Profile, Project, Skill, SkillGroup, Tag

LANG_NAMES = {"fa": "فارسی — Persian", "en": "English", "de": "Deutsch — German"}


def _per_language(*names):
    return [
        (LANG_NAMES.get(code, code), {"fields": [f"{name}_{code}" for name in names]})
        for code in LANG_CODES
    ]


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".svg")


class UploadWidget(AdminFileWidget):
    """The stock file input, plus what it never tells you.

    It shows the file that is live now, a preview of the one waiting, an undo
    for the choice, and — through admin-upload.js — a bar that stays on screen
    until «ذخیره» is pressed.
    """

    class Media:
        css = {"all": ["css/admin-upload.css"]}
        js = ["js/admin-upload.js"]

    def render(self, name, value, attrs=None, renderer=None):
        live = ""
        if value and getattr(value, "url", None) and value.name.lower().endswith(IMAGE_EXTENSIONS):
            live = format_html(
                '<a class="upload-live" href="{0}" target="_blank" rel="noopener" '
                'title="روی سایت همین است"><img src="{0}" alt=""></a>',
                value.url,
            )
        return format_html(
            '<div class="upload" data-upload>{}<div class="upload-field">{}'
            '<div class="upload-new" hidden><img alt="" hidden>'
            '<span><b class="upload-name"></b><small>با «ذخیره» روی سایت می‌نشیند</small></span>'
            '<button type="button" class="button" data-upload-undo>✕ منصرف شدم</button></div>'
            '<small class="upload-gone" hidden>با «ذخیره» از سایت برداشته می‌شود</small>'
            "</div></div>",
            live,
            super().render(name, value, attrs, renderer),
        )


# Every admin with a file field uses this (tests/test_admin_upload.py checks).
# ImageField needs its own key: the admin matches the field's own class before
# its parent's.
UPLOADS = {
    models.ImageField: {"widget": UploadWidget(attrs={"accept": "image/*"})},
    models.FileField: {"widget": UploadWidget},
}


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """One row, so the list is skipped and the files come first.

    The form is long (every text in three languages); with the stock order the
    portrait sat at the top but «ذخیره» only at the very bottom, so a chosen
    photo looked taken while nothing had been sent.
    """

    formfield_overrides = UPLOADS
    save_on_top = True
    fieldsets = [
        (
            "عکس و فایل",
            {
                "fields": ("avatar", "resume_file"),
                "description": "فایل را انتخاب کنید و «ذخیره» را بزنید؛ تا ذخیره نشود روی سایت نمی‌آید. "
                "برای برداشتن فایلی که الان روی سایت است، تیک «پاک کردن» کنارش را بزنید و ذخیره کنید.",
            },
        ),
        (
            "تماس",
            {"fields": ("email", "phone", "instagram", "telegram", "linkedin", "github", "twitter", "website", "is_available")},
        ),
        *_per_language(*Profile.I18N_FIELDS),
    ]

    def changelist_view(self, request, extra_context=None):
        # A list of one row is a detour, and «ذخیره» lands here: send it back
        # to the form, where the success message and the new photo show.
        return redirect("admin:content_profile_change", Profile.load().pk)

    def has_add_permission(self, request):
        return not Profile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


@admin.register(SkillGroup)
class SkillGroupAdmin(admin.ModelAdmin):
    list_display = ("name_fa", "name_en", "order")
    inlines = [SkillInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("slug", "name_fa", "name_en", "name_de")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    formfield_overrides = UPLOADS
    save_on_top = True
    list_display = ("slug", "title_fa", "year", "is_featured", "is_published", "order")
    list_filter = ("is_featured", "is_published", "tags")
    list_editable = ("is_featured", "is_published", "order")
    search_fields = ("slug", "title_fa", "title_en", "title_de")
    filter_horizontal = ("tags",)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("org_fa", "role_fa", "kind", "start", "end")
    list_filter = ("kind",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    formfield_overrides = UPLOADS
    save_on_top = True
    list_display = ("slug", "title_fa", "published_at", "is_published")
    list_filter = ("is_published", "tags")
    search_fields = ("slug", "title_fa", "title_en", "title_de")
    filter_horizontal = ("tags",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_handled")
    list_filter = ("is_handled", "language")
    readonly_fields = ("name", "email", "subject", "body", "language", "created_at")
    search_fields = ("name", "email", "body")
