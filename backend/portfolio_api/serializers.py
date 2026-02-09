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
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = SkillCategory
        fields = ["id", "name", "description", "order", "photo", "photo_url"]

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url
        return None


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
            "stats",
            "education",
            "skills",
            "projects",
        ]


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
