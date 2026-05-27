import os
import re
from functools import wraps

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .models import db, Enquiry, BlogPost
from .email_utils import send_enquiry_email


main = Blueprint("main", __name__)


SUPPORTED_BLOG_LANGUAGES = {"en", "mn"}


def clean_phone(phone: str) -> str:
    """Keep digits and plus only."""
    phone = (phone or "").strip()
    return re.sub(r"[^\d+]", "", phone)


def slugify(value: str) -> str:
    """Create a simple SEO-friendly slug."""
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "article"


def unique_slug(base_slug: str, post_id: int | None = None) -> str:
    """Ensure blog slugs stay unique when new articles are created."""
    slug = slugify(base_slug)
    candidate = slug
    counter = 2

    while True:
        query = BlogPost.query.filter_by(slug=candidate)
        if post_id:
            query = query.filter(BlogPost.id != post_id)
        if query.first() is None:
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to manage blog articles.", "warning")
            return redirect(url_for("main.admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/terms")
def terms():
    return render_template("terms.html")


@main.route("/privacy")
def privacy():
    return render_template("privacy.html")


@main.route("/privacy-policy")
def privacy_policy():
    return redirect(url_for("main.privacy"))


@main.route("/privacy-collection-statement")
def collection_statement():
    return render_template("privacy_collection_statement.html")


@main.route("/collection-statement")
def collection_statement_redirect():
    return redirect(url_for("main.collection_statement"))


@main.route("/terms-and-conditions")
def terms_and_conditions():
    return redirect(url_for("main.terms"))


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/team")
def team():
    return render_template("team.html")


@main.route("/practice-areas")
def practice_areas():
    return render_template("practice_areas.html")


@main.route("/industries")
def industries():
    return render_template("industries.html")


@main.route("/blog")
def blog_redirect():
    return redirect(url_for("main.blog_index", lang="en"))


@main.route("/blog/<lang>")
def blog_index(lang: str):
    if lang not in SUPPORTED_BLOG_LANGUAGES:
        abort(404)

    posts = (
        BlogPost.query.filter_by(is_published=True)
        .order_by(BlogPost.created_at.desc())
        .all()
    )
    return render_template("blog/index.html", posts=posts, lang=lang)


@main.route("/blog/<lang>/<slug>")
def blog_detail(lang: str, slug: str):
    if lang not in SUPPORTED_BLOG_LANGUAGES:
        abort(404)

    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    alternate_lang = "mn" if lang == "en" else "en"
    return render_template(
        "blog/detail.html",
        post=post,
        lang=lang,
        alternate_lang=alternate_lang,
    )


@main.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    configured_password = os.environ.get("OCHIRLAW_ADMIN_PASSWORD", "")

    if request.method == "POST":
        password = request.form.get("password") or ""
        if configured_password and password == configured_password:
            session["admin_logged_in"] = True
            flash("Logged in successfully.", "success")
            return redirect(request.args.get("next") or url_for("main.admin_blogs"))

        flash("Incorrect password, or admin password is not configured.", "danger")

    return render_template("admin/login.html", admin_enabled=bool(configured_password))


@main.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Logged out.", "info")
    return redirect(url_for("main.index"))


@main.route("/admin/blogs")
@admin_required
def admin_blogs():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("admin/blogs.html", posts=posts)


@main.route("/admin/blogs/new", methods=["GET", "POST"])
@admin_required
def admin_blog_new():
    post = BlogPost(author="Munkh-Erdene Saruul", is_published=False)

    if request.method == "POST":
        post.title_en = (request.form.get("title_en") or "").strip()
        post.title_mn = (request.form.get("title_mn") or "").strip()
        post.summary_en = (request.form.get("summary_en") or "").strip()
        post.summary_mn = (request.form.get("summary_mn") or "").strip()
        post.content_en = (request.form.get("content_en") or "").strip()
        post.content_mn = (request.form.get("content_mn") or "").strip()
        post.featured_image = (request.form.get("featured_image") or "").strip()
        post.category = (request.form.get("category") or "").strip()
        post.author = (request.form.get("author") or "Munkh-Erdene Saruul").strip()
        post.is_published = request.form.get("is_published") == "on"
        post.slug = unique_slug(request.form.get("slug") or post.title_en)

        if not post.title_en or not post.title_mn or not post.content_en or not post.content_mn:
            flash("English and Mongolian titles and article content are required.", "danger")
            return render_template("admin/blog_form.html", post=post, mode="new")

        db.session.add(post)
        db.session.commit()
        flash("Blog article created.", "success")
        return redirect(url_for("main.admin_blogs"))

    return render_template("admin/blog_form.html", post=post, mode="new")


@main.route("/admin/blogs/<int:post_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_blog_edit(post_id: int):
    post = BlogPost.query.get_or_404(post_id)

    if request.method == "POST":
        post.title_en = (request.form.get("title_en") or "").strip()
        post.title_mn = (request.form.get("title_mn") or "").strip()
        post.summary_en = (request.form.get("summary_en") or "").strip()
        post.summary_mn = (request.form.get("summary_mn") or "").strip()
        post.content_en = (request.form.get("content_en") or "").strip()
        post.content_mn = (request.form.get("content_mn") or "").strip()
        post.featured_image = (request.form.get("featured_image") or "").strip()
        post.category = (request.form.get("category") or "").strip()
        post.author = (request.form.get("author") or "Munkh-Erdene Saruul").strip()
        post.is_published = request.form.get("is_published") == "on"
        post.slug = unique_slug(request.form.get("slug") or post.title_en, post.id)

        if not post.title_en or not post.title_mn or not post.content_en or not post.content_mn:
            flash("English and Mongolian titles and article content are required.", "danger")
            return render_template("admin/blog_form.html", post=post, mode="edit")

        db.session.commit()
        flash("Blog article updated.", "success")
        return redirect(url_for("main.admin_blogs"))

    return render_template("admin/blog_form.html", post=post, mode="edit")


@main.route("/admin/blogs/<int:post_id>/delete", methods=["POST"])
@admin_required
def admin_blog_delete(post_id: int):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Blog article deleted.", "info")
    return redirect(url_for("main.admin_blogs"))


@main.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        phone = clean_phone(request.form.get("phone") or "")
        subject = (request.form.get("subject") or "").strip()
        message = (request.form.get("message") or "").strip()

        if not phone or len(phone) < 8:
            flash("Please enter a valid phone number.", "danger")
            return redirect(url_for("main.contact"))

        if not message or len(message) < 10:
            flash("Please enter a short message (at least 10 characters).", "danger")
            return redirect(url_for("main.contact"))

        enquiry = Enquiry(
            name=name or None,
            email=email or None,
            phone=phone,
            subject=subject or None,
            message=message,
        )

        db.session.add(enquiry)
        db.session.commit()

        try:
            print("Sending to:", current_app.config.get("OCHIRLAW_INBOX"))
            send_enquiry_email(current_app, enquiry)
        except Exception:
            pass

        flash("Thanks — we’ve received your enquiry and will be in touch.", "success")
        return redirect(url_for("main.contact"))

    return render_template("contact.html")
