#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
birlestir_ve_denetle.py — Paralel Tercüme Sayfalarını Denetleme, Birleştirme ve HTML Kitapçık Üretici
=====================================================================================================
Kullanım:
  python scripts/birlestir_ve_denetle.py ./proje_ciktisi --title "Risâle fi'l-Kelâm — Tahkikli Tercüme"
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


UNCERTAIN_PATTERN = re.compile(r"(\[\.\.\.[^\]]*\]|\[[^\]\n]{1,40}\?\]|\(!\))")


def esc(text: str) -> str:
    return html.escape(text or "", quote=True)


def parse_glossary_terms(glossary_text: str) -> list[dict]:
    terms: list[dict] = []
    for line in glossary_text.splitlines():
        line = line.strip()
        if not line.startswith("|") or "---" in line or "Asıl İbare" in line:
            continue
        cols = [c.strip().strip("`") for c in line.strip("|").split("|")]
        if len(cols) >= 4 and cols[0]:
            terms.append({
                "ibare": cols[0],
                "transkripsiyon": cols[1],
                "karsilik": cols[2],
                "not": cols[3],
            })
    return terms


def build_interactive_html(title: str, pages: list[dict], terms: list[dict], flags: list[dict]) -> str:
    page_cards = ""
    for p in pages:
        page_cards += f"""
        <article class="page-card" id="sayfa-{p['no']}">
          <div class="page-head">
            <span class="badge">Sayfa {p['no']}</span>
            <span class="muted">{esc(p['dosya'])}</span>
          </div>
          <pre class="md-block">{esc(p['icerik'])}</pre>
        </article>
        """

    term_rows = ""
    for t in terms:
        term_rows += f"""
        <tr class="filter-row">
          <td class="rtl">{esc(t['ibare'])}</td>
          <td><strong>{esc(t['transkripsiyon'])}</strong></td>
          <td>{esc(t['karsilik'])}</td>
          <td>{esc(t['not'])}</td>
        </tr>
        """

    flag_rows = ""
    for f in flags:
        flag_rows += f"""
        <tr>
          <td><a href="#sayfa-{f['sayfa']}">Sayfa {f['sayfa']}</a></td>
          <td><code>{esc(f['isaret'])}</code></td>
          <td>{esc(f['baglam'])}</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<style>
  :root {{
    --bg: #f7f4ec; --card: #ffffff; --ink: #1e252c; --accent: #1d4e4a;
    --gold: #9a6b2f; --border: #dfd6c5; --muted: #5f6973;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: "Segoe UI", system-ui, sans-serif; background: var(--bg); color: var(--ink); line-height: 1.65; }}
  header {{ background: linear-gradient(135deg, #163836, #264653); color: #fff; padding: 26px 20px; border-bottom: 4px solid var(--gold); }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 0 16px; }}
  header h1 {{ margin: 0 0 6px; font-family: Georgia, serif; font-size: 1.65rem; }}
  header p {{ margin: 0; opacity: .9; font-size: .95rem; }}
  .toolbar {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 18px 0; padding: 12px; background: var(--card); border: 1px solid var(--border); border-radius: 10px; }}
  .tab-btn {{ border: 1px solid var(--border); background: #faf7f0; padding: 8px 14px; border-radius: 7px; cursor: pointer; font-weight: 600; }}
  .tab-btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  .panel {{ display: none; }}
  .panel.active {{ display: block; }}
  .card, .page-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px; margin-bottom: 14px; }}
  .page-card {{ border-left: 4px solid var(--gold); }}
  .page-head {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
  .badge {{ background: var(--accent); color: #fff; padding: 2px 10px; border-radius: 99px; font-size: .8rem; font-weight: 600; }}
  .muted {{ color: var(--muted); font-size: .88rem; }}
  .md-block {{ white-space: pre-wrap; font-family: Georgia, "Amiri", serif; font-size: 1rem; margin: 0; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .92rem; }}
  th, td {{ padding: 9px 10px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }}
  th {{ background: #f2ecdf; }}
  .rtl {{ direction: rtl; font-family: "Amiri", "Traditional Arabic", serif; font-size: 1.25rem; }}
  .search {{ width: 100%; max-width: 360px; padding: 8px 12px; margin-bottom: 12px; border: 1px solid var(--border); border-radius: 7px; }}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <h1>{esc(title)}</h1>
    <p>Paralel Alt-Ajan Tahkikli Tercüme • Ortak Terim Sözlüğü ({len(terms)} ıstılah) • Şerh Denetimi ({len(flags)} kayıt)</p>
  </div>
</header>
<main class="wrap">
  <div class="toolbar">
    <button class="tab-btn active" onclick="showTab('t-pages', this)">Sayfa Sayfa Tercüme ({len(pages)})</button>
    <button class="tab-btn" onclick="showTab('t-glossary', this)">Ortak Terim Sözlüğü ({len(terms)})</button>
    <button class="tab-btn" onclick="showTab('t-flags', this)">Şerh &amp; Kontrol Noktaları ({len(flags)})</button>
  </div>
  <section id="t-pages" class="panel active">{page_cards or '<div class="card">Henüz çevrilmiş sayfa bulunamadı.</div>'}</section>
  <section id="t-glossary" class="panel card">
    <input class="search" type="search" placeholder="Istılah veya Türkçe karşılık ara..." oninput="filterRows(this.value)">
    <table id="tbl-terms">
      <thead><tr><th>Asıl İbare</th><th>Transkripsiyon</th><th>Onaylı Türkçe Karşılık</th><th>Not</th></tr></thead>
      <tbody>{term_rows or '<tr><td colspan="4">Terim kaydı yok.</td></tr>'}</tbody>
    </table>
  </section>
  <section id="t-flags" class="panel card">
    <table>
      <thead><tr><th>Sayfa</th><th>Şerh İşareti</th><th>Metin Bağlamı</th></tr></thead>
      <tbody>{flag_rows or '<tr><td colspan="3">Açık şerh veya şüpheli okuma işareti bulunmadı.</td></tr>'}</tbody>
    </table>
  </section>
</main>
<script>
function showTab(id, btn) {{
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}}
function filterRows(q) {{
  const s = q.trim().toLowerCase();
  document.querySelectorAll('#tbl-terms tbody tr.filter-row').forEach(r => {{
    r.style.display = r.innerText.toLowerCase().includes(s) ? '' : 'none';
  }});
}}
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Paralel çeviri sayfalarını birleştirir ve tutarlılık raporu üretir.")
    parser.add_argument("project_dir", help="yazma_hazirla.py tarafından oluşturulan proje klasörü")
    parser.add_argument("--title", default="Yazma Eser Tahkikli Tercüme ve Terim Sözlüğü", help="Çıktı başlığı")
    args = parser.parse_args()

    proj = Path(args.project_dir).resolve()
    cev_dir = proj / "ceviriler"
    glossary_path = proj / "glossary.md"
    manifest_path = proj / "manifest.json"

    expected_total = 0
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_total = int(manifest.get("toplam_sayfa", 0))

    md_files = sorted(cev_dir.glob("sayfa_*.md")) if cev_dir.exists() else []
    pages: list[dict] = []
    found_nums: set[int] = set()
    flags: list[dict] = []

    for f in md_files:
        m = re.search(r"(\d+)", f.stem)
        pno = int(m.group(1)) if m else len(pages) + 1
        found_nums.add(pno)
        content = f.read_text(encoding="utf-8").strip()
        pages.append({"no": pno, "dosya": f.name, "icerik": content})
        for line in content.splitlines():
            for hit in UNCERTAIN_PATTERN.findall(line):
                flags.append({"sayfa": pno, "isaret": hit, "baglam": line.strip()[:180]})

    pages.sort(key=lambda x: x["no"])
    missing = [i for i in range(1, expected_total + 1) if i not in found_nums] if expected_total else []

    glossary_text = glossary_path.read_text(encoding="utf-8") if glossary_path.exists() else ""
    terms = parse_glossary_terms(glossary_text)

    combined_md = [f"# {args.title}\n"]
    for p in pages:
        combined_md.append(f"\n---\n\n<!-- Sayfa {p['no']} -->\n{p['icerik']}\n")
    out_md = proj / "tam_metin_tercume.md"
    out_md.write_text("\n".join(combined_md), encoding="utf-8")

    report_lines = [
        f"# Tutarlılık ve Tahkik Denetim Raporu — {args.title}",
        "",
        f"- **Tamamlanan Sayfa Sayısı:** {len(pages)}" + (f" / {expected_total}" if expected_total else ""),
        f"- **Eksik Sayfalar:** {', '.join(map(str, missing)) if missing else 'Yok (Tamamı çevrildi)'}",
        f"- **Ortak Sözlükteki (`glossary.md`) Onaylı Istılah Sayısı:** {len(terms)}",
        f"- **Şerh / Şüpheli Okuma (`[...]`, `[kelime?]`, `(!)`) Kaydı:** {len(flags)}",
        "",
        "## Şerh ve Kontrol Noktaları Özeti",
    ]
    if flags:
        for fl in flags:
            report_lines.append(f"- **Sayfa {fl['sayfa']}** `{fl['isaret']}` → {fl['baglam']}")
    else:
        report_lines.append("- Açık şerh işareti bulunmamaktadır.")

    out_report = proj / "denetim_raporu.md"
    out_report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    out_html = proj / "tercume_kitapcigi.html"
    out_html.write_text(build_interactive_html(args.title, pages, terms, flags), encoding="utf-8")

    print(f"Birleştirilen Metin : {out_md}")
    print(f"Denetim Raporu      : {out_report}")
    print(f"İnteraktif Kitapçık : {out_html}")


if __name__ == "__main__":
    main()
