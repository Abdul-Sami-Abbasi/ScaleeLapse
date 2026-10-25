from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.core import views

router = DefaultRouter()
router.register("brands", views.BrandViewSet, basename="brand")
router.register("posts", views.PostViewSet, basename="post")
router.register("rules", views.RuleViewSet, basename="rule")
urlpatterns = [
    path("api/", include(router.urls)),
    path("api/auth/csrf/", views.csrf),
    path("api/auth/register/", views.register),
    path("api/auth/login/", views.sign_in),
    path("api/auth/logout/", views.sign_out),
    path("api/auth/me/", views.me),
    path("api/team/", views.team),
    path("api/dashboard/", views.dashboard),
    path("api/forecasts/", views.forecasts),
    path("api/assets/<int:pk>/", views.asset),
]
