from django.contrib import admin

from .models import Education, Message, Profile, Project, SkillCategory, Stat, ChatSession, ChatMessage


class StatInline(admin.TabularInline):
    model = Stat
    extra = 1


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class SkillCategoryInline(admin.TabularInline):
    model = SkillCategory
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "email", "updated_at"]
    inlines = [StatInline, EducationInline, SkillCategoryInline]


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ["degree", "institution", "year", "profile"]
    list_filter = ["profile"]


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "profile", "order"]
    list_filter = ["profile"]


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
