import os

from django.contrib import admin
from django.utils.html import format_html

from .image_utils import UploadedFile
from .models import Education, Message, Profile, Project, SkillCategory, Stat, ChatSession, ChatMessage


def _filesize_display(field):
    """Return a human-readable file-size string for a FileField."""
    if not field:
        return "—"
    try:
        size = field.size
    except (FileNotFoundError, ValueError):
        return "—"
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.2f} MB"


class StatInline(admin.TabularInline):
    model = Stat
    extra = 1


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class SkillCategoryInline(admin.TabularInline):
    model = SkillCategory
    extra = 1
    readonly_fields = ["photo_preview", "photo_size"]

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height:60px;border-radius:4px"/>', obj.photo.url)
        return "—"
    photo_preview.short_description = "Preview"

    def photo_size(self, obj):
        return _filesize_display(obj.photo)
    photo_size.short_description = "File Size"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "email", "avatar_preview", "avatar_size", "updated_at"]
    readonly_fields = ["avatar_preview", "avatar_size"]
    inlines = [StatInline, EducationInline, SkillCategoryInline]

    def avatar_preview(self, obj):
        if obj.avatar_url:
            return format_html('<img src="{}" style="max-height:80px;border-radius:8px"/>', obj.avatar_url.url)
        return "—"
    avatar_preview.short_description = "Avatar"

    def avatar_size(self, obj):
        return _filesize_display(obj.avatar_url)
    avatar_size.short_description = "File Size"


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ["degree", "institution", "year", "profile"]
    list_filter = ["profile"]


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "photo_preview", "photo_size", "profile", "order"]
    list_filter = ["profile"]
    readonly_fields = ["photo_preview", "photo_size"]

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height:60px;border-radius:4px"/>', obj.photo.url)
        return "—"
    photo_preview.short_description = "Preview"

    def photo_size(self, obj):
        return _filesize_display(obj.photo)
    photo_size.short_description = "File Size"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "profile", "is_featured", "order", "created_at"]
    list_filter = ["is_featured", "profile"]
    search_fields = ["title", "description"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "subject", "created_at", "is_read"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    actions = ["mark_as_read", "mark_as_unread"]

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ["label", "value", "profile", "order"]
    list_filter = ["profile"]


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ["session_id", "created_at", "updated_at"]
    readonly_fields = ["session_id", "created_at", "updated_at"]
    search_fields = ["session_id"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["session", "role", "content_preview", "created_at"]
    list_filter = ["role", "created_at"]
    search_fields = ["content", "session__session_id"]
    
    def content_preview(self, obj):
        return obj.content[:50]
    content_preview.short_description = "Content"


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = [
        "original_filename",
        "uploaded_by",
        "content_field",
        "human_size",
        "created_at",
    ]
    list_filter = ["content_field", "created_at", "uploaded_by"]
    search_fields = ["original_filename", "content_field"]
    readonly_fields = [
        "uploaded_by",
        "original_filename",
        "original_size",
        "path_original",
        "path_icon",
        "path_normal",
        "path_large",
        "content_field",
        "created_at",
        "updated_at",
    ]

    def human_size(self, obj):
        size = obj.original_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 * 1024):.2f} MB"
    human_size.short_description = "Original Size"
