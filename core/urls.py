"""URLs for the tlc app."""

from django.urls import path
from django.views.generic import TemplateView

app_name = "core"  # pylint: disable=invalid-name

urlpatterns = [
    path(
        "legal/about",
        TemplateView.as_view(template_name="core/about.html"),
        name="about",
    ),
    path(
        "legal/privacy",
        TemplateView.as_view(template_name="core/privacy.html"),
        name="privacy",
    ),
    path(
        "legal/tos",
        TemplateView.as_view(template_name="core/tos.html"),
        name="tos",
    ),
    path(
        "home",
        TemplateView.as_view(template_name="core/home.html"),
        name="home",
    ),
]
