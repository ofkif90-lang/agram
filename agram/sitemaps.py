from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return [
            "index",
            "guide",
            "about",
            "contact",
            "privacy",
            "terms",
            "faq",
        ]

    def location(self, item):
        return reverse(item)