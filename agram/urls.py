from django.urls import path
from django.views.generic import RedirectView
from django.http import HttpResponse
from downloader import views

from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
}



favicon_view = RedirectView.as_view(url="/static/favicon.svg", permanent=True)

urlpatterns = [

path(
    "sitemap.xml",
    sitemap,
    {"sitemaps": sitemaps},
    name="django.contrib.sitemaps.views.sitemap",
),


    
    path("", views.index, name="index"),
    path("guide", views.guide, name="guide"),
    path("about", views.about, name="about"),
    path("contact", views.contact, name="contact"),
    path("privacy", views.privacy, name="privacy"),
    path("terms", views.terms, name="terms"),
    path("faq", views.faq, name="faq"),
    path("api/search", views.api_search, name="api_search"),
    path("api/content", views.api_content, name="api_content"),
    path("api/status", views.api_status, name="api_status"),
    path("download", views.download_proxy, name="download"),
    path("favicon.ico", favicon_view),

    path(
    "google55e2cfdb79c0b019.html",
    lambda request: HttpResponse(
        "google-site-verification: google55e2cfdb79c0b019.html",
        content_type="text/html",
    ),
),




                            ]

from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
}