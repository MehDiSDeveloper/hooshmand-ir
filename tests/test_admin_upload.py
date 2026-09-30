"""The admin's photos and files can be changed, undone and removed.

A chosen file only travels when the form is saved; these pin that the save
lands the file, that the page it returns to shows it, that "clear" empties it,
and that no file field in the admin is left on the stock widget.
"""

import shutil
import tempfile
from io import BytesIO

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.test import TestCase, override_settings
from PIL import Image

from apps.content.admin import UploadWidget
from apps.content.models import Profile

MEDIA = tempfile.mkdtemp()


def png(name="roya.png"):
    buf = BytesIO()
    Image.new("RGB", (4, 4), "pink").save(buf, "PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


class EveryFileFieldTests(TestCase):
    def test_every_file_field_in_the_admin_uses_the_upload_widget_and_says_where_it_shows(self):
        checked = 0
        for model, model_admin in admin.site._registry.items():
            for field in model._meta.get_fields():
                if not isinstance(field, models.FileField):
                    continue
                with self.subTest(field=f"{model.__name__}.{field.name}"):
                    formfield = model_admin.formfield_for_dbfield(field, request=None)
                    self.assertIsInstance(formfield.widget, UploadWidget)
                    self.assertTrue(field.help_text, "say where on the site this file shows")
                checked += 1
        self.assertGreaterEqual(checked, 4)


@override_settings(MEDIA_ROOT=MEDIA, GEO_LANGUAGE_ENABLED=False)
class ProfilePhotoTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        user = get_user_model().objects.create_superuser("owner", "o@example.com", "pw")
        self.client.force_login(user)
        # Every Persian column is required (@i18n_fields), so the form fills them all.
        self.persian = {f"{name}_fa": "رویا" for name in Profile.I18N_FIELDS}
        Profile.objects.update_or_create(pk=1, defaults=self.persian)
        self.url = "/admin/content/profile/1/change/"

    def form(self, **extra):
        return {**self.persian, "is_available": "on", **extra}

    def test_the_list_opens_the_form(self):
        self.assertRedirects(self.client.get("/admin/content/profile/"), self.url)

    def test_the_form_starts_with_the_files_and_explains_itself(self):
        page = self.client.get(self.url).content.decode()
        self.assertIn("js/admin-upload.js", page)
        self.assertIn("data-upload", page)
        self.assertIn("business card", page)  # the avatar's help text
        self.assertLess(page.index('name="avatar"'), page.index('name="full_name_fa"'))
        self.assertLess(page.index('name="_save"'), page.index('name="avatar"'))  # save_on_top

    def test_save_puts_the_photo_on_the_site_and_shows_it(self):
        response = self.client.post(self.url, self.form(avatar=png()), follow=True)
        avatar = Profile.load().avatar
        self.assertTrue(avatar.name.startswith("profile/roya"))
        self.assertContains(response, 'class="upload-live"')
        self.assertContains(response, avatar.url)
        self.assertContains(self.client.get("/"), avatar.url)

    def test_clear_removes_it(self):
        self.client.post(self.url, self.form(avatar=png()))
        self.client.post(self.url, self.form(**{"avatar-clear": "on"}))
        self.assertFalse(Profile.load().avatar)
