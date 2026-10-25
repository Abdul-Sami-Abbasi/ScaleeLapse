import csv, hashlib, io, json, re
from pathlib import Path
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.http import FileResponse, HttpResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from PIL import Image, ImageOps
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from ai.brand_audit.engine import analyze, batch, decode_image
from ai.compliance.engine import assess
from ai.nlp.engine import recommend
from ai.forecasting.engine import forecast
from .models import *
from .serializers import BrandSerializer, PostSerializer, RuleSerializer


def require_role(user, *roles):
    if user.membership.role not in roles:
        raise PermissionDenied("Your role cannot perform this action.")


def log(user, action, obj):
    AuditLog.objects.create(
        organization=user.membership.organization,
        actor=user,
        action=action,
        object_id=str(obj.pk),
    )


def user_data(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.membership.role,
        "organization": user.membership.organization.name,
        "is_demo": user.membership.organization.is_demo,
    }


def password_check(value):
    try:
        validate_password(value)
    except DjangoValidationError as e:
        raise ValidationError({"password": e.messages})


@api_view(["GET"])
@permission_classes([AllowAny])
def csrf(request):
    return Response({"csrfToken": get_token(request)})


@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_protect
def register(request):
    username = str(request.data.get("username", "")).strip()
    password = str(request.data.get("password", ""))
    org = str(request.data.get("organization", "")).strip()
    if not re.fullmatch(r"[\w.@+-]{3,150}", username):
        raise ValidationError(
            "Username must contain 3 to 150 letters, numbers or . @ + - _."
        )
    if not org or len(org) > 120:
        raise ValidationError("Enter an organization name up to 120 characters.")
    password_check(password)
    if User.objects.filter(username=username).exists():
        raise ValidationError("Username is already registered.")
    with transaction.atomic():
        user = User.objects.create_user(
            username=username, password=password, email=request.data.get("email", "")
        )
        organization = Organization.objects.create(name=org)
        Membership.objects.create(user=user, organization=organization, role="OWNER")
        log(user, "REGISTER", user)
    login(request, user)
    return Response(user_data(user), status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_protect
def sign_in(request):
    user = authenticate(
        request,
        username=request.data.get("username"),
        password=request.data.get("password"),
    )
    if user is None or not hasattr(user, "membership"):
        return Response({"detail": "Invalid username or password."}, status=400)
    login(request, user)
    return Response(user_data(user))


@api_view(["POST"])
def sign_out(request):
    logout(request)
    return Response({"detail": "Logged out."})


@api_view(["GET", "PATCH"])
def me(request):
    if request.method == "PATCH":
        if "email" in request.data:
            request.user.email = request.data["email"]
        if request.data.get("password"):
            password_check(request.data["password"])
            request.user.set_password(request.data["password"])
        request.user.save()
        if request.data.get("password"):
            update_session_auth_hash(request, request.user)
    return Response(user_data(request.user))


@api_view(["GET", "POST", "PATCH"])
def team(request):
    org = request.user.membership.organization
    if request.method in ["POST", "PATCH"]:
        require_role(request.user, "OWNER", "ADMIN")
        role = request.data.get("role", "CREATOR")
        if role not in ["ADMIN", "CREATOR", "REVIEWER"]:
            raise ValidationError("Role must be ADMIN, CREATOR or REVIEWER.")
        if request.user.membership.role == "ADMIN" and role == "ADMIN":
            raise PermissionDenied("Only owners can appoint administrators.")
        if request.method == "POST":
            username = str(request.data.get("username", "")).strip()
            password = str(request.data.get("password", ""))
            if (
                not re.fullmatch(r"[\w.@+-]{3,150}", username)
                or User.objects.filter(username=username).exists()
            ):
                raise ValidationError("Choose an unused username, 3 to 150 characters.")
            password_check(password)
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password)
                Membership.objects.create(user=user, organization=org, role=role)
                log(request.user, "TEAM_CREATE", user)
        else:
            member = Membership.objects.filter(
                organization=org, user_id=request.data.get("id")
            ).first()
            if not member:
                raise ValidationError("Team member not found.")
            if member.role == "OWNER" or member.user == request.user:
                raise PermissionDenied("Cannot change owner or your own role.")
            if request.user.membership.role == "ADMIN" and member.role == "ADMIN":
                raise PermissionDenied("Only owners can edit administrators.")
            member.role = role
            member.save()
            log(request.user, "TEAM_ROLE", member.user)
    return Response(
        [
            user_data(m.user)
            for m in Membership.objects.filter(organization=org).select_related(
                "user", "organization"
            )
        ]
    )


def safe_upload(upload):
    if not upload:
        raise ValidationError("Select an image.")
    if upload.size > 10 * 1024 * 1024:
        raise ValidationError("Image exceeds 10 MB.")
    data = upload.read()
    try:
        pixels = decode_image(data)
    except ValueError as e:
        raise ValidationError(str(e))
    # Preserve image resolution while stripping metadata and original filenames.
    with Image.open(io.BytesIO(data)) as original:
        original = ImageOps.exif_transpose(original).convert("RGBA")
        background = Image.new("RGBA", original.size, "white")
        background.alpha_composite(original)
        buffer = io.BytesIO()
        background.convert("RGB").save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name="image.png"), hashlib.sha256(
        data
    ).hexdigest()


class BrandViewSet(viewsets.ModelViewSet):
    serializer_class = BrandSerializer

    def get_queryset(self):
        return Brand.objects.filter(
            organization=self.request.user.membership.organization
        ).prefetch_related("colors", "assets")

    def perform_create(self, serializer):
        require_role(self.request.user, "OWNER", "ADMIN")
        brand = serializer.save(organization=self.request.user.membership.organization)
        log(self.request.user, "BRAND_CREATE", brand)

    def perform_update(self, serializer):
        require_role(self.request.user, "OWNER", "ADMIN")
        brand = serializer.save()
        log(self.request.user, "BRAND_EDIT", brand)
        # A changed kit invalidates prior approval/analysis.
        for post in brand.posts.all():
            invalidate(post)

    def perform_destroy(self, instance):
        require_role(self.request.user, "OWNER", "ADMIN")
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError("Delete or reassign this brand’s posts first.")

    @action(detail=True, methods=["post"])
    def logo(self, request, pk=None):
        require_role(request.user, "OWNER", "ADMIN")
        brand = self.get_object()
        file, _ = safe_upload(request.FILES.get("image"))
        asset = BrandAsset.objects.create(brand=brand, file=file)
        log(request.user, "LOGO_UPLOAD", asset)
        return Response(self.get_serializer(brand).data)

    @action(detail=True, methods=["post"])
    def batch(self, request, pk=None):
        brand = self.get_object()
        files = request.FILES.getlist("images")
        if not files or len(files) > 20:
            raise ValidationError("Upload between 1 and 20 images.")
        return Response(
            batch(
                [(f.name, f.read(10 * 1024 * 1024 + 1)) for f in files],
                list(brand.colors.values("hex", "role")),
            )
        )


def invalidate(post):
    VisualAnalysis.objects.filter(post=post).delete()
    AISuggestion.objects.filter(post=post).delete()
    ComplianceResult.objects.filter(post=post).delete()
    PostHashtag.objects.filter(post=post).delete()
    post.status = "DRAFT"
    post.save()


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(
            organization=self.request.user.membership.organization
        ).select_related("brand", "creator")

    def editable(self, post):
        require_role(self.request.user, "OWNER", "ADMIN", "CREATOR")
        if (
            self.request.user.membership.role == "CREATOR"
            and post.creator_id != self.request.user.id
        ):
            raise PermissionDenied("You can only edit your own posts.")
        if post.status in [
            "ANALYZING",
            "READY_FOR_REVIEW",
            "APPROVED",
            "READY_TO_PUBLISH",
        ]:
            raise ValidationError("Return this post to draft before editing.")

    def perform_create(self, serializer):
        require_role(self.request.user, "OWNER", "ADMIN", "CREATOR")
        post = serializer.save(
            organization=self.request.user.membership.organization,
            creator=self.request.user,
        )
        log(self.request.user, "POST_CREATE", post)

    def perform_update(self, serializer):
        self.editable(serializer.instance)
        post = serializer.save()
        invalidate(post)
        log(self.request.user, "POST_EDIT", post)

    def perform_destroy(self, instance):
        self.editable(instance)
        log(self.request.user, "POST_DELETE", instance)
        instance.delete()

    @action(detail=True, methods=["get", "post"])
    def image(self, request, pk=None):
        post = self.get_object()
        if request.method == "GET":
            if not hasattr(post, "media"):
                raise ValidationError("No image uploaded.")
            return FileResponse(post.media.file.open("rb"), content_type="image/png")
        self.editable(post)
        file, digest = safe_upload(request.FILES.get("image"))
        old = Media.objects.filter(post=post).first()
        if old:
            old.file.delete(save=False)
            old.delete()
        Media.objects.create(post=post, file=file, sha256=digest)
        invalidate(post)
        return Response(self.get_serializer(post).data)

    @action(detail=True, methods=["post"])
    def analyze(self, request, pk=None):
        post = self.get_object()
        self.editable(post)
        if not hasattr(post, "media"):
            raise ValidationError("Upload an image before analysis.")
        with transaction.atomic():
            post = Post.objects.select_for_update().get(pk=post.pk)
            self.editable(post)
            post.status = "ANALYZING"
            post.save()
            try:
                with post.media.file.open("rb") as f:
                    visual = analyze(
                        f.read(),
                        list(post.brand.colors.values("hex", "role")),
                        post.brand.tolerance,
                    )
                duplicates = (
                    Media.objects.filter(
                        post__organization=post.organization,
                        post__brand=post.brand,
                        sha256=post.media.sha256,
                    )
                    .exclude(post=post)
                    .count()
                )
                visual["design_fatigue"] = {
                    "exact_duplicate_posts": duplicates,
                    "status": "REVIEW_REUSE" if duplicates else "NO_EXACT_DUPLICATES",
                    "limitation": "Exact-image reuse heuristic, not a validated fatigue model.",
                }
                suggestions = recommend(
                    post.caption, settings.BASE_DIR / "models/hashtag_transformer"
                )
                rules = list(
                    ComplianceRule.objects.filter(
                        organization=post.organization, active=True
                    )
                    .filter(Q(platform=post.platform) | Q(platform="ALL"))
                    .values()
                )
                safe = []
                flagged = []
                for tag in suggestions["hashtags"]:
                    (flagged if assess("", [tag], rules)["findings"] else safe).append(
                        tag
                    )
                suggestions["hashtags"] = safe
                suggestions["withheld_hashtags"] = flagged
                suggestions["editorial_keywords"] = [
                    tag
                    for tag in suggestions.get("editorial_keywords", [])
                    if not assess("", [tag], rules)["findings"]
                ]
                supplied = re.findall(r"#\w+", post.caption)
                risk = assess(post.caption, supplied + safe, rules)
                VisualAnalysis.objects.update_or_create(
                    post=post, defaults={"result": visual}
                )
                AISuggestion.objects.update_or_create(
                    post=post, defaults={"result": suggestions}
                )
                ComplianceResult.objects.update_or_create(
                    post=post, defaults={"result": risk}
                )
                post.post_hashtags.all().delete()
                for tag in dict.fromkeys(supplied + safe):
                    h, _ = Hashtag.objects.get_or_create(name=tag.lower())
                    PostHashtag.objects.create(post=post, hashtag=h)
            except (ValueError, ImportError, OSError) as e:
                raise ValidationError(str(e))
            post.status = "DRAFT"
            post.save()
            log(request.user, "ANALYZE", post)
        return Response(self.get_serializer(post).data)

    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        with transaction.atomic():
            post = self.get_queryset().select_for_update().get(pk=self.get_object().pk)
            decision = request.data.get("decision")
            comments = str(request.data.get("comments", ""))[:3000]
            target = {
                "SUBMIT": "READY_FOR_REVIEW",
                "APPROVE": "APPROVED",
                "REQUEST_CHANGES": "CHANGES_REQUIRED",
                "MARK_READY": "READY_TO_PUBLISH",
                "REOPEN": "DRAFT",
            }.get(decision)
            allowed = {
                "SUBMIT": ["DRAFT", "CHANGES_REQUIRED"],
                "APPROVE": ["READY_FOR_REVIEW"],
                "REQUEST_CHANGES": ["READY_FOR_REVIEW"],
                "MARK_READY": ["APPROVED"],
                "REOPEN": [
                    "READY_FOR_REVIEW",
                    "APPROVED",
                    "READY_TO_PUBLISH",
                    "CHANGES_REQUIRED",
                ],
            }
            if decision not in allowed or post.status not in allowed[decision]:
                raise ValidationError("Invalid workflow transition.")
            if decision in ["APPROVE", "REQUEST_CHANGES", "MARK_READY"]:
                require_role(request.user, "OWNER", "ADMIN", "REVIEWER")
                if post.creator_id == request.user.id:
                    raise PermissionDenied(
                        "A different team member must review and approve this post."
                    )
            else:
                require_role(request.user, "OWNER", "ADMIN", "CREATOR")
                if (
                    request.user.membership.role == "CREATOR"
                    and post.creator_id != request.user.id
                ):
                    raise PermissionDenied("You can only submit your own posts.")
            if decision == "SUBMIT" and not all(
                hasattr(post, x)
                for x in ["visual_analysis", "ai_suggestion", "compliance_result"]
            ):
                raise ValidationError("Analyze this post before submitting.")
            if decision == "REQUEST_CHANGES" and not comments.strip():
                raise ValidationError("Explain the changes required.")
            if decision == "APPROVE" and not comments.strip():
                raise ValidationError(
                    "Record your review of the analysis warnings and Brand Kit."
                )
            if decision == "REOPEN":
                invalidate(post)
            post.status = target
            post.save()
            Approval.objects.create(
                post=post, reviewer=request.user, decision=decision, comments=comments
            )
            log(request.user, decision, post)
        return Response(self.get_serializer(post).data)

    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        post = self.get_object()
        data = self.get_serializer(post).data
        if request.query_params.get("export") == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["hex", "percentage", "matched", "approved_color"])
            for p in data["analyses"].get("visual_analysis", {}).get("palette", []):
                writer.writerow(
                    [p["hex"], p["percentage"], p["matched"], p["approved_color"]]
                )
            response = HttpResponse(output.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="post-{post.id}-palette.csv"'
            )
            return response
        return Response(data)


class RuleViewSet(viewsets.ModelViewSet):
    serializer_class = RuleSerializer

    def get_queryset(self):
        return ComplianceRule.objects.filter(
            organization=self.request.user.membership.organization
        )

    def perform_create(self, serializer):
        require_role(self.request.user, "OWNER", "ADMIN")
        with transaction.atomic():
            rule = serializer.save(
                organization=self.request.user.membership.organization
            )
            log(self.request.user, "RULE_CREATE", rule)
            self.invalidate_policy()

    def invalidate_policy(self):
        for post in Post.objects.filter(
            organization=self.request.user.membership.organization
        ):
            invalidate(post)

    def perform_update(self, serializer):
        require_role(self.request.user, "OWNER", "ADMIN")
        with transaction.atomic():
            rule = serializer.save()
            log(self.request.user, "RULE_EDIT", rule)
            self.invalidate_policy()

    def perform_destroy(self, instance):
        require_role(self.request.user, "OWNER", "ADMIN")
        with transaction.atomic():
            log(self.request.user, "RULE_DELETE", instance)
            instance.delete()
            self.invalidate_policy()

    @action(detail=False, methods=["post"])
    def import_rules(self, request):
        require_role(request.user, "OWNER", "ADMIN")
        if not isinstance(request.data, list) or len(request.data) > 500:
            raise ValidationError("Supply a JSON array of at most 500 sourced rules.")
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            serializer.save(organization=request.user.membership.organization)
            self.invalidate_policy()
        return Response(serializer.data, status=201)


@api_view(["GET"])
def asset(request, pk):
    a = BrandAsset.objects.filter(
        pk=pk, brand__organization=request.user.membership.organization
    ).first()
    if not a:
        return Response(status=404)
    return FileResponse(a.file.open("rb"), content_type="image/png")


@api_view(["GET"])
def dashboard(request):
    posts = Post.objects.filter(organization=request.user.membership.organization)
    return Response(
        {
            "posts": posts.count(),
            "brands": Brand.objects.filter(
                organization=request.user.membership.organization
            ).count(),
            "awaiting_review": posts.filter(status="READY_FOR_REVIEW").count(),
            "ready_to_publish": posts.filter(status="READY_TO_PUBLISH").count(),
            "recent": PostSerializer(
                posts[:5], many=True, context={"request": request}
            ).data,
            "activity": list(
                AuditLog.objects.filter(
                    organization=request.user.membership.organization
                ).values("action", "object_id", "created_at", "actor__username")[:15]
            ),
        }
    )


@api_view(["GET", "POST"])
def forecasts(request):
    org = request.user.membership.organization
    if request.method == "GET":
        return Response(
            [
                {
                    "id": f.id,
                    "brand": f.history.brand.name,
                    "is_demo": f.history.is_demo,
                    "provenance": f.history.provenance,
                    "result": f.result,
                    "created_at": f.created_at,
                }
                for f in Forecast.objects.filter(history__organization=org)
                .select_related("history__brand")
                .order_by("-created_at")[:30]
            ]
        )
    require_role(request.user, "OWNER", "ADMIN", "CREATOR")
    brand = Brand.objects.filter(pk=request.data.get("brand"), organization=org).first()
    if not brand:
        raise ValidationError("Select a brand.")
    file = request.FILES.get("file")
    if not file or file.size > 10 * 1024 * 1024:
        raise ValidationError("Upload a CSV file up to 10 MB.")
    provenance = str(request.data.get("provenance", "")).strip()
    if not provenance:
        raise ValidationError(
            "Describe the dataset source and whether it is synthetic."
        )
    data = file.read()
    metric = request.data.get("metric", "likes")
    account = request.data.get("account_id") or None
    try:
        result = forecast(
            data,
            metric,
            account,
            request.data.get("model", "arima"),
            int(request.data.get("horizon", 7)),
        )
    except (ValueError, TypeError) as e:
        raise ValidationError(str(e))
    with transaction.atomic():
        history = EngagementHistory.objects.create(
            organization=org,
            brand=brand,
            metric=metric,
            source_name=Path(file.name).name,
            source_hash=hashlib.sha256(data).hexdigest(),
            provenance=provenance,
            is_demo=org.is_demo
            or str(request.data.get("is_demo", "false")).lower() == "true",
            account_id=account or "",
            rows=result["history"],
        )
        obj = Forecast.objects.create(history=history, result=result)
        log(request.user, "FORECAST", obj)
    return Response(
        {"id": obj.id, "result": result, "is_demo": history.is_demo}, status=201
    )
