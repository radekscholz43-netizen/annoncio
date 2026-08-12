#!/usr/bin/env python3
"""
Osobni archiv inzeratu z annonce.cz.

Stahuje konkretni inzeraty (zadane uzivatelem pres URL), ktere by jinak
mohly zmizet, a uklada je lokalne (text, atributy, kontakt, fotky).

Pouziti:
    python download_ads.py urls.txt
    python download_ads.py https://www.annonce.cz/inzerat/... https://www.annonce.cz/inzerat/...
"""

import csv
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_DELAY_SECONDS = 2  # slusna prodleva mezi pozadavky
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "stazene_inzeraty"
INDEX_FILE = OUTPUT_DIR / "index.csv"


def load_urls(args: list[str]) -> list[str]:
    urls: list[str] = []
    for arg in args:
        path = Path(arg)
        if path.is_file():
            with path.open(encoding="utf-8") as f:
                urls.extend(line.strip() for line in f if line.strip() and not line.startswith("#"))
        else:
            urls.append(arg.strip())
    return urls


def ad_id_from_url(url: str) -> str:
    match = re.search(r"/inzerat/([\w-]+)\.html", url)
    if not match:
        raise ValueError(f"Nerozpoznane URL inzeratu: {url}")
    return match.group(1)


def request_with_retry(url: str, attempts: int = 3, delay: float = 1.5):
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
            resp.raise_for_status()
            return resp
        except Exception as e:
            last_error = e
            if attempt < attempts:
                time.sleep(delay)
    raise last_error


def fetch(url: str) -> str:
    return request_with_retry(url).text


def clean_text(el) -> str:
    return " ".join(el.get_text(" ", strip=True).split())


def parse_ad(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    title_el = soup.select_one("h1")
    title = clean_text(title_el) if title_el else None

    web_id_el = soup.select_one(".web-id")
    web_id = clean_text(web_id_el).replace("WebID:", "").strip() if web_id_el else None

    date_el = soup.select_one(".date")
    date_text = clean_text(date_el).replace("Datum:", "").strip() if date_el else None

    attrs = {}
    for row in soup.select("table.attrs tr"):
        th = row.select_one("th[data-name-id]")
        td = row.select_one("td")
        if th and td:
            key = th.get("data-name-id")
            attrs[key] = clean_text(td)

    services = [clean_text(li) for li in soup.select("ul.bullets-two-cols li")]

    desc_el = soup.select_one("p.ad-desc")
    description = clean_text(desc_el) if desc_el else None

    phone_el = soup.select_one("a.phone-link")
    phone = phone_el.get("href", "").replace("tel:", "") if phone_el else None

    photo_urls = []
    main_img = soup.select_one("img.carousel-detail")
    if main_img and main_img.get("data-full"):
        photo_urls.append(main_img["data-full"])

    for a in soup.select("ul.thumbnails li a[href]"):
        href = a.get("href")
        if href and href not in photo_urls:
            photo_urls.append(href)

    return {
        "source_url": url,
        "web_id": web_id,
        "title": title,
        "date_posted": date_text,
        "attributes": attrs,
        "services": services,
        "description": description,
        "phone": phone,
        "photo_urls": photo_urls,
        "downloaded_at": datetime.now().isoformat(timespec="seconds"),
    }


def save_ad(data: dict, ad_id: str) -> Path:
    ad_dir = OUTPUT_DIR / ad_id
    ad_dir.mkdir(parents=True, exist_ok=True)

    with (ad_dir / "data.json").open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    for i, photo_url in enumerate(data["photo_urls"], start=1):
        ext = Path(urlparse(photo_url).path).suffix or ".jpg"
        photo_path = ad_dir / f"foto_{i}{ext}"
        if photo_path.exists():
            continue
        resp = request_with_retry(photo_url)
        photo_path.write_bytes(resp.content)

    return ad_dir


def update_index(data: dict, ad_id: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    is_new = not INDEX_FILE.exists()

    existing_rows = []
    if not is_new:
        with INDEX_FILE.open(encoding="utf-8", newline="") as f:
            existing_rows = list(csv.DictReader(f))
    existing_rows = [r for r in existing_rows if r["ad_id"] != ad_id]

    attrs = data["attributes"]
    existing_rows.append({
        "ad_id": ad_id,
        "title": data["title"] or "",
        "city": attrs.get("location_city", ""),
        "age": attrs.get("age", ""),
        "height": attrs.get("height", ""),
        "weigh": attrs.get("weigh", ""),
        "breast": attrs.get("breast", ""),
        "services": "; ".join(data.get("services") or []),
        "description": data.get("description") or "",
        "phone": data["phone"] or "",
        "date_posted": data["date_posted"] or "",
        "downloaded_at": data["downloaded_at"],
        "source_url": data["source_url"],
    })

    fieldnames = [
        "ad_id", "title", "city", "age", "height", "weigh", "breast",
        "services", "description", "phone", "date_posted", "downloaded_at", "source_url",
    ]
    with INDEX_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_rows)


def download_one(url: str) -> tuple[str, dict]:
    """Stahne, rozparsuje a ulozi jeden inzerat. Pouziva jak CLI (main), tak web app."""
    ad_id = ad_id_from_url(url)
    html = fetch(url)
    data = parse_ad(html, url)
    save_ad(data, ad_id)
    update_index(data, ad_id)
    return ad_id, data


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    urls = load_urls(sys.argv[1:])
    print(f"Nalezeno {len(urls)} URL ke zpracovani.")

    for i, url in enumerate(urls, start=1):
        try:
            print(f"[{i}/{len(urls)}] Stahuji {url} ...")
            ad_id, _data = download_one(url)
            print(f"    -> ulozeno do {OUTPUT_DIR / ad_id}")
        except Exception as e:
            print(f"    !! chyba u {url}: {e}")

        if i < len(urls):
            time.sleep(REQUEST_DELAY_SECONDS)

    print(f"\nHotovo. Prehled: {INDEX_FILE}")


if __name__ == "__main__":
    main()
