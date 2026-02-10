from rest_framework import serializers

from .models import Education, Message, Profile, Project, SkillCategory, Stat, ChatSession, ChatMessage


class StatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stat
        fields = ["id", "value", "label", "order"]


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ["id", "degree", "institution", "year", "gpa", "details", "order"]


class SkillCategorySerializer(serializers.ModelSerializer):
    photo_urls = serializers.SerializerMethodField()

    class Meta:
        model = SkillCategory
        fields = ["id", "name", "description", "order", "photo", "photo_urls"]

    def _build_url(self, request, url):
        return request.build_absolute_uri(url) if request else url

    def get_photo_urls(self, obj):
        if not obj.photo or not obj.photo.name:
            return None
        request = self.context.get("request")
        return {
            "original": self._build_url(request, obj.photo.original_url) if obj.photo.original_url else None,
            "icon": self._build_url(request, obj.photo.icon_url) if obj.photo.icon_url else None,
            "normal": self._build_url(request, obj.photo.normal_url) if obj.photo.normal_url else None,
            "large": self._build_url(request, obj.photo.large_url) if obj.photo.large_url else None,
        }


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "technologies",
            "github_url",
            "live_url",
            "image_url",
            "is_featured",
            "created_at",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    stats = StatSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    skills = SkillCategorySerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    avatar_urls = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "name",
            "role",
            "subtitle",
            "summary",
            "email",
            "github",
            "linkedin",
            "avatar_url",
            "avatar_urls",
            "stats",
            "education",
            "skills",
            "projects",
        ]

    def _build_url(self, request, url):
        return request.build_absolute_uri(url) if request else url

    def get_avatar_urls(self, obj):
        if not obj.avatar_url or not obj.avatar_url.name:
            return None
        request = self.context.get("request")
        return {
            "original": self._build_url(request, obj.avatar_url.original_url) if obj.avatar_url.original_url else None,
            "icon": self._build_url(request, obj.avatar_url.icon_url) if obj.avatar_url.icon_url else None,
            "normal": self._build_url(request, obj.avatar_url.normal_url) if obj.avatar_url.normal_url else None,
            "large": self._build_url(request, obj.avatar_url.large_url) if obj.avatar_url.large_url else None,
        }


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "name", "email", "subject", "message", "created_at"]
        read_only_fields = ["id", "created_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ["id", "session_id", "messages", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
