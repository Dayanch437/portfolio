import io
import os
import threading
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.fields.files import FieldFile
from PIL import Image


# ---------------------------------------------------------------------------
# Size presets — every upload produces all three variants + original
# ---------------------------------------------------------------------------
SIZE_PRESETS = {
    "icon": (256, 256),
    "normal": (800, 800),
    "large": (1920, 1920),
}

VARIANT_FOLDERS = ("original", "icon", "normal", "large")

WEBP_INITIAL_QUALITY = 85
WEBP_MIN_QUALITY = 60
TARGET_MAX_SIZE = 500 * 1024


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _encode_webp(img: Image.Image, quality: int) -> bytes:
    """Encode a PIL Image to WebP bytes."""
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=quality, method=6)
    return buffer.getvalue()


def _compress(img: Image.Image, max_dimensions: tuple[int, int]) -> bytes:
    """Resize + adaptive-quality WebP encode."""
    copy = img.copy()
    copy.thumbnail(max_dimensions, Image.LANCZOS)

    quality = WEBP_INITIAL_QUALITY
    webp_bytes = _encode_webp(copy, quality)

    while len(webp_bytes) > TARGET_MAX_SIZE and quality > WEBP_MIN_QUALITY:
        quality -= 5
        webp_bytes = _encode_webp(copy, quality)

    return webp_bytes


def optimize_image(image_field, max_dimensions=(1920, 1920)):
    """
    Optimize an uploaded image (single-variant helper kept for standalone use).

    Returns (ContentFile, new_filename) or (None, None).
    """
    if not image_field:
        return None, None

    try:
        image_field.seek(0)
        img = Image.open(image_field)
    except Exception:
        return None, None

    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")

    webp_bytes = _compress(img, max_dimensions)
    original_name = Path(image_field.name).stem
    new_filename = f"{original_name}.webp"
    return ContentFile(webp_bytes), new_filename


def _generate_variants(image_field):
    """
    Generate original + icon / normal / large WebP variants.
    """
    if not image_field:
        return None, None

    try:
        image_field.seek(0)
        raw_bytes = image_field.read()
        image_field.seek(0)
        img = Image.open(image_field)
    except Exception:
        return None, None

    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")

    original_name = Path(image_field.name).name
    stem = Path(image_field.name).stem

    variants = {
        "original": (ContentFile(raw_bytes), original_name),
    }
    for preset, dimensions in SIZE_PRESETS.items():
        webp_bytes = _compress(img, dimensions)
        variants[preset] = (ContentFile(webp_bytes), f"{stem}.webp")

    return variants, stem


def delete_file(path):
    """Safely delete a file from disk if it exists."""
    if path and os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# UploadedFile — audit log for every image that goes through the field
# ---------------------------------------------------------------------------

class UploadedFile(models.Model):
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
    )
    original_filename = models.CharField(max_length=255)
    original_size = models.PositiveIntegerField(help_text="Original file size in bytes")

    path_original = models.CharField(max_length=500)
    path_icon = models.CharField(max_length=500)
    path_normal = models.CharField(max_length=500)
    path_large = models.CharField(max_length=500)

    content_field = models.CharField(
        max_length=200,
        help_text="app_label.Model.field that owns this file",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        user = self.uploaded_by or "anonymous"
        return f"{self.original_filename} by {user} ({self.created_at:%Y-%m-%d %H:%M})"


# ---------------------------------------------------------------------------
# CompressedImageField — saves original + icon / normal / large
# ---------------------------------------------------------------------------

class CompressedFieldFile(FieldFile):
    """
    Custom FieldFile that generates **four** files on save.

    The field value stores the *normal* variant path.
    All variant URLs are resolved from the UploadedFile DB record
    (not path manipulation) to avoid dedup suffix mismatches.
    """

    def _get_record(self):
        """Get the UploadedFile record for this field value."""
        if not self.name:
            return None
        try:
            return UploadedFile.objects.filter(path_normal=self.name).first()
        except Exception:
            return None

    @property
    def original_url(self):
        rec = self._get_record()
        if rec and rec.path_original:
            return self.storage.url(rec.path_original)
        return None

    @property
    def icon_url(self):
        rec = self._get_record()
        if rec and rec.path_icon:
            return self.storage.url(rec.path_icon)
        return None

    @property
    def normal_url(self):
        return self.url if self.name else None

    @property
    def large_url(self):
        rec = self._get_record()
        if rec and rec.path_large:
            return self.storage.url(rec.path_large)
        return None

    @property
    def all_urls(self):
        """Return a dict of all variant URLs."""
        rec = self._get_record()
        if not rec:
            return {
                "original": None,
                "icon": None,
                "normal": self.url if self.name else None,
                "large": None,
            }
        return {
            "original": self.storage.url(rec.path_original) if rec.path_original else None,
            "icon": self.storage.url(rec.path_icon) if rec.path_icon else None,
            "normal": self.url if self.name else None,
            "large": self.storage.url(rec.path_large) if rec.path_large else None,
        }

    # -- save ----------------------------------------------------------------

    def save(self, name, content, save=True):
        """Intercept save to produce four files in separate sub-folders."""
        variants, stem = _generate_variants(content)
        if variants is None:
            super().save(name, content, save=save)
            return

        upload_to = self.field.upload_to
        if callable(upload_to):
            upload_to = str(Path(upload_to(self.instance, name)).parent)

        saved_paths = {}

        # Save original, icon, large as siblings
        for preset in ("original", "icon", "large"):
            cf, fname = variants[preset]
            variant_path = os.path.join(upload_to, preset, fname)
            if self.storage.exists(variant_path):
                self.storage.delete(variant_path)
            actual = self.storage.save(variant_path, cf)
            saved_paths[preset] = actual

        # Save normal via parent (this sets self.name = the actual saved path)
        cf, fname = variants["normal"]
        normal_path = os.path.join(upload_to, "normal", fname)
        if self.storage.exists(normal_path):
            self.storage.delete(normal_path)
        super().save(normal_path, cf, save=save)
        saved_paths["normal"] = self.name

        # --- Create the audit record ----------------------------------------
        original_cf, original_fname = variants["original"]
        try:
            content.seek(0)
            original_size = len(content.read())
            content.seek(0)
        except Exception:
            original_size = 0

        user = _get_current_user()

        field_label = (
            f"{self.instance._meta.app_label}."
            f"{self.instance._meta.object_name}."
            f"{self.field.name}"
        )

        UploadedFile.objects.create(
            uploaded_by=user,
            original_filename=original_fname,
            original_size=original_size,
            path_original=saved_paths["original"],
            path_icon=saved_paths["icon"],
            path_normal=saved_paths["normal"],
            path_large=saved_paths["large"],
            content_field=field_label,
        )

    # -- delete --------------------------------------------------------------

    def delete(self, save=True):
        """Delete all variant files from storage and the audit record."""
        if self.name:
            rec = self._get_record()
            if rec:
                # Delete all variants using exact paths from DB
                for path in (rec.path_original, rec.path_icon, rec.path_large):
                    if path and self.storage.exists(path):
                        self.storage.delete(path)
                rec.delete()

        super().delete(save=save)


class CompressedImageField(models.FileField):
    """
    A ``FileField`` that automatically generates four files on upload.

    All variant URLs are resolved from the ``UploadedFile`` DB record,
    so Django storage dedup suffixes (e.g. ``photo_abc123.webp``) are
    handled correctly.
    """

    attr_class = CompressedFieldFile

    def deconstruct(self):
        return super().deconstruct()

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        from django.db.models.signals import post_delete, pre_save

        pre_save.connect(self._remember_old_file, sender=cls)
        post_delete.connect(self._delete_file_on_model_delete, sender=cls)

    def _remember_old_file(self, sender, instance, **kwargs):
        if not instance.pk:
            return
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return

        old_field_file = getattr(old_instance, self.attname, None)
        if old_field_file and old_field_file.name:
            attr = f"_old_{self.attname}_name"
            setattr(instance, attr, old_field_file.name)

        from django.db.models.signals import post_save

        dispatch_uid = f"cleanup_{self.attname}_{id(instance)}"

        def _cleanup_after_save(sender, instance, **kw):
            post_save.disconnect(
                _cleanup_after_save, sender=sender, dispatch_uid=dispatch_uid
            )
            attr = f"_old_{self.attname}_name"
            old_name = getattr(instance, attr, None)
            new_file = getattr(instance, self.attname, None)
            new_name = new_file.name if new_file else None
            if old_name and old_name != new_name:
                storage = new_file.storage if new_file else old_field_file.storage
                # Delete all old variants using DB record
                try:
                    rec = UploadedFile.objects.filter(path_normal=old_name).first()
                    if rec:
                        for path in (rec.path_original, rec.path_icon, rec.path_large):
                            if path and storage.exists(path):
                                storage.delete(path)
                        rec.delete()
                except Exception:
                    pass
                # Delete old normal
                if storage.exists(old_name):
                    storage.delete(old_name)

        post_save.connect(
            _cleanup_after_save, sender=sender, dispatch_uid=dispatch_uid
        )

    def _delete_file_on_model_delete(self, sender, instance, **kwargs):
        field_file = getattr(instance, self.attname, None)
        if field_file:
            field_file.delete(save=False)


# ---------------------------------------------------------------------------
# Thread-local middleware to capture the current user for audit logging
# ---------------------------------------------------------------------------

_thread_locals = threading.local()


def _get_current_user():
    """Return the current request user, or None."""
    user = getattr(_thread_locals, "user", None)
    if user and user.is_authenticated:
        return user
    return None


class CurrentUserMiddleware:
    """
    Stores ``request.user`` in thread-local storage so
    ``CompressedImageField`` can record who uploaded a file.

    Add to MIDDLEWARE **after** ``AuthenticationMiddleware``.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = getattr(request, "user", None)
        try:
            return self.get_response(request)
        finally:
            _thread_locals.user = None
