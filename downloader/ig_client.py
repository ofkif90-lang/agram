import re, requests
from urllib.parse import urlparse

RAPIDAPI_KEY = "184d0c7eb5msh64ee07976709c06p1b2173jsnb7f2decf926c"
TIMEOUT = 20

API_STATUS = [
    {"rank": 1, "name": "instagram120", "host": "instagram120.p.rapidapi.com",
     "features": "بروفايل، منشورات، ريلز، ستوري، هايلايت، تحميل بالكود", "status": "active"},
    {"rank": 2, "name": "instagram362", "host": "instagram362.p.rapidapi.com",
     "features": "بروفايل، منشورات، ستوري، تحميل بالكود", "status": "active"},
    {"rank": 3, "name": "tiktok-youtube-dl", "host": "instagram-tiktok-youtube-downloader.p.rapidapi.com",
     "features": "تحميل بالرابط (ريلز، هايلايت، صورة بروفايل)", "status": "active"},
    {"rank": 4, "name": "instagram-api-special", "host": "instagram-api-special.p.rapidapi.com",
     "features": "تحميل ريلز بالرابط", "status": "active"},
    {"rank": 5, "name": "instagram-api39", "host": "instagram-api39.p.rapidapi.com",
     "features": "تحميل ريلز بالرابط", "status": "active"},
    {"rank": 6, "name": "scraper-api-advanced", "host": "instagram-scraper-api-advanced.p.rapidapi.com",
     "features": "تحميل ريلز بالكود، معلومات مستخدم", "status": "active"},
]

LAST_USED_API = {"name": "", "rank": 0}


def _hdr(host):
    return {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": host, "Content-Type": "application/json"}


def _get(host, path, params=None):
    try:
        return requests.get(f"https://{host}{path}", headers=_hdr(host), params=params, timeout=TIMEOUT).json()
    except Exception:
        return None


def _post(host, path, payload):
    try:
        return requests.post(f"https://{host}{path}", headers=_hdr(host), json=payload, timeout=TIMEOUT).json()
    except Exception:
        return None


def _mark_api(rank, name):
    LAST_USED_API["rank"] = rank
    LAST_USED_API["name"] = name


def _extract_username(q):
    q = q.strip()
    m = re.search(r"instagram\.com/([A-Za-z0-9._]+)/?", q)
    if m and "/p/" not in q and "/reel/" not in q and "/stories/" not in q:
        return m.group(1)
    if "/" in q or "." in q:
        return None
    return q.lstrip("@")


def _extract_shortcode(q):
    q = q.strip()
    m = re.search(r"instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)", q)
    return m.group(1) if m else None


def _best_video(it):
    vv = it.get("video_versions") or []
    if vv and isinstance(vv, list):
        return vv[0].get("url")
    return it.get("video_url") or it.get("videoUrl") or it.get("download_url") or it.get("video") or it.get("url")


def _best_thumb(it):
    iv = it.get("image_versions2") or it.get("image_versions") or {}
    if isinstance(iv, dict) and iv.get("candidates"):
        return iv["candidates"][0].get("url")
    if isinstance(iv, list) and iv:
        return iv[0].get("url")
    return it.get("thumbnail_url") or it.get("thumbnailUrl") or it.get("thumbnail") or it.get("display_url") or it.get("thumb") or it.get("imageUrl")


def _dedup_key(url):
    if not url:
        return None
    p = urlparse(url)
    return p.path.split("/")[-1].split("?")[0] if p.path else url


def _dedup_media(items):
    seen, out = set(), []
    for it in items:
        url = it.get("url")
        key = _dedup_key(url) or it.get("id") or url
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def _norm_profile(username, uname, full_name, pic, followers, following, bio, post_count, verified=False, private=False, uid=""):
    return {
        "username": uname or username, "full_name": full_name or "",
        "profile_pic": pic or "", "user_id": str(uid or ""),
        "is_private": private, "is_verified": verified,
        "followers": followers, "following": following,
        "biography": bio or "", "post_count": post_count,
    }


IG120 = "instagram120.p.rapidapi.com"

def _ig120_userinfo(username):
    j = _post(IG120, "/api/instagram/userInfo", {"username": username})
    if not j or not j.get("result"):
        return None
    u = j["result"][0].get("user", {}) if j["result"] else {}
    return _norm_profile(username, u.get("username"), u.get("full_name"), u.get("profile_pic_url"),
        u.get("follower_count"), u.get("following_count"), u.get("biography"),
        u.get("media_count"), u.get("is_verified", False), u.get("is_private", False), u.get("pk") or u.get("id"))

def _ig120_media_by_shortcode(code):
    j = _post(IG120, "/api/instagram/mediaByShortcode", {"shortcode": code})
    if not j:
        return None
    if isinstance(j, list):
        urls = j[0].get("urls", []) if j else []
        return urls[0].get("url") if urls else None
    urls = j.get("urls", [])
    return urls[0].get("url") if urls and isinstance(urls, list) else None

def _ig120_posts(username):
    j = _post(IG120, "/api/instagram/posts", {"username": username})
    if not j or not j.get("result"):
        return []
    edges = j.get("result", {}).get("edges", []) if isinstance(j.get("result"), dict) else []
    out = []
    for e in edges:
        n = e.get("node", {})
        mt = n.get("media_type")
        if mt == 2 or n.get("product_type") == "clips":
            v = _best_video(n)
            if v: out.append({"url": v, "type": "video", "thumb": _best_thumb(n), "id": str(n.get("pk") or n.get("id") or "")})
        elif mt == 8:
            for c in n.get("carousel_media", n.get("children", [])):
                if c.get("media_type") == 2:
                    v = _best_video(c)
                    if v: out.append({"url": v, "type": "video", "thumb": _best_thumb(c), "id": str(c.get("pk") or "")})
                else:
                    t = _best_thumb(c)
                    if t: out.append({"url": t, "type": "image", "thumb": t, "id": str(c.get("pk") or "")})
        else:
            t = _best_thumb(n)
            if t: out.append({"url": t, "type": "image", "thumb": t, "id": str(n.get("pk") or n.get("id") or "")})
    return out

def _ig120_reels(username):
    j = _post(IG120, "/api/instagram/reels", {"username": username})
    if not j or not j.get("result"):
        return []
    edges = j.get("result", {}).get("edges", []) if isinstance(j.get("result"), dict) else []
    out = []
    for e in edges:
        n = e.get("node", {})
        m = n.get("media", n)
        code = m.get("code", "")
        v = _best_video(m)
        if not v and code: v = _ig120_media_by_shortcode(code)
        if v: out.append({"url": v, "type": "video", "thumb": _best_thumb(m), "id": str(m.get("pk") or m.get("id") or "")})
    return out

def _ig120_stories(username):
    j = _post(IG120, "/api/instagram/stories", {"username": username})
    if not j or not j.get("result"):
        return []
    out = []
    for it in j.get("result", []):
        v = _best_video(it)
        if v: out.append({"url": v, "type": "video", "thumb": _best_thumb(it), "id": str(it.get("pk") or it.get("id") or "")})
        else:
            t = _best_thumb(it)
            if t: out.append({"url": t, "type": "image", "thumb": t, "id": str(it.get("pk") or it.get("id") or "")})
    return out

def _ig120_highlights(username):
    j = _post(IG120, "/api/instagram/highlights", {"username": username})
    if not j or not j.get("result"):
        return []
    all_items = []
    for h in j.get("result", []):
        items = _ig120_highlight_stories(h.get("id", ""))
        for it in items:
            it["title"] = h.get("title", "")
            all_items.append(it)
    return all_items

def _ig120_highlight_stories(hid):
    j = _post(IG120, "/api/instagram/highlightStories", {"highlightId": hid})
    if not j or not j.get("result"):
        return []
    out = []
    for it in j.get("result", []):
        v = _best_video(it)
        if v: out.append({"url": v, "type": "video", "thumb": _best_thumb(it), "id": str(it.get("pk") or it.get("id") or "")})
        else:
            t = _best_thumb(it)
            if t: out.append({"url": t, "type": "image", "thumb": t, "id": str(it.get("pk") or it.get("id") or "")})
    return out


IG362 = "instagram362.p.rapidapi.com"

def _ig362_user(username):
    j = _get(IG362, f"/user/{username}")
    if not j or not isinstance(j, dict) or not j.get("username"):
        return None
    return _norm_profile(username, j.get("username"), j.get("fullName"), j.get("profilePicUrl") or j.get("hdProfilePicUrl"),
        j.get("followerCount"), j.get("followingCount"), j.get("bio"), j.get("postCount"), False, j.get("isPrivate", False), j.get("id"))

def _ig362_posts(username):
    j = _get(IG362, f"/posts/{username}")
    if not j or not isinstance(j, list):
        return []
    out = []
    for p in j:
        v = p.get("videoUrl")
        if v: out.append({"url": v, "type": "video", "thumb": p.get("imageUrl", ""), "id": str(p.get("postId") or "")})
        else:
            img = p.get("imageUrl")
            if img: out.append({"url": img, "type": "image", "thumb": img, "id": str(p.get("postId") or "")})
    return out

def _ig362_stories(username):
    j = _get(IG362, f"/stories/{username}")
    if not j or not isinstance(j, list):
        return []
    out = []
    for s in j:
        v = s.get("videoUrl")
        if v: out.append({"url": v, "type": "video", "thumb": s.get("imageUrl", ""), "id": str(s.get("id") or s.get("createdAt") or "")})
        else:
            img = s.get("imageUrl")
            if img: out.append({"url": img, "type": "image", "thumb": img, "id": str(s.get("id") or s.get("createdAt") or "")})
    return out

def _ig362_post_by_code(code):
    j = _get(IG362, f"/post/{code}")
    if not j or not isinstance(j, list):
        return None
    out = []
    for p in j:
        v = p.get("videoUrl")
        if v: out.append({"url": v, "type": "video", "thumb": p.get("imageUrl", ""), "id": code})
        else:
            img = p.get("imageUrl")
            if img: out.append({"url": img, "type": "image", "thumb": img, "id": code})
    return out or None


TTDL = "instagram-tiktok-youtube-downloader.p.rapidapi.com"

def _ttdl_fetch(url):
    j = _get(TTDL, "/fetch", {"url": url})
    if not j or not j.get("ok"):
        return None
    items = []
    if j.get("items"):
        for it in j["items"]:
            dl = it.get("download_url") or it.get("url")
            if dl: items.append({"url": dl, "type": it.get("type", "video"), "thumb": it.get("thumbnail_url", ""), "id": it.get("id", "")})
    elif j.get("download_url"):
        items.append({"url": j["download_url"], "type": j.get("type", "video"), "thumb": j.get("thumbnail_url", ""), "id": "1"})
    return items or None


APISPEC = "instagram-api-special.p.rapidapi.com"

def _apispec_fetch(url):
    j = _get(APISPEC, "/instagram/", {"url": url})
    if not j or not j.get("status"):
        return None
    out = []
    for r in (j.get("result") or []):
        u = r.get("url") or r.get("video_url") or r.get("download_url")
        if u: out.append({"url": u, "type": "video" if ".mp4" in u else "image", "thumb": r.get("thumbnail", ""), "id": r.get("id", "")})
    return out or None


API39 = "instagram-api39.p.rapidapi.com"

def _api39_fetch(url):
    j = _get(API39, "/instagram/", {"url": url})
    if not j or not j.get("status"):
        return None
    out = []
    for r in (j.get("result") or []):
        u = r.get("url") or r.get("video_url") or r.get("download_url")
        if u: out.append({"url": u, "type": "video" if ".mp4" in u else "image", "thumb": r.get("thumbnail", ""), "id": r.get("id", "")})
    return out or None


SCRADV = "instagram-scraper-api-advanced.p.rapidapi.com"

def _scradv_reel(code):
    j = _get(SCRADV, f"/api/download/reel/{code}")
    if not j or not j.get("success"):
        return None
    d = j.get("data", {})
    v = d.get("videoUrl") or d.get("video_url")
    if v: return [{"url": v, "type": "video", "thumb": d.get("thumbnailUrl", ""), "id": d.get("shortcode", "")}]
    return None


def search(q):
    username = _extract_username(q)
    if username:
        return _search_by_username(username)
    code = _extract_shortcode(q)
    if code:
        return _search_by_shortcode(code)
    return None

def _search_by_username(username):
    profile = _ig120_userinfo(username)
    if profile:
        _mark_api(1, "instagram120")
        return {"profile": profile, "media": _dedup_media(_ig120_posts(username)), "api_used": "instagram120 (#1)"}
    profile = _ig362_user(username)
    if profile:
        _mark_api(2, "instagram362")
        return {"profile": profile, "media": _dedup_media(_ig362_posts(username)), "api_used": "instagram362 (#2)"}
    return None

def _search_by_shortcode(code):
    url = f"https://www.instagram.com/reel/{code}/"
    media = _ttdl_fetch(url)
    if media:
        _mark_api(3, "tiktok-youtube-dl")
        return {"profile": None, "media": _dedup_media(media), "api_used": "tiktok-youtube-dl (#3)"}
    media = _apispec_fetch(url)
    if media:
        _mark_api(4, "instagram-api-special")
        return {"profile": None, "media": _dedup_media(media), "api_used": "instagram-api-special (#4)"}
    media = _api39_fetch(url)
    if media:
        _mark_api(5, "instagram-api39")
        return {"profile": None, "media": _dedup_media(media), "api_used": "instagram-api39 (#5)"}
    media = _scradv_reel(code)
    if media:
        _mark_api(6, "scraper-api-advanced")
        return {"profile": None, "media": _dedup_media(media), "api_used": "scraper-api-advanced (#6)"}
    v = _ig120_media_by_shortcode(code)
    if v:
        _mark_api(1, "instagram120")
        return {"profile": None, "media": _dedup_media([{"url": v, "type": "video", "thumb": "", "id": code}]), "api_used": "instagram120 (#1)"}
    media = _ig362_post_by_code(code)
    if media:
        _mark_api(2, "instagram362")
        return {"profile": None, "media": _dedup_media(media), "api_used": "instagram362 (#2)"}
    return None

def fetch_tab(username, tab):
    username = username.lstrip("@")
    if tab == "posts":
        m = _ig120_posts(username)
        if m: _mark_api(1, "instagram120"); return _dedup_media(m)
        m = _ig362_posts(username)
        if m: _mark_api(2, "instagram362"); return _dedup_media(m)
        return []
    if tab == "reels":
        m = _ig120_reels(username)
        if m: _mark_api(1, "instagram120"); return _dedup_media(m)
        return []
    if tab == "stories":
        m = _ig120_stories(username)
        if m: _mark_api(1, "instagram120"); return _dedup_media(m)
        m = _ig362_stories(username)
        if m: _mark_api(2, "instagram362"); return _dedup_media(m)
        return []
    if tab == "highlights":
        m = _ig120_highlights(username)
        if m: _mark_api(1, "instagram120"); return _dedup_media(m)
        return []
    return []
