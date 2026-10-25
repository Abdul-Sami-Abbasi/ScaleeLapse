"""Opt-in synthetic organization; never used for academic evaluation."""

import io, os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from backend.core.models import (
    Organization,
    Membership,
    Brand,
    BrandColor,
    Post,
    Media,
    VisualAnalysis,
    AISuggestion,
    ComplianceResult,
    Approval,
    BrandAsset,
)
from ai.brand_audit.engine import analyze
from ai.nlp.engine import recommend
from ai.compliance.engine import assess
import hashlib


class Command(BaseCommand):
    help = "Create clearly labeled synthetic demo workspace. Requires DEMO_PASSWORD environment variable."

    @transaction.atomic
    def handle(self, *args, **options):
        password = os.getenv("DEMO_PASSWORD")
        if not password or len(password) < 10:
            raise CommandError("Set DEMO_PASSWORD to at least 10 characters.")
        if User.objects.filter(username="demo.owner").exists():
            self.stdout.write("Demo already exists; no changes.")
            return
        org = Organization.objects.create(name="Form & Field · DEMO", is_demo=True)
        users = {}
        for role in ["owner", "creator", "reviewer"]:
            u = User.objects.create_user(
                "demo." + role, password=password, email=f"{role}@example.invalid"
            )
            Membership.objects.create(user=u, organization=org, role=role.upper())
            users[role] = u
        brand = Brand.objects.create(
            organization=org,
            name="Form & Field",
            description="SYNTHETIC DEMO BRAND · Everyday objects, thoughtfully made.",
            fonts=["Georgia", "DM Sans"],
            kit_source="SYNTHETIC DEMO DATA — created for application testing",
            rules="Use a calm, welcoming voice. Reviewer checks typography manually.",
        )
        colors = [
            {"hex": "#184F40", "role": "PRIMARY"},
            {"hex": "#D2AC88", "role": "SECONDARY"},
            {"hex": "#F0EBDF", "role": "BACKGROUND"},
        ]
        for c in colors:
            BrandColor.objects.create(brand=brand, **c)
        titles = [
            "A slower kind of morning",
            "Made for everyday moments",
            "Room for something new",
        ]
        for idx, title in enumerate(titles):
            im = Image.new("RGB", (800, 900), ["#D2AC88", "#184F40", "#F0EBDF"][idx])
            d = ImageDraw.Draw(im)
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 72)
                small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
            except OSError:
                font = ImageFont.load_default(size=60)
                small = ImageFont.load_default(size=18)
            ink = "#F0EBDF" if idx < 2 else "#184F40"
            d.text((60, 80), "FORM & FIELD", fill=ink, font=small)
            d.text(
                (60, 280),
                [
                    "a slower\nkind of\nmorning.",
                    "made for\neveryday\nmoments.",
                    "room for\nsomething\nnew.",
                ][idx],
                fill=ink,
                font=font,
                spacing=12,
            )
            d.text((60, 790), "SYNTHETIC DEMO DATA", fill=ink, font=small)
            b = io.BytesIO()
            im.save(b, "PNG")
            data = b.getvalue()
            p = Post.objects.create(
                organization=org,
                brand=brand,
                creator=users["creator"],
                title=title,
                caption=f"{title}. Thoughtfully made objects for your home. Share your favorite morning ritual. #thoughtfuldesign",
                status=["READY_FOR_REVIEW", "DRAFT", "READY_TO_PUBLISH"][idx],
            )
            Media.objects.create(
                post=p,
                file=ContentFile(data, name="demo.png"),
                sha256=hashlib.sha256(data).hexdigest(),
            )
            if idx != 1:
                v = analyze(data, colors)
                v["design_fatigue"] = {"exact_duplicate_posts": 0}
                VisualAnalysis.objects.create(post=p, result=v)
                a = recommend(p.caption)
                AISuggestion.objects.create(post=p, result=a)
                ComplianceResult.objects.create(
                    post=p, result=assess(p.caption, a["hashtags"], [])
                )
            if idx == 2:
                Approval.objects.create(
                    post=p,
                    reviewer=users["reviewer"],
                    decision="APPROVE",
                    comments="SYNTHETIC DEMO review: palette, text, and unavailable model warnings reviewed.",
                )
                Approval.objects.create(
                    post=p,
                    reviewer=users["reviewer"],
                    decision="MARK_READY",
                    comments="Manual publishing only.",
                )
        self.stdout.write(
            self.style.SUCCESS(
                "SYNTHETIC DEMO DATA created. Users: demo.owner, demo.creator, demo.reviewer. Password comes from DEMO_PASSWORD."
            )
        )
