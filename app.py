#!/usr/bin/env python3
"""
Jednoduche webove rozhrani pro osobni archiv inzeratu z annonce.cz.

Spusteni:
    python app.py
(automaticky se otevre v prohlizeci na http://127.0.0.1:5000)
"""

import csv
import json
import re
from pathlib import Path

from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string

from download_ads import OUTPUT_DIR, INDEX_FILE, download_one

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Archiv inzeratu - annonce.cz</title>
<style>
  body { font-family: sans-serif; max-width: 1200px; margin: 2rem auto; padding: 0 1rem; color: #222; }
  h1 { font-size: 1.4rem; }
  textarea { width: 100%; height: 120px; font-family: monospace; }
  button { padding: 0.5rem 1.2rem; font-size: 1rem; margin-top: 0.5rem; cursor: pointer; }
  table { border-collapse: collapse; width: 100%; margin-top: 1.5rem; }
  th, td { border: 1px solid #ddd; padding: 0.4rem 0.6rem; text-align: left; font-size: 0.9rem; }
  th { background: #f5f5f5; }
  img.thumb { height: 180px; border-radius: 6px; display: block; }
  .log { background: #f0f0f0; padding: 1rem; white-space: pre-wrap; font-family: monospace; margin-top: 1rem; }
  .ok { color: #1a7f37; }
  .err { color: #c0392b; }
  a { color: #0366d6; }
  .services-filter { display: flex; flex-wrap: wrap; gap: 0.3rem 1rem; background: #f5f5f5; padding: 0.8rem; border-radius: 6px; max-height: 180px; overflow-y: auto; }
  .services-filter label { font-size: 0.85rem; white-space: nowrap; }
  .services-form button { margin-right: 0.8rem; }
</style>
</head>
<body>
  <h1>Osobni archiv inzeratu (annonce.cz)</h1>
  <p>Vlozte URL adresy inzeratu, ktere jste si sami vybrali (jedna na radek), a stisknete Stahnout.</p>
  <form method="post" action="{{ url_for('download') }}">
    <textarea name="urls" placeholder="https://www.annonce.cz/inzerat/...&#10;https://www.annonce.cz/inzerat/..."></textarea>
    <br>
    <button type="submit">Stahnout</button>
  </form>

  {% if log %}
  <div class="log">{% for line in log %}{{ line }}
{% endfor %}</div>
  {% endif %}

  {% if rows_exist %}
  <h3>Filtrovat</h3>
  <form method="get" action="{{ url_for('index') }}" class="services-form">
    <input type="hidden" name="sort" value="{{ sort }}">
    <input type="hidden" name="dir" value="{{ dir }}">
    <p>
      <input type="text" name="q" value="{{ query }}" placeholder="hledat v nazvu/popisu, napr. asie, exotika, MILF...">
    </p>
    {% if all_services %}
    <div class="services-filter">
      {% for s in all_services %}
      <label><input type="checkbox" name="service" value="{{ s }}" {% if s in selected_services %}checked{% endif %}> {{ s }}</label>
      {% endfor %}
    </div>
    {% endif %}
    <button type="submit">Filtrovat</button>
    {% if selected_services or query %}<a href="{{ url_for('index', sort=sort, dir=dir) }}">Zrusit filtr</a>{% endif %}
  </form>
  {% endif %}

  <h2>Ulozene inzeraty ({{ rows|length }})</h2>
  {% if rows %}
  <table>
    <tr>
      <th>Foto</th>
      <th>{{ sort_link('title', 'Jmeno') | safe }}</th>
      <th>{{ sort_link('age', 'Vek') | safe }}</th>
      <th>{{ sort_link('city', 'Mesto') | safe }}</th>
      <th>{{ sort_link('weigh', 'Vaha') | safe }}</th>
      <th>{{ sort_link('services', 'Sluzby') | safe }}</th>
      <th>{{ sort_link('phone', 'Telefon') | safe }}</th>
      <th>{{ sort_link('downloaded_at', 'Ulozeno') | safe }}</th>
      <th></th>
    </tr>
    {% for row in rows %}
    <tr>
      <td>{% if row.thumb %}<img class="thumb" src="{{ url_for('photo', ad_id=row.ad_id, filename=row.thumb) }}">{% endif %}</td>
      <td>{{ row.title }}</td>
      <td>{{ row.age }}</td>
      <td>{{ row.city }}</td>
      <td>{{ row.weigh }}</td>
      <td>{{ row.services }}</td>
      <td>{{ row.phone }}</td>
      <td>{{ row.downloaded_at }}</td>
      <td><a href="{{ url_for('detail', ad_id=row.ad_id) }}">ulozena kopie</a></td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p><em>Zatim zadny ulozeny inzerat.</em></p>
  {% endif %}
</body>
</html>
"""

DETAIL_PAGE = """
<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>{{ data.title }} - ulozena kopie</title>
<style>
  body { font-family: sans-serif; max-width: 700px; margin: 2rem auto; padding: 0 1rem; color: #222; }
  h1 { font-size: 1.4rem; }
  .notice { background: #fff8e1; border: 1px solid #f0d98c; padding: 0.6rem 1rem; border-radius: 4px; margin-bottom: 1rem; font-size: 0.9rem; }
  .photos { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0; }
  .photos img { max-height: 260px; border-radius: 6px; cursor: zoom-in; }
  table { border-collapse: collapse; margin: 1rem 0; }
  th, td { border: 1px solid #ddd; padding: 0.3rem 0.6rem; text-align: left; font-size: 0.9rem; }
  .desc { white-space: pre-wrap; }
  .back { display: inline-block; margin-top: 1.5rem; }
  a { color: #0366d6; }

  .lightbox { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.9); z-index: 100; }
  .lightbox.open { display: flex; align-items: center; justify-content: center; }
  .lightbox img { max-width: 90vw; max-height: 90vh; border-radius: 6px; }
  .lightbox .close { position: absolute; top: 1rem; right: 1.5rem; color: #fff; font-size: 2rem; cursor: pointer; line-height: 1; }
  .lightbox .nav { position: absolute; top: 50%; transform: translateY(-50%); color: #fff; font-size: 3rem; cursor: pointer; user-select: none; padding: 0 1rem; }
  .lightbox .prev { left: 0.5rem; }
  .lightbox .next { right: 0.5rem; }
  .lightbox .counter { position: absolute; bottom: 1rem; left: 50%; transform: translateX(-50%); color: #fff; font-size: 0.9rem; }
</style>
</head>
<body>
  <p class="notice">Toto je vase lokalne ulozena kopie inzeratu ze dne {{ data.downloaded_at }}.
  Puvodni inzerat na annonce.cz uz nemusi existovat.
  <a href="{{ data.source_url }}" target="_blank">Zkusit otevrit puvodni inzerat</a>.</p>

  <h1>{{ data.title }}</h1>

  {% if photos %}
  <div class="photos">
    {% for p in photos %}
    <img src="{{ url_for('photo', ad_id=ad_id, filename=p) }}" onclick="openLightbox({{ loop.index0 }})">
    {% endfor %}
  </div>

  <div class="lightbox" id="lightbox" onclick="if(event.target===this) closeLightbox()">
    <span class="close" onclick="closeLightbox()">&times;</span>
    <span class="nav prev" onclick="showPhoto(-1)">&#10094;</span>
    <img id="lightbox-img" src="">
    <span class="nav next" onclick="showPhoto(1)">&#10095;</span>
    <span class="counter" id="lightbox-counter"></span>
  </div>

  <script>
    const photoUrls = [{% for p in photos %}"{{ url_for('photo', ad_id=ad_id, filename=p) }}"{% if not loop.last %}, {% endif %}{% endfor %}];
    let currentPhoto = 0;

    function openLightbox(i) {
      currentPhoto = i;
      renderPhoto();
      document.getElementById('lightbox').classList.add('open');
    }
    function closeLightbox() {
      document.getElementById('lightbox').classList.remove('open');
    }
    function showPhoto(delta) {
      currentPhoto = (currentPhoto + delta + photoUrls.length) % photoUrls.length;
      renderPhoto();
    }
    function renderPhoto() {
      document.getElementById('lightbox-img').src = photoUrls[currentPhoto];
      document.getElementById('lightbox-counter').textContent = (currentPhoto + 1) + ' / ' + photoUrls.length;
    }
    document.addEventListener('keydown', function(e) {
      if (!document.getElementById('lightbox').classList.contains('open')) return;
      if (e.key === 'Escape') closeLightbox();
      if (e.key === 'ArrowLeft') showPhoto(-1);
      if (e.key === 'ArrowRight') showPhoto(1);
    });
  </script>
  {% endif %}

  <table>
    {% for key, value in data.attributes.items() %}
    <tr><th>{{ key }}</th><td>{{ value }}</td></tr>
    {% endfor %}
    {% if data.services %}
    <tr><th>sluzby</th><td>{{ data.services | join(', ') }}</td></tr>
    {% endif %}
    {% if data.phone %}
    <tr><th>telefon</th><td>{{ data.phone }}</td></tr>
    {% endif %}
    {% if data.date_posted %}
    <tr><th>datum vystaveni</th><td>{{ data.date_posted }}</td></tr>
    {% endif %}
  </table>

  {% if data.description %}
  <p class="desc">{{ data.description }}</p>
  {% endif %}

  <a class="back" href="{{ url_for('index') }}">&larr; zpet na prehled</a>
</body>
</html>
"""


NUMERIC_SORT_FIELDS = {"age", "weigh", "height"}


def natural_key(value: str):
    parts = re.split(r"(\d+)", value or "")
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def leading_number(value: str):
    match = re.search(r"[\d]+(?:[.,]\d+)?", value or "")
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def row_services(row) -> list[str]:
    return [s.strip() for s in (row.get("services") or "").split(";") if s.strip()]


def read_index_rows(sort: str = "downloaded_at", direction: str = "desc"):
    if not INDEX_FILE.exists():
        return []
    with INDEX_FILE.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        ad_dir = OUTPUT_DIR / row["ad_id"]
        photos = sorted(ad_dir.glob("foto_1.*")) if ad_dir.exists() else []
        row["thumb"] = photos[0].name if photos else None

    def sort_key(row):
        value = row.get(sort, "") or ""
        if sort in NUMERIC_SORT_FIELDS:
            num = leading_number(value)
            if num is None:
                return (1, 0.0)
            return (0, num)
        if sort == "city":
            return (0, natural_key(value))
        return (0, value.lower())

    rows.sort(key=sort_key, reverse=(direction == "desc"))
    return rows


ALL_KNOWN_SERVICES = [
    "69", "Anál", "Autoerotika", "Bondage", "Clinic", "Doprovod", "Fisting",
    "Foot fetish", "Klasika", "Líbání", "Masáž", "Masáž prostaty", "Mazlení",
    "Online sex", "Orál", "Piss", "Sexy hrátky", "SM", "Squirt", "Striptýz",
]


def distinct_services(rows) -> list[str]:
    services = set(ALL_KNOWN_SERVICES)
    for row in rows:
        services.update(row_services(row))
    return sorted(services)


def make_sort_link(current_sort: str, current_dir: str):
    def sort_link(field: str, label: str) -> str:
        new_dir = "desc" if (current_sort == field and current_dir == "asc") else "asc"
        arrow = ""
        if current_sort == field:
            arrow = " ▲" if current_dir == "asc" else " ▼"
        url = url_for("index", sort=field, dir=new_dir)
        return f'<a href="{url}">{label}{arrow}</a>'
    return sort_link


@app.route("/")
def index():
    sort = request.args.get("sort", "downloaded_at")
    direction = request.args.get("dir", "desc")
    selected_services = request.args.getlist("service")
    query = request.args.get("q", "").strip()

    rows = read_index_rows(sort, direction)
    all_services = distinct_services(rows)
    rows_exist = bool(rows)

    if selected_services:
        wanted = set(selected_services)
        rows = [r for r in rows if wanted & set(row_services(r))]

    if query:
        q = query.lower()
        rows = [
            r for r in rows
            if q in (r.get("title", "") or "").lower()
            or q in (r.get("description", "") or "").lower()
        ]

    return render_template_string(
        PAGE,
        rows=rows,
        log=None,
        sort_link=make_sort_link(sort, direction),
        sort=sort,
        dir=direction,
        all_services=all_services,
        selected_services=selected_services,
        query=query,
        rows_exist=rows_exist,
    )


@app.route("/download", methods=["POST"])
def download():
    raw = request.form.get("urls", "")
    urls = [line.strip() for line in raw.splitlines() if line.strip()]
    log = [f"Nalezeno {len(urls)} URL ke zpracovani."]

    for i, url in enumerate(urls, start=1):
        try:
            ad_id, data = download_one(url)
            log.append(f"[{i}/{len(urls)}] OK: {data['title']} ({ad_id})")
        except Exception as e:
            log.append(f"[{i}/{len(urls)}] CHYBA u {url}: {e}")

    log.append("Hotovo.")
    rows = read_index_rows()
    return render_template_string(
        PAGE,
        rows=rows,
        log=log,
        sort_link=make_sort_link("downloaded_at", "desc"),
        sort="downloaded_at",
        dir="desc",
        all_services=distinct_services(rows),
        selected_services=[],
        query="",
        rows_exist=bool(rows),
    )


@app.route("/inzerat/<ad_id>")
def detail(ad_id):
    data_path = Path(OUTPUT_DIR) / ad_id / "data.json"
    if not data_path.exists():
        return f"Inzerat '{ad_id}' nebyl v archivu nalezen.", 404
    with data_path.open(encoding="utf-8") as f:
        data = json.load(f)
    photos = sorted(p.name for p in (Path(OUTPUT_DIR) / ad_id).glob("foto_*"))
    return render_template_string(DETAIL_PAGE, ad_id=ad_id, data=data, photos=photos)


@app.route("/foto/<ad_id>/<filename>")
def photo(ad_id, filename):
    return send_from_directory(Path(OUTPUT_DIR) / ad_id, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
