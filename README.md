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

## Hosting (Vercel)

The site is hosted on Vercel, which reads `vercel.json` in this repo:

- Build command: `python3 build.py` (dependencies from `requirements.txt`)
- Output directory: `dist`
- Old addresses (`/blog`, `/privacy-policy`, `/terms-and-conditions`, `/collection-statement`, `/admin/...`)
  redirect permanently to their current pages.

Every commit to `main` deploys automatically. Other branches get their own preview link.

If the live domain isn't `https://ochirlaw.com.au`, change `SITE_URL` at the top of `build.py`
(it's used for the sitemap, canonical links and social media previews).

## Where things are

- Fonts: `static/fonts/` (compressed WOFF2; the original TTFs stay as a fallback)
- Optimised logo, background pattern and photos used by the pages: `static/img/`
- Original full-size brand files: `static/images/`
- Bootstrap is served from `static/vendor/` instead of an outside CDN
