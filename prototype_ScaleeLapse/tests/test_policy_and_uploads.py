import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from backend.core.models import Post
from tests.test_api import users, create_post
from tests.test_engines import picture


@pytest.mark.django_db
def test_rule_changes_invalidate_approved_evidence(users):
    pid, bid = create_post(users)
    creator = users["CREATOR"][1]
    owner = users["OWNER"][1]
    creator.post(
        f"/api/posts/{pid}/image/", {"image": SimpleUploadedFile("test.png", picture())}
    )
    creator.post(f"/api/posts/{pid}/analyze/")
    assert hasattr(Post.objects.get(pk=pid), "compliance_result")
    r = owner.post(
        "/api/rules/",
        {
            "term": "design",
            "kind": "HASHTAG",
            "severity": "MEDIUM",
            "platform": "ALL",
            "explanation": "Synthetic unit test policy",
            "source": "Synthetic unit-test provenance",
        },
        format="json",
    )
    assert r.status_code == 201, r.data
    assert not hasattr(Post.objects.get(pk=pid), "compliance_result")
    assert (
        creator.post(
            f"/api/posts/{pid}/transition/", {"decision": "SUBMIT"}
        ).status_code
        == 400
    )


@pytest.mark.django_db
def test_source_required_and_cross_tenant_media(users):
    c = users["OWNER"][1]
    assert (
        c.post(
            "/api/rules/",
            {
                "term": "test",
                "kind": "TEXT",
                "severity": "HIGH",
                "explanation": "Test",
                "source": "",
            },
            format="json",
        ).status_code
        == 400
    )
    pid, bid = create_post(users)
    assert (
        users["REVIEWER"][1]
        .post(
            f"/api/posts/{pid}/image/",
            {"image": SimpleUploadedFile("x.png", picture())},
        )
        .status_code
        == 403
    )
