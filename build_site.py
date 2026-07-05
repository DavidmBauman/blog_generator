"""
build_site.py -- tiny static blog generator

Usage:
    python build_site.py

Reads:
    template.html    -- post page shell containing <!--TITLE--> and <!--CONTENT--> markers
    src/<name>.html  -- post fragments, discovered automatically. Each starts
                        with metadata lines, ended by the first blank line:

                            title: My Post Title
                            date: 2026-07-04
                            draft: true          (optional -- excluded from the build)

                            <p>Post content starts after the first blank line...</p>

Writes:
    posts/<name>.html  -- one page per fragment (the folder is wiped and
                          regenerated every build; never hand-edit it)
    blog.html          -- EDITED IN PLACE: the region between <!--POSTS:BEGIN-->
                          and <!--POSTS:END--> is replaced with a fresh <ul> of
                          posts. Everything outside the markers is untouched, so
                          keep hand-editing this page as usual. Safe to re-run.

Ordering:
    Posts are sorted by date, newest first. Use ISO dates (yyyy-mm-dd).
    Posts with no date sort last and produce a warning.
"""

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

SRC_DIR      = Path("src")
OUT_DIR      = Path("posts")
TEMPLATE     = Path("template.html")
BLOG_PAGE    = Path("blog.html")
MARKER_BEGIN = "<!--POSTS:BEGIN-->"
MARKER_END   = "<!--POSTS:END-->"

METADATA_KEYS = {"title", "date", "draft"}


@dataclass
class Post:
    title: str
    date: str
    out_name: str


def die(msg):
    sys.exit(f"error: {msg}")


def warn(msg):
    print(f"warning: {msg}", file=sys.stderr)


def parse_fragment(text):
    """Split leading 'key: value' metadata lines from the content.

    Metadata ends at the first blank line. A fragment with no metadata is
    treated as all content.
    """
    meta = {}
    lines = text.splitlines(keepends=True)
    content_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "":                      # blank line: content follows
            content_start = i + 1
            break
        key, sep, value = stripped.partition(":")
        if sep and key.strip() in METADATA_KEYS:
            meta[key.strip()] = value.strip()
        else:                                   # not metadata: all of it is content
            break

    return meta, "".join(lines[content_start:])


def load_posts():
    """Discover fragments in SRC_DIR, skipping drafts. Returns (post, content) pairs."""
    if not SRC_DIR.is_dir():
        die(f"could not find source folder: {SRC_DIR}")

    loaded = []
    for src in sorted(SRC_DIR.glob("*.html")):
        meta, content = parse_fragment(src.read_text(encoding="utf-8"))

        if meta.get("draft", "").lower() in ("true", "yes", "1"):
            print(f"  {src} -> skipped (draft)")
            continue

        out_name = src.stem + ".html"

        title = meta.get("title", "")
        if not title:
            warn(f"{src} has no 'title:' line, using filename")
            title = out_name

        date = meta.get("date", "")
        if not date:
            warn(f"{src} has no 'date:' line, it will sort last")

        loaded.append((Post(title, date, out_name), content))

    # Newest first. Stable sorts: filename first as tiebreaker, then date
    # descending. Undated posts ("" sorts before any ISO date) land last.
    loaded.sort(key=lambda pair: pair[0].out_name)
    loaded.sort(key=lambda pair: pair[0].date, reverse=True)
    return loaded


def render_post_pages(template, loaded):
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)      # purely generated: wipe so renamed/removed
    OUT_DIR.mkdir()                 # posts never leave stale pages behind

    for post, content in loaded:
        page = (template
                .replace("<!--TITLE-->", post.title)
                .replace("<!--CONTENT-->", content))
        (OUT_DIR / post.out_name).write_text(page, encoding="utf-8")
        print(f"  {SRC_DIR / post.out_name} -> {OUT_DIR / post.out_name}")


def inject_post_list(posts):
    items = []
    for post in posts:
        date_html = f'<span class="post-date">{post.date}</span> ' if post.date else ""
        items.append(f'  <li>{date_html}<a href="{OUT_DIR.name}/{post.out_name}">{post.title}</a></li>')
    post_list = '\n<ul class="post-list">\n' + "\n".join(items) + "\n</ul>\n"

    if not BLOG_PAGE.exists():
        die(f"could not open {BLOG_PAGE}")
    blog = BLOG_PAGE.read_text(encoding="utf-8")

    before, sep_begin, rest = blog.partition(MARKER_BEGIN)
    if not sep_begin:
        die(f"{BLOG_PAGE} is missing marker: {MARKER_BEGIN}")
    _, sep_end, after = rest.partition(MARKER_END)
    if not sep_end:
        die(f"{BLOG_PAGE} is missing marker: {MARKER_END}")

    BLOG_PAGE.write_text(before + MARKER_BEGIN + post_list + MARKER_END + after,
                         encoding="utf-8")
    print(f"  post list -> {BLOG_PAGE} (between markers)")


def main():
    if not TEMPLATE.exists():
        die(f"could not open {TEMPLATE}")
    template = TEMPLATE.read_text(encoding="utf-8")

    loaded = load_posts()
    render_post_pages(template, loaded)
    inject_post_list([post for post, _ in loaded])

    n = len(loaded)
    print(f"done: {n} post{'' if n == 1 else 's'}")


if __name__ == "__main__":
    main()
