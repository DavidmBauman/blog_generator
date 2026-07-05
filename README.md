# blog_generator

A static blog generator in a single Python file.

It scans `src/` for posts, creates an html file per post and pushes it
into `posts/`, and injects a date-sorted list of posts into `blog.html`
between two marker comments. Everything outside the markers is left alone,
so `blog.html` stays a normal hand-edited page.

## Usage

```
python build_site.py
```

Requires Python 3. Run it from the folder containing `build_site.py`.

## Writing a post

Create `src/my-post.html`:

```
title: My Post Title
date: 2026-07-05

<h1>My Post Title</h1>
<p>Content starts after the first blank line.</p>
```

Then run the build.

- Posts are sorted newest-first by `date` (use ISO format: `yyyy-mm-dd`).
- Add `draft: true` to the metadata to exclude a post from the build.

## Files

| File            | Role                                                        |
| --------------- | ----------------------------------------------------------- |
| `build_site.py` | The generator.                                              |
| `template.html` | Shell for post pages. Markers: `<!--TITLE-->`, `<!--CONTENT-->`. |
| `blog.html`     | Blog index page. The list is injected between `<!--POSTS:BEGIN-->` and `<!--POSTS:END-->`. |
| `src/`          | Post fragments (your content).                              |
| `posts/`        | Generated output. Wiped and rebuilt every run — never hand-edit, not committed. |
