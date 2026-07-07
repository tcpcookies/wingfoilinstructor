#!/usr/bin/env python3
from __future__ import annotations

import posixpath
import time
import urllib.request
from pathlib import Path


ORIGIN = "https://wingfoilinstructor.com"
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT

PAGES = {
    "/": "index.html",
    "/start/": "start/index.html",
    "/ABLAUF-SCHULUNG/": "ABLAUF-SCHULUNG/index.html",
    "/WINGFOIL-VERLEIH/": "WINGFOIL-VERLEIH/index.html",
    "/trainer/": "trainer/index.html",
    "/PARTNER/": "PARTNER/index.html",
    "/kontakt/": "kontakt/index.html",
    "/KONTAKT/Impressum/": "kontakt/Impressum/index.html",
}

OLD_CONTACT_BLOCK = (
    '<p style="text-align: center;">Wingfoil Instructor</p>'
    '<p style="text-align: center;">Stefan Bernt</p>'
    '<p style="text-align: center;">Görbelmoosweg 14<br></p>'
    '<p style="text-align: center;">01590- 1010101| info@wingfoil-instructor.com<br></p>'
)

NEW_CONTACT_BLOCK = (
    '<p style="text-align: center;">Contacts: David Leidenfrost</p>'
    '<p style="text-align: center;">Adress: Helgolander Str. 94<br>'
    '28217 Bremen<br>Germany</p>'
    '<p style="text-align: center;">Phone: +49 1578 7165058<br>'
    'Email: <a href="mailto:David.Leidenfrost@gmail.com" class="cm_anchor">'
    'David.Leidenfrost@gmail.com</a><br></p>'
)

OLD_IMPRESSUM_BLOCK = (
    "Impressum<br>Angaben gemäß § 5 TMG<br>Wingfoil Instructor.de<br>"
    "Bernt Stefan<br>Görbelmoosweg 14<br>82205 Gilching<br>Kontakt<br>"
    "Telefon: 0049 159 01010101<br>E-Mail: info@wingfoil-instructor.de"
)

NEW_IMPRESSUM_BLOCK = (
    "Impressum<br>Angaben gemäß § 5 TMG<br>Wingfoil Instructor.de<br>"
    "David Leidenfrost<br>Helgolander Str. 94<br>28217 Bremen<br>"
    'Germany<br>Kontakt<br>Telefon: +49 1578 7165058<br>'
    'E-Mail: <a href="mailto:David.Leidenfrost@gmail.com" class="cm_anchor">'
    "David.Leidenfrost@gmail.com</a>"
)


def fetch(path: str) -> str:
    req = urllib.request.Request(
        ORIGIN + path,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=35) as response:
        return response.read().decode("utf-8", errors="replace")


def rel_link(current_output: str, target_path: str) -> str:
    current_dir = posixpath.dirname(current_output) or "."
    target_output = PAGES[target_path]
    target_dir = posixpath.dirname(target_output) or "."
    rel = posixpath.relpath(target_dir, current_dir)
    return "./" if rel == "." else rel + "/"


def rewrite_html(html: str, current_output: str) -> str:
    # Keep vendor/runtime resources on the authorized source host.
    html = html.replace('="/.cm4all', f'="{ORIGIN}/.cm4all')
    html = html.replace("='/.cm4all", f"='{ORIGIN}/.cm4all")
    html = html.replace('url("/.cm4all', f'url("{ORIGIN}/.cm4all')
    html = html.replace("url('/.cm4all", f"url('{ORIGIN}/.cm4all")
    html = html.replace('url(/.cm4all', f"url({ORIGIN}/.cm4all")
    html = html.replace('href="/index.php', f'href="{ORIGIN}/index.php')
    html = html.replace("href='/index.php", f"href='{ORIGIN}/index.php")
    html = html.replace('href="/start/index.php', f'href="{ORIGIN}/start/index.php')
    html = html.replace("href='/start/index.php", f"href='{ORIGIN}/start/index.php")
    html = html.replace(OLD_CONTACT_BLOCK, NEW_CONTACT_BLOCK)
    html = html.replace(OLD_IMPRESSUM_BLOCK, NEW_IMPRESSUM_BLOCK)
    html = html.replace("mailto:info@wingfoil-instructor.com", "mailto:David.Leidenfrost@gmail.com")
    html = html.replace("tel:+4915901010101", "tel:+4915787165058")
    html = html.replace(
        '<li id="cm_navigation_pid_7121621"><a title="WINGFOILEN" href="/start/" class="cm_anchor">WINGFOILEN</a></li>',
        "",
    )
    html = html.replace(
        '<li id="cm_navigation_pid_7121621" class="cm_current"><a title="WINGFOILEN" href="/start/" class="cm_anchor">WINGFOILEN</a></li>',
        "",
    )
    html = html.replace(
        '<li id="cm_navigation_pid_7121621" class="cm_current"><a title="WINGFOILEN" href="/" class="cm_anchor">WINGFOILEN</a></li>',
        "",
    )
    html = html.replace('navigationText: "WINGFOILEN"', 'navigationText: ""')
    html = html.replace("&amp;nt=WINGFOILEN", "&amp;nt=")

    for source_path in sorted(PAGES, key=len, reverse=True):
        if source_path == "/":
            continue
        local = rel_link(current_output, source_path)
        html = html.replace(f'href="{source_path}"', f'href="{local}"')
        html = html.replace(f"href='{source_path}'", f"href='{local}'")
        html = html.replace(f'action="{source_path}"', f'action="{local}"')
        html = html.replace(f"action='{source_path}'", f"action='{local}'")

    html = html.replace('href="/"', 'href="./"')
    html = html.replace("href='/'", "href='./'")

    marker = "</head>"
    injected = (
        '<script>document.documentElement.classList.add("github-pages-static-copy");</script>'
        "\n"
    )
    if marker in html and "github-pages-static-copy" not in html:
        html = html.replace(marker, injected + marker, 1)
    return html


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    for path, output in PAGES.items():
        print(f"Fetching {path}")
        html = fetch(path)
        html = rewrite_html(html, output)
        destination = SITE / output
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(html, encoding="utf-8")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
