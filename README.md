# Ochir Law website

A static website: plain HTML files built from templates. There's no server or database to run.
Bookings and enquiries go through Smokeball (embedded on the Contact page).

## How it's organised

```
templates/        the pages (home, about, team, practice areas, …) and shared layout (base.html)
static/           CSS, fonts and images
content/blog/     blog posts, one folder per post
build.py          turns all of the above into the finished site in dist/
```

## Making a change

Edit any file on github.com (pencil icon) or locally, then commit to `main`.
The host rebuilds and publishes the site automatically within about a minute.

## Adding a blog post

1. Copy `content/blog/_example/` and rename the copy, e.g. `content/blog/new-construction-laws/`.
   The folder name becomes the address: `/blog/en/new-construction-laws/`.
2. Edit `post.yml` (date, category, cover image).
3. Write the English article in `en.md` and the Mongolian one in `mn.md`.
4. Put any images in the same folder and refer to them by file name.
5. Commit. The post appears on the blog list, newest first.

To hide a post without deleting it, set `published: false` in its `post.yml`.

### Custom-designed posts

For a post with its own layout, create a template in `templates/blog/layouts/` that starts with
`{% extends "blog/detail.html" %}` and overrides `{% block post_body %}`, then set
`layout: blog/layouts/your-file.html` in the post's `post.yml`. You can also put raw HTML
straight into `en.md` / `mn.md`.

## Previewing locally

```
pip install -r requirements.txt
python build.py --serve
```

Then open http://localhost:8000.

## Hosting (Cloudflare Pages / AWS Amplify / Netlify)

Connect this GitHub repo and use:

- Build command: `pip install -r requirements.txt && python build.py`
- Output directory: `dist`
- Python version: 3.12 (set in `.python-version`)

If the live domain isn't `https://ochirlaw.com.au`, change `SITE_URL` at the top of `build.py`
(it's used for the sitemap and links shared on social media).
