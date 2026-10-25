import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from backend.core.models import Organization, Membership, Brand, Post, Approval
from tests.test_engines import picture, history


@pytest.fixture
def users(db):
    org = Organization.objects.create(name="SYNTHETIC TEST organization")
    result = {}
    for role in ["OWNER", "CREATOR", "REVIEWER"]:
        user = User.objects.create_user(role, password="TestPass!79452")
        Membership.objects.create(user=user, organization=org, role=role)
        c = APIClient()
        c.force_authenticate(user)
        result[role] = (user, c)
    return result


def create_post(users):
    owner = users["OWNER"][1]
    creator = users["CREATOR"][1]
    b = owner.post(
        "/api/brands/",
        {
            "name": "SYNTHETIC TEST brand",
            "colors": [{"hex": "#FF0000", "role": "PRIMARY"}],
        },
        format="json",
    )
    assert b.status_code == 201, b.data
    p = creator.post(
        "/api/posts/",
        {
            "brand": b.data["id"],
            "title": "Test post",
            "caption": "Coffee roasting story",
        },
        format="json",
    )
    assert p.status_code == 201, p.data
    return p.data["id"], b.data["id"]


@pytest.mark.django_db
def test_full_workflow_permissions_and_exports(users):
    creator = users["CREATOR"][1]
    reviewer = users["REVIEWER"][1]
    owner = users["OWNER"][1]
    pid, bid = create_post(users)
    assert creator.post("/api/brands/", {"name": "Forbidden"}).status_code == 403
    assert (
        creator.post(
            f"/api/posts/{pid}/transition/", {"decision": "SUBMIT"}
        ).status_code
        == 400
    )
    assert (
        creator.post(
            f"/api/posts/{pid}/image/",
            {"image": SimpleUploadedFile("x.png", picture(), content_type="image/png")},
        ).status_code
        == 200
    )
    r = creator.post(f"/api/posts/{pid}/analyze/")
    assert r.status_code == 200, r.data
    assert r.data["analyses"]["visual_analysis"]["score"] == 100
    assert (
        creator.post(
            f"/api/posts/{pid}/transition/", {"decision": "SUBMIT"}
        ).status_code
        == 200
    )
    assert (
        creator.patch(f"/api/posts/{pid}/", {"caption": "illegal edit"}).status_code
        == 400
    )
    assert (
        creator.post(
            f"/api/posts/{pid}/transition/", {"decision": "APPROVE", "comments": "ok"}
        ).status_code
        == 403
    )
    assert (
        reviewer.post(
            f"/api/posts/{pid}/transition/",
            {"decision": "APPROVE", "comments": "Reviewed all findings"},
        ).status_code
        == 200
    )
    assert (
        reviewer.post(f"/api/posts/{pid}/transition/", {"decision": "MARK_READY"}).data[
            "status"
        ]
        == "READY_TO_PUBLISH"
    )
    assert reviewer.get(f"/api/posts/{pid}/export/").status_code == 200
    assert reviewer.get(f"/api/posts/{pid}/export/?export=csv").status_code == 200
    assert Approval.objects.filter(post_id=pid).count() == 3
    assert [
        x["decision"] for x in reviewer.get(f"/api/posts/{pid}/").data["approvals"]
    ] == ["SUBMIT", "APPROVE", "MARK_READY"]
    assert (
        owner.patch(
            f"/api/brands/{bid}/", {"name": "Changed kit"}, format="json"
        ).status_code
        == 200
    )
    assert Post.objects.get(pk=pid).status == "DRAFT"


@pytest.mark.django_db
def test_tenant_isolation(users):
    pid, bid = create_post(users)
    org = Organization.objects.create(name="Other")
    user = User.objects.create_user("other")
    Membership.objects.create(user=user, organization=org, role="OWNER")
    c = APIClient()
    c.force_authenticate(user)
    assert c.get(f"/api/posts/{pid}/").status_code == 404
    assert c.get(f"/api/brands/{bid}/").status_code == 404
    assert (
        c.post("/api/posts/", {"brand": bid, "title": "x", "caption": "x"}).status_code
        == 400
    )
    assert not c.get("/api/posts/").data


@pytest.mark.django_db
def test_bad_uploads_and_forecast(users):
    pid, bid = create_post(users)
    c = users["CREATOR"][1]
    assert (
        c.post(
            f"/api/posts/{pid}/image/", {"image": SimpleUploadedFile("bad.png", b"bad")}
        ).status_code
        == 400
    )
    assert (
        c.post(
            "/api/forecasts/",
            {
                "brand": bid,
                "file": SimpleUploadedFile("bad.csv", b"bad"),
                "provenance": "test fixture",
            },
        ).status_code
        == 400
    )
    r = c.post(
        "/api/forecasts/",
        {
            "brand": bid,
            "file": SimpleUploadedFile("test.csv", history()),
            "provenance": "SYNTHETIC TEST DATA",
            "is_demo": "true",
        },
    )
    assert r.status_code == 201, r.data
    assert r.data["is_demo"] is True


@pytest.mark.django_db
def test_session_auth_and_csrf():
    c = APIClient(enforce_csrf_checks=True)
    assert (
        c.post(
            "/api/auth/register/",
            {"username": "new", "password": "StrongPass!9381", "organization": "New"},
        ).status_code
        == 403
    )
    token = c.get("/api/auth/csrf/").data["csrfToken"]
    r = c.post(
        "/api/auth/register/",
        {"username": "new", "password": "StrongPass!9381", "organization": "New"},
        HTTP_X_CSRFTOKEN=token,
    )
    assert r.status_code == 201, r.data
    assert User.objects.get(username="new").password != "StrongPass!9381"
    assert c.get("/api/auth/me/").status_code == 200
    token = c.get("/api/auth/csrf/").data["csrfToken"]
    assert c.post("/api/auth/logout/", HTTP_X_CSRFTOKEN=token).status_code == 200
    assert c.get("/api/posts/").status_code == 403
    token = c.get("/api/auth/csrf/").data["csrfToken"]
    assert (
        c.post(
            "/api/auth/login/",
            {"username": "new", "password": "StrongPass!9381"},
            HTTP_X_CSRFTOKEN=token,
        ).status_code
        == 200
    )


@pytest.mark.django_db
def test_request_changes_and_invalid_transition(users):
    pid, bid = create_post(users)
    c = users["CREATOR"][1]
    r = users["REVIEWER"][1]
    assert (
        r.post(f"/api/posts/{pid}/transition/", {"decision": "MARK_READY"}).status_code
        == 400
    )
    c.post(
        f"/api/posts/{pid}/image/", {"image": SimpleUploadedFile("x.png", picture())}
    )
    c.post(f"/api/posts/{pid}/analyze/")
    c.post(f"/api/posts/{pid}/transition/", {"decision": "SUBMIT"})
    assert (
        r.post(
            f"/api/posts/{pid}/transition/", {"decision": "REQUEST_CHANGES"}
        ).status_code
        == 400
    )
    assert (
        r.post(
            f"/api/posts/{pid}/transition/",
            {"decision": "REQUEST_CHANGES", "comments": "Change caption"},
        ).status_code
        == 200
    )
    assert (
        c.patch(f"/api/posts/{pid}/", {"caption": "Updated story"}).status_code == 200
    )
    assert (
        c.post(f"/api/posts/{pid}/transition/", {"decision": "SUBMIT"}).status_code
        == 400
    )
