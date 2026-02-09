import re
from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash

from .models import db, Enquiry
from .email_utils import send_enquiry_email


main = Blueprint("main", __name__)


def clean_phone(phone: str) -> str:
    """Keep digits and plus only."""
    phone = (phone or "").strip()
    return re.sub(r"[^\d+]", "", phone)


@main.route("/")
def index():
    return render_template("index.html")  # landing page
@main.route("/terms")
def terms():
    return render_template("terms.html")


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/practice-areas")  # this must render its own template
def practice_areas():
    return render_template("practice_areas.html")  # make sure this file exists


@main.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        phone = clean_phone(request.form.get("phone") or "")
        subject = (request.form.get("subject") or "").strip()
        message = (request.form.get("message") or "").strip()

        # basic validation
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
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
            user_agent=(request.headers.get("User-Agent") or "")[:255],
        )

        db.session.add(enquiry)
        db.session.commit()

        # send email notification (don’t crash the user if email fails)
        try:
            print("Sending to:", current_app.config.get("OCHIRLAW_INBOX"))
            send_enquiry_email(current_app, enquiry)
        except Exception:
            # Keep it quiet in prod; log server-side if you have logging
            pass

        flash("Thanks — we’ve received your enquiry and will be in touch.", "success")
        return redirect(url_for("main.contact"))

    return render_template("contact.html")
