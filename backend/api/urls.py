from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path, reverse_lazy
from django.views.generic.base import RedirectView
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .graphs.views import (
    CirculantGraphViewSet,
    CirculantGraphDataViewSet,
    CompleteGraphViewSet,
    CompleteGraphDataViewSet,
)
from .simulations.views import (
    InstanceViewSet,
    ParametersViewSet,
)
from .users.views import UserCreateViewSet, UserViewSet


class OptionalSlashRouter(DefaultRouter):
    """Extend the `DefaultRouter` by making trailing_slash (`/`) optional for all URLs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = "/?"


router = OptionalSlashRouter()
router.register(r"graphs/circulant", CirculantGraphViewSet)
router.register(r"graphs/circulant", CirculantGraphDataViewSet)
router.register(r"graphs/complete", CompleteGraphViewSet)
router.register(r"graphs/complete", CompleteGraphDataViewSet)

router.register(r"simulations/instances", InstanceViewSet)
router.register(r"simulations/parameters", ParametersViewSet)

router.register(r"users", UserViewSet)
router.register(r"register", UserCreateViewSet)

urlpatterns = [
    re_path("admin/", admin.site.urls),
    re_path("api/v1/", include(router.urls)),
    re_path("api-token-auth/", views.obtain_auth_token),
    re_path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)),
    re_path(
        "api/v1", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
