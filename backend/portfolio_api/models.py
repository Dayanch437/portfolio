import os

from django.db import models

from .image_utils import delete_file, optimize_image


class Profile(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300)
    summary = models.TextField()
    email = models.EmailField()
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    avatar_url = models.FileField(("Avatar"), upload_to="avatars/", max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Track the old file so we can delete it after a successful save
        old_file_path = None
        if self.pk:
            try:
                old_instance = Profile.objects.get(pk=self.pk)
                if old_instance.avatar_url:
                    old_file_path = old_instance.avatar_url.path
            except Profile.DoesNotExist:
                pass

        # Optimize the uploaded avatar
        if self.avatar_url and hasattr(self.avatar_url, "file"):
            optimized, new_name = optimize_image(self.avatar_url)
            if optimized is not None:
                self.avatar_url.save(new_name, optimized, save=False)

        super().save(*args, **kwargs)

        # Clean up old file if it was replaced
        if old_file_path and (
            not self.avatar_url or old_file_path != self.avatar_url.path
        ):
            delete_file(old_file_path)

    def delete(self, *args, **kwargs):
        file_path = self.avatar_url.path if self.avatar_url else None
        super().delete(*args, **kwargs)
        delete_file(file_path)


class Stat(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="stats")
    value = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.label}: {self.value}"


class Education(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="education"
    )
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year = models.CharField(max_length=50)
    gpa = models.CharField(max_length=50, blank=True)
    details = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class SkillCategory(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="skills"
    )
    photo = models.FileField(upload_to="skill_photos/", blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Skill Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        old_file_path = None
        if self.pk:
            try:
                old_instance = SkillCategory.objects.get(pk=self.pk)
                if old_instance.photo:
                    old_file_path = old_instance.photo.path
            except SkillCategory.DoesNotExist:
                pass

        # Optimize the uploaded skill photo
        if self.photo and hasattr(self.photo, "file"):
            optimized, new_name = optimize_image(self.photo)
            if optimized is not None:
                self.photo.save(new_name, optimized, save=False)

        super().save(*args, **kwargs)

        if old_file_path and (
            not self.photo or old_file_path != self.photo.path
        ):
            delete_file(old_file_path)

    def delete(self, *args, **kwargs):
        file_path = self.photo.path if self.photo else None
        super().delete(*args, **kwargs)
        delete_file(file_path)


class Project(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="projects"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.CharField(max_length=500)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "order"]

    def __str__(self):
        return self.title


class Message(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Message from {self.name} - {self.created_at.strftime('%Y-%m-%d')}"


class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Chat Session {self.session_id}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
