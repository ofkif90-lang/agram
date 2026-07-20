import re, requests
from urllib.parse import urlparse
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from . import ig_client
from agram.middleware import rate_limit_check, _is_allowed_host, _is_private_ip


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def index(request):
    return render(request, "index.html", {"api_status": ig_client.API_STATUS})

def guide(request):
    return render(request, "guide.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def privacy(request):
    return render(request, "privacy.html")

def terms(request):
    return render(request, "terms.html")

def faq(request):
    return render(request, "faq.html")


def api_search(request):
    ip = _client_ip(request)
    if not rate_limit_check(ip):
        return JsonResponse({"ok": False, "error": "طلبات كثيرة. حاول بعد دقيقة."}, status=429)
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"ok": False, "error": "اكتب اسم مستخدم أو رابط."}, status=400)
    try:
        result = ig_client.search(q)
        if not result:
            return JsonResponse({"ok": False, "error": "لا توجد نتائج. جرّب رابطاً أو اسم مستخدم آخر."})
        return JsonResponse({"ok": True, "data": result})
    except Exception as e:
        return JsonResponse({"ok": False, "error": "حدث خطأ. حاول مرة أخرى."}, status=500)


def api_content(request):
    ip = _client_ip(request)
    if not rate_limit_check(ip):
        return JsonResponse({"ok": False, "error": "طلبات كثيرة. حاول بعد دقيقة."}, status=429)
    username = request.GET.get("username", "").strip()
    if not username:
        return JsonResponse({"ok": False, "error": "username required"}, status=400)
    tab = request.GET.get("tab", "posts")
    if tab not in ("posts", "reels", "stories", "highlights"):
        tab = "posts"
    try:
        media = ig_client.fetch_tab(username, tab)
        if not media:
            return JsonResponse({"ok": False, "error": "لا يوجد محتوى متاح في هذا القسم حالياً."})
        return JsonResponse({"ok": True, "data": {"media": media, "api_used": f"{ig_client.LAST_USED_API['name']} (#{ig_client.LAST_USED_API['rank']})" if ig_client.LAST_USED_API["name"] else None}})
    except Exception:
        return JsonResponse({"ok": False, "error": "حدث خطأ. حاول مرة أخرى."}, status=500)


def api_status(request):
    return JsonResponse({"ok": True, "data": ig_client.API_STATUS})


def download_proxy(request):
    ip = _client_ip(request)
    if not rate_limit_check(ip):
        return JsonResponse({"ok": False, "error": "طلبات كثيرة. حاول بعد دقيقة."}, status=429)
    url = request.GET.get("url", "").strip()
    if not url or not url.startswith("https://"):
        return JsonResponse({"ok": False, "error": "invalid url"}, status=400)
    if not _is_allowed_host(url):
        return JsonResponse({"ok": False, "error": "host not allowed"}, status=403)
    try:
        host = urlparse(url).hostname or ""
        if _is_private_ip(host):
            return JsonResponse({"ok": False, "error": "blocked"}, status=403)
    except Exception:
        return JsonResponse({"ok": False, "error": "invalid url"}, status=400)
    view = request.GET.get("view", "0") == "1"
    tab = request.GET.get("tab", "media")
    if not re.match(r"^[a-z]{1,20}$", tab):
        tab = "media"
    try:
        r = requests.get(url, stream=True, timeout=60, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
        if r.status_code != 200:
            return JsonResponse({"ok": False, "error": "upstream error"}, status=502)
        ct = r.headers.get("Content-Type", "application/octet-stream").lower()
        is_video = "video" in ct
        is_image = "image" in ct
        first_chunk = b""
        if not is_video and not is_image:
            first_chunk = next(r.iter_content(chunk_size=32), b"")
            if b"ftyp" in first_chunk:
                is_video = True
                ct = "video/mp4"
            elif first_chunk[:2] == b"\xff\xd8":
                is_image = True
                ct = "image/jpeg"
            elif first_chunk[:4] == b"\x89PNG":
                is_image = True
                ct = "image/png"
        ext = "mp4" if is_video else ("jpg" if is_image else "bin")
        filename = f"agram_{tab}.{ext}"
        resp = HttpResponse(content_type=ct)
        resp["Content-Disposition"] = "inline" if view else f'attachment; filename="{filename}"'
        cl = r.headers.get("Content-Length")
        if cl:
            resp["Content-Length"] = cl
        if first_chunk:
            resp.write(first_chunk)
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                resp.write(chunk)
        return resp
    except Exception:
        return JsonResponse({"ok": False, "error": "download failed"}, status=502)
