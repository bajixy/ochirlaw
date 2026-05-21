from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Enquiry(db.Model):
    __tablename__ = "enquiries"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(40), nullable=False)
    subject = db.Column(db.String(160))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(220), unique=True, nullable=False)

    title_en = db.Column(db.String(220), nullable=False)
    title_mn = db.Column(db.String(220), nullable=False)
    summary_en = db.Column(db.Text)
    summary_mn = db.Column(db.Text)
    content_en = db.Column(db.Text, nullable=False)
    content_mn = db.Column(db.Text, nullable=False)

    featured_image = db.Column(db.String(500))
    category = db.Column(db.String(120))
    author = db.Column(db.String(120), default="Munkh-Erdene Saruul")
    is_published = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
