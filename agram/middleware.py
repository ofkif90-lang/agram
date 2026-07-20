import time, collections, ipaddress
from urllib.parse import urlparse

ALLOWED_HOSTS_LIST = {
    'instagram.com', 'www.instagram.com', 'cdninstagram.com',
    'fbcdn.net', 'scontent', 'dl.snapcdn.app', 'i.snapcdn.app',
    'story-viewer.co', 'dl.story-viewer.co',
}

RATE_LIMIT = collections.defaultdict(list)
RATE_WINDOW = 60
RATE_MAX = 30


def _is_allowed_host(url):
    try:
        host = (urlparse(url).hostname or '').lower()
        if not host:
            return False
        for allowed in ALLOWED_HOSTS_LIST:
            if host == allowed or host.endswith('.' + allowed):
                return True
        if 'cdninstagram' in host or 'fbcdn' in host or 'scontent' in host or 'story-viewer' in host:
            return True
        return False
    except Exception:
        return False


def _is_private_ip(host):
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except Exception:
        return False


def rate_limit_check(ip):
    now = time.time()
    w = RATE_LIMIT[ip]
    w[:] = [t for t in w if now - t < RATE_WINDOW]
    if len(w) >= RATE_MAX:
        return False
    w.append(now)
    return True


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        if not response.get('Content-Security-Policy'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' https: data: blob:; "
                "media-src 'self' https: blob:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
            )
        return response

# agram/middleware.py

class RobotsTagMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # لو الطلب خاص بالـ sitemap.xml
        if request.path.endswith("sitemap.xml"):
            response["X-Robots-Tag"] = "all"  # غيّر القيمة
        return response
