import uuid
from django.db import models
from django.contrib.auth.models import User


def upload_path(instance, filename):
    return f"uploads/{uuid.uuid4().hex}.png"


class Organization(models.Model):
    name = models.CharField(max_length=120)
    is_demo = models.BooleanField(default=False)


class Membership(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="membership"
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=12,
        choices=[(x, x) for x in ["OWNER", "ADMIN", "CREATOR", "REVIEWER"]],
        default="CREATOR",
    )


class Brand(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    fonts = models.JSONField(default=list)
    rules = models.TextField(blank=True)
    kit_source = models.CharField(max_length=500, blank=True)
    tolerance = models.FloatField(default=0.15)
    created_at = models.DateTimeField(auto_now_add=True)


class BrandColor(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="colors")
    hex = models.CharField(max_length=7)
    role = models.CharField(
        max_length=12, choices=[(x, x) for x in ["PRIMARY", "SECONDARY", "BACKGROUND"]]
    )


class BrandAsset(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="assets")
    file = models.FileField(upload_to=upload_path)
    kind = models.CharField(max_length=20, default="LOGO")


class Post(models.Model):
    STATES = [
        "DRAFT",
        "ANALYZING",
        "READY_FOR_REVIEW",
        "CHANGES_REQUIRED",
        "APPROVED",
        "READY_TO_PUBLISH",
    ]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="posts")
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=160)
    caption = models.TextField()
    platform = models.CharField(
        max_length=12,
        choices=[("INSTAGRAM", "Instagram"), ("FACEBOOK", "Facebook")],
        default="INSTAGRAM",
    )
    status = models.CharField(
        max_length=24, choices=[(x, x) for x in STATES], default="DRAFT", db_index=True
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]


class Media(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to=upload_path)
    sha256 = models.CharField(max_length=64, db_index=True)


class VisualAnalysis(models.Model):
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="visual_analysis"
    )
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now=True)


class AISuggestion(models.Model):
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="ai_suggestion"
    )
    result = models.JSONField()


class Hashtag(models.Model):
    name = models.CharField(max_length=150, unique=True)


class PostHashtag(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_hashtags"
    )
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "hashtag"], name="unique_post_hashtag"
            )
        ]


class ComplianceRule(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    term = models.CharField(max_length=150)
    kind = models.CharField(
        max_length=10, choices=[("HASHTAG", "Hashtag"), ("TEXT", "Text")]
    )
    severity = models.CharField(
        max_length=6, choices=[(x, x) for x in ["LOW", "MEDIUM", "HIGH"]]
    )
    platform = models.CharField(
        max_length=12,
        choices=[(x, x) for x in ["ALL", "INSTAGRAM", "FACEBOOK"]],
        default="ALL",
    )
    explanation = models.TextField()
    source = models.CharField(max_length=500)
    reviewed_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)


class ComplianceResult(models.Model):
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="compliance_result"
    )
    result = models.JSONField()


class EngagementHistory(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    metric = models.CharField(max_length=30)
    source_name = models.CharField(max_length=200)
    source_hash = models.CharField(max_length=64)
    provenance = models.CharField(max_length=500)
    is_demo = models.BooleanField(default=False)
    account_id = models.CharField(max_length=80, blank=True)
    rows = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class Forecast(models.Model):
    history = models.ForeignKey(
        EngagementHistory, on_delete=models.CASCADE, related_name="forecasts"
    )
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class Approval(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="approvals")
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT)
    decision = models.CharField(max_length=24)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=60)
    object_id = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
