from django.db import models


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
