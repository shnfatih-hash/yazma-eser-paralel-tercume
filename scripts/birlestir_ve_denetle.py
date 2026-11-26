#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
birlestir_ve_denetle.py — Paralel Tercüme Sayfalarını Denetleme, Birleştirme ve HTML Kitapçık Üretici
=====================================================================================================
Çıktılar:
  1) tam_metin_tercume.md       — Atıflı Akademik Tahkik Nüshası ([vr. Xa] ve şerh aparatı korunur)
  2) tam_metin_akici_okuma.md   — Kesintisiz Akıcı Saf Okuma Metni (sayfa/varak başlıkları ve rekabe
                                  kesintileri arındırılmış, bölünmüş paragrafları birleştirilmiş metin)
  3) denetim_raporu.md          — Eksik sayfa, ıstılah sıklığı ve şüpheli okuma ([...], [kelime?], (!)) raporu
  4) tercume_kitapcigi.html     — Tahkikli Görünüm + Kesintisiz Akıcı Okuma + Sözlük + Şerh sekmeli HTML kitapçık

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
HARAKAT_AND_CTRL_RE = re.compile(r"[\u064B-\u065F\u0670\u0640\u200C\u200D]")

# Varak / sayfa işaretleri (akıcı saf okuma çıktısında temizlenir; [Mü'min: 55] gibi referanslara dokunmaz)
FOLIO_HEADING_RE = re.compile(
    r"^\s*#{1,4}\s*(?:Sayfa|SAYFA|Page|PAGE|Varak|VARAK|vr\.?)\s*\d+[abAB]?(?:\s*[—\-:•].*)?$",
    re.IGNORECASE,
)
INLINE_FOLIO_MARKER_RE = re.compile(
    r"\[(?:vr\.?|varak|sayfa|page)\s*\d+\s*[abAB]?(?:\s*[-–]\s*\d+[abAB]?)?\]",
    re.IGNORECASE,
)
BARE_PAGE_LINE_RE = re.compile(
    r"^\s*(?:SAYFA|Sayfa|PAGE|Page|VARAK|Varak|vr\.?)\s+\d+[abAB]?\s*$"
)
REKABE_TAG_RE = re.compile(r"\[?\s*(?:Rekabe|Müş['‘]ir(?:\s+kelime)?)\s*:[^\n\]]*\]?", re.IGNORECASE)
SAHH_INLINE_RE = re.compile(r"\[([^\[\]\n]+?)\s*\(sahh\)\]", re.IGNORECASE)
ANGLE_OR_GUILLEMET_QUOTE_RE = re.compile(r"(?:«([^»\n]+)»|﴿([^﴾\n]+)﴾|\{([^\}\n]+)\})")
TERMINAL_PUNCT_RE = re.compile(r'[.!?…:"”\')\]»]\s*$')


def normalize_ottoman_arabic(text: str) -> str:
    """
    Arapça ve Osmanlıca/Farsça klavye/kaynak kodlamaları arasındaki Ye, Kef,
    Sağır Kef, Elif ve hareke/ZWNJ farklarını kanonik biçimde eşitler.
    """
    if not text:
        return ""
    s = HARAKAT_AND_CTRL_RE.sub("", text)
    s = (
        s.replace("\u064a", "\u06cc")  # Arabic Yeh (ي) -> Farsi/Ottoman Yeh (ی)
        .replace("\u0649", "\u06cc")   # Alef Maksura (ى) -> Farsi/Ottoman Yeh (ی)
        .replace("\u0643", "\u06a9")   # Arabic Kaf (ك) -> Keheh (ک)
        .replace("\u06af", "\u06a9")   # Gaf (گ) -> Keheh (ک)
        .replace("\u06ad", "\u06a9")   # Sağır Kef (ڭ) -> Keheh (ک) esnek arama için
        .replace("\u0623", "\u0627")   # أ -> ا
        .replace("\u0625", "\u0627")   # إ -> ا
        .replace("\u0622", "\u0627")   # آ -> ا
    )
    return " ".join(s.split())


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


def _normalize_quotes_preserving_citations(text: str) -> str:
    """
    Kaynak metindeki «...», ﴿...﴾ ve {...} ayraçlarını çift tırnağa ("...") çevirir;
    [Mü'min: 55], (Buhârî, 12), [...] ve [kelime?] gibi referans ve şerh ayraçlarına dokunmaz.
    """
    def _repl(m: re.Match) -> str:
        inner = m.group(1) or m.group(2) or m.group(3) or ""
        return f'"{inner.strip()}"'

    return ANGLE_OR_GUILLEMET_QUOTE_RE.sub(_repl, text)


def _extract_translation_slice(page_md: str) -> str:
    """
    Standart şablonlu sayfa dosyalarından yalnızca Türkçe tercüme ve derkenar/minhü
    katmanlarını alır; künye, Arapça/Osmanlıca asıl metin ve yeni terim adayları tablolarını ayıklar.
    Şablonsuz düz çeviri sayfalarında ise tüm metni koruyarak yalnızca varak başlıklarını temizler.
    """
    lines = page_md.splitlines()
    has_structured_sections = any(
        re.match(r"^\s*#{2,3}\s*(?:Akademik Türkçe Tercüme|Türkçe Tercüme|Tercüme)\b", ln, re.IGNORECASE)
        for ln in lines
    )

    kept: list[str] = []
    mode = "keep" if not has_structured_sections else "skip"

    for raw_ln in lines:
        ln = raw_ln.rstrip()
        if FOLIO_HEADING_RE.match(ln) or BARE_PAGE_LINE_RE.match(ln):
            continue
        sec_m = re.match(r"^\s*#{2,3}\s+(.+?)\s*$", ln)
        if sec_m:
            sec_title = sec_m.group(1).lower()
            if any(k in sec_title for k in ("türkçe tercüme", "akademik türkçe", "tercüme", "çeviri")):
                mode = "keep"
                continue
            if any(k in sec_title for k in ("derkenar", "hâmiş", "hamiş", "minhü", "minhu")):
                mode = "notes"
                continue
            if any(
                k in sec_title
                for k in ("künye", "varak durumu", "asıl metin", "orijinal metin", "yeni terim", "kritik aparat", "şerh ve kritik")
            ):
                mode = "skip"
                continue

        if mode == "skip":
            continue
        if mode == "notes":
            stripped = ln.strip().lstrip("-* ").strip()
            if not stripped or "yoktur" in stripped.lower() or "bulunmamaktadır" in stripped.lower():
                continue
            if not stripped.lower().startswith(("derkenar notu:", "minhü notu:", "not:")):
                kept.append(f"Derkenar Notu: {stripped}")
            else:
                kept.append(stripped)
            continue

        kept.append(ln)

    cleaned = "\n".join(kept)
    cleaned = INLINE_FOLIO_MARKER_RE.sub("", cleaned)
    cleaned = REKABE_TAG_RE.sub("", cleaned)
    cleaned = SAHH_INLINE_RE.sub(r"\1", cleaned)
    cleaned = _normalize_quotes_preserving_citations(cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def build_clean_reading_text(pages: list[dict]) -> str:
    """
    Sayfa/varak kesintilerini ve rekabe tekrarlarını kaldırır; sayfa geçişi yüzünden
    ikiye bölünen cümle ve paragrafları tek bir akıcı paragraf halinde birleştirir.
    Yarım kalan cümlenin bulunduğu sayfadaki derkenar/minhü notlarını cümlenin ortasına
    sokmaz; birleştirilen paragraf tamamlandığında hemen altına yerleştirir.
    """
    paragraphs: list[str] = []
    deferred_notes: list[str] = []

    def _is_note(blk: str) -> bool:
        return blk.startswith(("Derkenar Notu:", "Minhü Notu:", "Not:"))

    def _has_open_body_para() -> bool:
        return (
            bool(paragraphs)
            and not _is_note(paragraphs[-1])
            and not paragraphs[-1].startswith(("#", ">", "-", "*"))
            and not TERMINAL_PUNCT_RE.search(paragraphs[-1])
        )

    for p in pages:
        chunk = _extract_translation_slice(p.get("icerik", ""))
        if not chunk:
            continue
        page_paras = [blk.strip() for blk in re.split(r"\n\s*\n", chunk) if blk.strip()]
        for para in page_paras:
            if _is_note(para):
                if _has_open_body_para():
                    deferred_notes.append(para)
                else:
                    paragraphs.append(para)
                continue

            is_heading_or_list = para.startswith(("#", ">", "-", "*"))
            if not is_heading_or_list and _has_open_body_para():
                # Rekabe (müş'ir kelime) tekrarı varsa otomatik düşür
                prev_words = paragraphs[-1].split()
                curr_words = para.split()
                if prev_words and curr_words:
                    last_w = prev_words[-1].strip('.,;:!?"”\'()[]').lower()
                    first_w = curr_words[0].strip('.,;:!?"”\'()[]').lower()
                    if len(last_w) >= 3 and last_w == first_w:
                        para = " ".join(curr_words[1:])
                paragraphs[-1] = f"{paragraphs[-1].rstrip()} {para.lstrip()}".strip()
            else:
                if deferred_notes:
                    paragraphs.extend(deferred_notes)
                    deferred_notes.clear()
                paragraphs.append(para)

            if deferred_notes and not _has_open_body_para():
                paragraphs.extend(deferred_notes)
                deferred_notes.clear()

    if deferred_notes:
        paragraphs.extend(deferred_notes)

    return "\n\n".join(paragraphs).strip()


def build_interactive_html(
    title: str,
    pages: list[dict],
    terms: list[dict],
    flags: list[dict],
    clean_text: str | None = None,
) -> str:
    if clean_text is None:
        clean_text = build_clean_reading_text(pages)

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

    clean_paras_html = ""
    if clean_text:
        for blk in clean_text.split("\n\n"):
            b = blk.strip()
            if not b:
                continue
            if b.startswith(("Derkenar Notu:", "Minhü Notu:", "Not:")):
                clean_paras_html += f'<div class="inline-note">{esc(b)}</div>\n'
            elif b.startswith("#"):
                clean_paras_html += f'<h3>{esc(b.lstrip("# ").strip())}</h3>\n'
            else:
                clean_paras_html += f"<p>{esc(b)}</p>\n"

    term_rows = ""
    for t in terms:
        term_rows += f"""
        <tr class="filter-row">
          <td class="rtl">{esc(t['ibare'])}</td>
          <td><strong>{esc(t['transkripsiyon'])}</strong></td>
          <td>{esc(t['karsilik'])}</td>
          <td>{t.get('gecis_sayisi', 0)} sayfa</td>
          <td>{esc(t['not'])}</td>
        </tr>
        """

    flag_rows = ""
    for f in flags:
        flag_rows += f"""
        <tr>
          <td><a href="#sayfa-{f['sayfa']}" onclick="jumpToPage('sayfa-{f['sayfa']}')">Sayfa {f['sayfa']}</a></td>
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
  body {{ margin: 0; font-family: "Segoe UI", system-ui, sans-serif; background: var(--bg); color: var(--ink); line-height: 1.7; }}
  header {{ background: linear-gradient(135deg, #163836, #264653); color: #fff; padding: 26px 20px; border-bottom: 4px solid var(--gold); }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 0 16px; }}
  header h1 {{ margin: 0 0 6px; font-family: Georgia, serif; font-size: 1.65rem; }}
  header p {{ margin: 0; opacity: .9; font-size: .95rem; }}
  .toolbar {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; justify-content: space-between; margin: 18px 0; padding: 12px; background: var(--card); border: 1px solid var(--border); border-radius: 10px; }}
  .tab-group {{ display: flex; gap: 8px; flex-wrap: wrap; }}
  .tab-btn {{ border: 1px solid var(--border); background: #faf7f0; padding: 8px 14px; border-radius: 7px; cursor: pointer; font-weight: 600; }}
  .tab-btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  .copy-btn {{ border: 1px solid var(--gold); background: #fff9eb; color: #6b4611; padding: 7px 13px; border-radius: 7px; cursor: pointer; font-weight: 600; font-size: .88rem; }}
  .panel {{ display: none; }}
  .panel.active {{ display: block; }}
  .card, .page-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px; margin-bottom: 14px; }}
  .page-card {{ border-left: 4px solid var(--gold); }}
  .page-head {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
  .badge {{ background: var(--accent); color: #fff; padding: 2px 10px; border-radius: 99px; font-size: .8rem; font-weight: 600; }}
  .muted {{ color: var(--muted); font-size: .88rem; }}
  .md-block {{ white-space: pre-wrap; font-family: Georgia, "Amiri", serif; font-size: 1rem; margin: 0; }}
  .clean-reader {{ font-family: Georgia, "Times New Roman", serif; font-size: 1.07rem; line-height: 1.85; padding: 24px 28px; }}
  .clean-reader p {{ margin: 0 0 14px; text-align: justify; }}
  .clean-reader h3 {{ color: var(--accent); margin: 18px 0 10px; }}
  .inline-note {{ background: #faf5e8; border-left: 3px solid var(--gold); padding: 9px 14px; margin: 8px 0 14px; font-size: .94rem; color: #3c3426; border-radius: 4px; }}
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
    <p>Paralel Alt-Ajan Tahkikli Tercüme • Kesintisiz Akıcı Okuma Modu • Ortak Terim Sözlüğü ({len(terms)} ıstılah) • Şerh Denetimi ({len(flags)} kayıt)</p>
  </div>
</header>
<main class="wrap">
  <div class="toolbar">
    <div class="tab-group">
      <button class="tab-btn active" id="btn-pages" onclick="showTab('t-pages', this)">Sayfa Sayfa Tahkik ({len(pages)})</button>
      <button class="tab-btn" id="btn-clean" onclick="showTab('t-clean', this)">Kesintisiz Akıcı Okuma (Saf Metin)</button>
      <button class="tab-btn" id="btn-glossary" onclick="showTab('t-glossary', this)">Ortak Terim Sözlüğü ({len(terms)})</button>
      <button class="tab-btn" id="btn-flags" onclick="showTab('t-flags', this)">Şerh &amp; Kontrol Noktaları ({len(flags)})</button>
    </div>
  </div>
  <section id="t-pages" class="panel active">{page_cards or '<div class="card">Henüz çevrilmiş sayfa bulunamadı.</div>'}</section>
  <section id="t-clean" class="panel card clean-reader">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:14px; padding-bottom:10px; border-bottom:1px solid var(--border);">
      <span class="muted">Varak/sayfa işaretleri ve rekabe tekrarları kaldırılmış, bölünmüş paragrafları birleştirilmiş saf okuma metni:</span>
      <button class="copy-btn" onclick="copyCleanText(this)">📋 Saf Metni Kopyala</button>
    </div>
    <div id="clean-body">{clean_paras_html or '<p class="muted">Henüz çevrilmiş metin bulunamadı.</p>'}</div>
    <textarea id="raw-clean-text" style="display:none;">{esc(clean_text)}</textarea>
  </section>
  <section id="t-glossary" class="panel card">
    <input class="search" type="search" placeholder="Istılah veya Türkçe karşılık ara (ي/ی ve ك/ک/ڭ uyumlu)..." oninput="filterRows(this.value)">
    <table id="tbl-terms">
      <thead><tr><th>Asıl İbare</th><th>Transkripsiyon</th><th>Onaylı Türkçe Karşılık</th><th>Metinde Geçiş</th><th>Not</th></tr></thead>
      <tbody>{term_rows or '<tr><td colspan="5">Terim kaydı yok.</td></tr>'}</tbody>
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
function normOsm(str) {{
  return (str || '').toLowerCase()
    .replace(/[\u064B-\u065F\u0670\u0640\u200C\u200D]/g, '')
    .replace(/[\u064a\u0649]/g, '\u06cc')
    .replace(/[\u0643\u06af\u06ad]/g, '\u06a9')
    .replace(/[â]/g, 'a').replace(/[î]/g, 'i').replace(/[û]/g, 'u');
}}
function showTab(id, btn) {{
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}}
function jumpToPage(anchorId) {{
  showTab('t-pages', document.getElementById('btn-pages'));
  const el = document.getElementById(anchorId);
  if (el) el.scrollIntoView({{ behavior: 'smooth' }});
}}
function copyCleanText(btn) {{
  const raw = document.getElementById('raw-clean-text').value;
  navigator.clipboard.writeText(raw);
  const prev = btn.textContent;
  btn.textContent = '✓ Kopyalandı!';
  setTimeout(() => btn.textContent = prev, 2200);
}}
function filterRows(q) {{
  const s = normOsm(q.trim());
  document.querySelectorAll('#tbl-terms tbody tr.filter-row').forEach(r => {{
    r.style.display = normOsm(r.innerText).includes(s) ? '' : 'none';
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

    # Kanonik Osmanlıca/Arapça Unicode eşitlemesi ile her ıstılahın kaç sayfada geçtiğini denetle
    norm_pages = [(p["no"], normalize_ottoman_arabic(p["icerik"]), p["icerik"].lower()) for p in pages]
    for t in terms:
        norm_ibare = normalize_ottoman_arabic(t["ibare"])
        karsilik_low = t["karsilik"].lower().split("(")[0].strip()
        hit_pages = [
            pno
            for pno, np_txt, low_txt in norm_pages
            if (norm_ibare and norm_ibare in np_txt) or (len(karsilik_low) >= 4 and karsilik_low in low_txt)
        ]
        t["gecis_sayisi"] = len(hit_pages)

    combined_md = [f"# {args.title}\n"]
    for p in pages:
        combined_md.append(f"\n---\n\n<!-- Sayfa {p['no']} -->\n{p['icerik']}\n")
    out_md = proj / "tam_metin_tercume.md"
    out_md.write_text("\n".join(combined_md), encoding="utf-8")

    clean_reading_text = build_clean_reading_text(pages)
    out_clean_md = proj / "tam_metin_akici_okuma.md"
    out_clean_md.write_text(f"# {args.title}\n\n{clean_reading_text}\n", encoding="utf-8")

    report_lines = [
        f"# Tutarlılık ve Tahkik Denetim Raporu — {args.title}",
        "",
        f"- **Tamamlanan Sayfa Sayısı:** {len(pages)}" + (f" / {expected_total}" if expected_total else ""),
        f"- **Eksik Sayfalar:** {', '.join(map(str, missing)) if missing else 'Yok (Tamamı çevrildi)'}",
        f"- **Ortak Sözlükteki (`glossary.md`) Onaylı Istılah Sayısı:** {len(terms)}",
        f"- **Şerh / Şüpheli Okuma (`[...]`, `[kelime?]`, `(!)`) Kaydı:** {len(flags)}",
        f"- **Üretilen Çıktılar:** `tam_metin_tercume.md` (Atıflı Tahkik) • `tam_metin_akici_okuma.md` (Varaksız Saf Metin) • `tercume_kitapcigi.html`",
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
    out_html.write_text(build_interactive_html(args.title, pages, terms, flags, clean_reading_text), encoding="utf-8")

    print(f"Atıflı Tahkik Metni : {out_md}")
    print(f"Akıcı Saf Okuma     : {out_clean_md}")
    print(f"Denetim Raporu      : {out_report}")
    print(f"İnteraktif Kitapçık : {out_html}")


if __name__ == "__main__":
    main()
