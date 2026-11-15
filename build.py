"""Build the Ochir Law website into plain static files.

Run:  python build.py          -> writes the finished site to dist/
      python build.py --serve  -> builds, then previews at http://localhost:8000

Pages live in templates/, blog posts in content/blog/<slug>/, and images,
fonts and CSS in static/. See README.md for how to add a blog post.
"""

import shutil
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).parent
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
BLOG_DIR = ROOT / "content" / "blog"
OUT = ROOT / "dist"

# Change this if the live domain is different.
SITE_URL = "https://ochirlaw.com.au"
LANGS = ("en", "mn")
DEFAULT_AUTHOR = "Munkh-Erdene Saruul"

# Simple pages: endpoint name -> (template, output path)
PAGES = {
    "main.index": ("index.html", ""),
    "main.about": ("about.html", "about"),
    "main.team": ("team.html", "team"),
    "main.practice_areas": ("practice_areas.html", "practice-areas"),
    "main.industries": ("industries.html", "industries"),
    "main.contact": ("contact.html", "contact"),
    "main.terms": ("terms.html", "terms"),
    "main.privacy": ("privacy.html", "privacy"),
    "main.collection_statement": ("privacy_collection_statement.html", "privacy-collection-statement"),
}

# Old addresses that should keep working.
REDIRECTS = {
    "blog": "/blog/en/",
    "privacy-policy": "/privacy/",
    "terms-and-conditions": "/terms/",
    "collection-statement": "/privacy-collection-statement/",
}


# ---------------------------------------------------------------- blog posts

@dataclass
class Post:
    slug: str
    folder: Path
    date: datetime
    category: str = ""
    author: str = DEFAULT_AUTHOR
    image: str = ""
    layout: str = "blog/detail.html"
    published: bool = True
    title: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)
    body: dict = field(default_factory=dict)

    # Names the existing templates already use.
    @property
    def title_en(self): return self.title.get("en", "")
    @property
    def title_mn(self): return self.title.get("mn", "")
    @property
    def summary_en(self): return self.summary.get("en", "")
    @property
    def summary_mn(self): return self.summary.get("mn", "")
    @property
    def content_en(self): return self.body.get("en", "")
    @property
    def content_mn(self): return self.body.get("mn", "")
    @property
    def featured_image(self): return self.image
    @property
    def created_at(self): return self.date
    @property
    def updated_at(self): return self.date


def read_markdown(path: Path) -> tuple[dict, str]:
    """Split a markdown file into its --- front matter --- and body."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        _, front, body = text.split("---", 2)
        return yaml.safe_load(front) or {}, body.strip()
    return {}, text.strip()


def to_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    return datetime.fromisoformat(str(value))


def load_posts() -> list[Post]:
    posts = []
    if not BLOG_DIR.exists():
        return posts
    for folder in sorted(BLOG_DIR.iterdir()):
        meta_file = folder / "post.yml"
        if not folder.is_dir() or folder.name.startswith("_") or not meta_file.exists():
            continue
        meta = yaml.safe_load(meta_file.read_text(encoding="utf-8")) or {}
        post = Post(
            slug=folder.name,
            folder=folder,
            date=to_datetime(meta.get("date", date.today())),
            category=meta.get("category", ""),
            author=meta.get("author", DEFAULT_AUTHOR),
            image=meta.get("image", ""),
            layout=meta.get("layout", "blog/detail.html"),
            published=meta.get("published", True),
        )
        for lang in LANGS:
            md_file = folder / f"{lang}.md"
            if not md_file.exists():
                sys.exit(f"Blog post '{folder.name}' is missing {lang}.md")
            front, body = read_markdown(md_file)
            post.title[lang] = front.get("title", "")
            post.summary[lang] = front.get("summary", "")
            post.body[lang] = body
            if not post.title[lang]:
                sys.exit(f"Blog post '{folder.name}/{lang}.md' needs a title")
        if post.published:
            posts.append(post)
    return sorted(posts, key=lambda p: p.date, reverse=True)


# ------------------------------------------------------------------ helpers

def make_url_for(current_endpoint: str):
    """Stand-in for Flask's url_for so the templates work unchanged."""

    def url_for(endpoint, _external=False, **kw):
        if endpoint == "static":
            path = "/static/" + kw["filename"]
        elif endpoint in PAGES:
            out = PAGES[endpoint][1]
            path = f"/{out}/" if out else "/"
        elif endpoint == "main.blog_index":
            path = f"/blog/{kw['lang']}/"
        elif endpoint == "main.blog_detail":
            path = f"/blog/{kw['lang']}/{kw['slug']}/"
        else:
            raise KeyError(f"Unknown page link in template: {endpoint}")
        return SITE_URL + path if _external else path

    return url_for


class FakeRequest:
    def __init__(self, endpoint):
        self.endpoint = endpoint


def write(path: str, html: str):
    target = OUT / path / "index.html" if not path.endswith(".html") else OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


def redirect_page(to: str) -> str:
    return (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<meta http-equiv="refresh" content="0; url={to}">'
        f'<link rel="canonical" href="{SITE_URL}{to}">'
        f'<title>Redirecting…</title></head><body><a href="{to}">Continue</a></body></html>'
    )


# -------------------------------------------------------------------- build

def build():
    env = Environment(
        loader=FileSystemLoader([TEMPLATES, BLOG_DIR]),
        autoescape=select_autoescape(["html"]),
    )
    env.globals["current_year"] = date.today().year
    env.globals["get_flashed_messages"] = lambda **kw: []
    md = markdown.Markdown(extensions=["extra", "sane_lists"])
    env.filters["markdown"] = lambda text: Markup(md.reset().convert(text or ""))

    def render(template, endpoint, **ctx):
        return env.get_template(template).render(
            url_for=make_url_for(endpoint), request=FakeRequest(endpoint), **ctx
        )

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(STATIC, OUT / "static")

    urls = []

    for endpoint, (template, out) in PAGES.items():
        write(out, render(template, endpoint))
        urls.append(f"/{out}/" if out else "/")

    posts = load_posts()
    for lang in LANGS:
        write(f"blog/{lang}", render("blog/index.html", "main.blog_index", posts=posts, lang=lang))
        urls.append(f"/blog/{lang}/")
        for post in posts:
            out = f"blog/{lang}/{post.slug}"
            alt = "mn" if lang == "en" else "en"
            write(out, render(post.layout, "main.blog_detail", post=post, lang=lang, alternate_lang=alt))
            urls.append(f"/{out}/")

    # Copy each post's images next to it, so en.md can use ![](photo.jpg)
    for post in posts:
        for f in post.folder.iterdir():
            if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".pdf"}:
                for lang in LANGS:
                    shutil.copy2(f, OUT / "blog" / lang / post.slug / f.name)

    for old, new in REDIRECTS.items():
        write(old, redirect_page(new))

    if (TEMPLATES / "404.html").exists():
        write("404.html", render("404.html", "404"))

    sitemap = "\n".join(f"  <url><loc>{SITE_URL}{u}</loc></url>" for u in urls)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap}\n</urlset>\n",
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")

    print(f"Built {len(urls)} pages and {len(posts)} blog post(s) into {OUT.name}/")


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        import functools
        import http.server

        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=OUT)
        print("Preview at http://localhost:8000  (Ctrl+C to stop)")
        http.server.ThreadingHTTPServer(("", 8000), handler).serve_forever()
