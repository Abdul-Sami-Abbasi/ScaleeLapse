from django.db import transaction
from rest_framework import serializers
from ai.brand_audit.engine import hex_hsv
from .models import *


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandColor
        fields = ["hex", "role"]

    def validate_hex(self, value):
        try:
            hex_hsv(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        return value.upper()


class BrandSerializer(serializers.ModelSerializer):
    colors = ColorSerializer(many=True, required=False)
    assets = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "description",
            "fonts",
            "rules",
            "kit_source",
            "tolerance",
            "colors",
            "assets",
        ]

    def get_assets(self, obj):
        return [
            {"id": a.id, "kind": a.kind, "url": f"/api/assets/{a.id}/"}
            for a in obj.assets.all()
        ]

    def validate_tolerance(self, v):
        if not 0.01 <= v <= 0.5:
            raise serializers.ValidationError("Use a tolerance between 0.01 and 0.5.")
        return v

    def validate_fonts(self, v):
        if not isinstance(v, list) or any(
            not isinstance(x, str) or len(x) > 100 for x in v
        ):
            raise serializers.ValidationError("Provide a list of font names.")
        return v

    @transaction.atomic
    def create(self, data):
        colors = data.pop("colors", [])
        brand = Brand.objects.create(**data)
        BrandColor.objects.bulk_create([BrandColor(brand=brand, **c) for c in colors])
        return brand

    @transaction.atomic
    def update(self, instance, data):
        colors = data.pop("colors", None)
        instance = super().update(instance, data)
        if colors is not None:
            instance.colors.all().delete()
            BrandColor.objects.bulk_create(
                [BrandColor(brand=instance, **c) for c in colors]
            )
        return instance


class PostSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    image_url = serializers.SerializerMethodField()
    analyses = serializers.SerializerMethodField()
    approvals = serializers.SerializerMethodField()
    hashtags = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "brand",
            "brand_name",
            "title",
            "caption",
            "platform",
            "status",
            "scheduled_at",
            "created_at",
            "updated_at",
            "creator",
            "image_url",
            "analyses",
            "approvals",
            "hashtags",
        ]
        read_only_fields = ["status", "creator"]

    def validate_brand(self, v):
        if v.organization_id != self.context["request"].user.membership.organization_id:
            raise serializers.ValidationError("Brand not found.")
        return v

    def validate_caption(self, v):
        if not v.strip() or len(v) > 10000:
            raise serializers.ValidationError(
                "Enter a caption between 1 and 10,000 characters."
            )
        return v

    def get_image_url(self, obj):
        return f"/api/posts/{obj.id}/image/" if hasattr(obj, "media") else None

    def get_analyses(self, obj):
        return {
            k: getattr(obj, k).result
            for k in ["visual_analysis", "ai_suggestion", "compliance_result"]
            if hasattr(obj, k)
        }

    def get_approvals(self, obj):
        return list(
            obj.approvals.order_by("created_at", "id").values(
                "id", "reviewer__username", "decision", "comments", "created_at"
            )
        )

    def get_hashtags(self, obj):
        return list(obj.post_hashtags.values_list("hashtag__name", flat=True))


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceRule
        fields = [
            "id",
            "term",
            "kind",
            "severity",
            "platform",
            "explanation",
            "source",
            "reviewed_at",
            "active",
        ]
        read_only_fields = ["reviewed_at"]

    def validate_source(self, v):
        if len(v.strip()) < 8:
            raise serializers.ValidationError(
                "Record a source URL or a clear internal-policy provenance."
            )
        return v
