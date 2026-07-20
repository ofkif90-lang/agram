from django.urls import path
from django.views.generic import RedirectView
from django.http import HttpResponse
from django.contrib.sitemaps import views as sitemap_views

from downloader import views
from .sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
}

def robots_txt(request):
    return HttpResponse(
        """User-agent: *
Allow: /

Sitemap: https://agram-production.up.railway.app/sitemap.xml
""",
        content_type="text/plain"
    )

# تعديل هنا: عملنا view مخصص للـ sitemap.xml
def sitemap_xml(request):
    response = sitemap_views.sitemap(request, {"sitemaps": sitemaps})
    response["Content-Type"] = "application/xml"
    # شيل الـ x-robots-tag لو بيتضاف تلقائيًا
    if "X-Robots-Tag" in response:
        del response["X-Robots-Tag"]
    return response

favicon_view = RedirectView.as_view(
    url="/static/favicon.svg",
    permanent=True
)

urlpatterns = [
    path("sitemap.xml", sitemap_xml),   # استخدمنا الـ view الجديد هنا
    path("robots.txt", robots_txt),
    path("test/", lambda request: HttpResponse("WORKING")),

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
