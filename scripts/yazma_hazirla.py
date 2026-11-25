#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yazma_hazirla.py — Çok Sayfalı Yazma Eser PDF / Görsel Hazırlama ve 10'lu Dalga Planlayıcı
==========================================================================================
Kullanım:
  python scripts/yazma_hazirla.py prepare eser.pdf --out ./proje_ciktisi --batch-size 10 --dpi 220
  python scripts/yazma_hazirla.py prepare ./varak_klasoru --out ./proje_ciktisi --split-folios
  python scripts/yazma_hazirla.py crop sayfa_001.png --box 0.1,0.2,0.9,0.35 --out kesit.png

Gereksinim:
  - Python 3.8+
  - Pillow (`pip install Pillow`)
  - PDF girdileri için PyMuPDF (`pip install pymupdf`)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Hata: 'Pillow' kurulu değil. Kurmak için: pip install Pillow")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}
MAX_ZIP_BYTES = 4 * 1024 ** 3
MAX_ZIP_FILES = 5000

GLOSSARY_TEMPLATE = """# Ortak Terim Sözlüğü ve Tercüme İlkeleri (`glossary.md`)

> **Koordinasyon Kuralı:** Paralel çalışan alt-ajanlar bu dosyayı **salt-okunur** okur ve buradaki karşılıklara birebir uyar. Yeni tespit edilen ıstılahlar her sayfa dosyasının sonundaki `## Yeni Terim Adayları` bölümüne yazılır; her 10'lu dalga sonunda Koordinatör tarafından bu tabloya eklenir.

## 1. Eser Künyesi ve Üslup Kuralları
- **Eser Adı:** [Aşama 1'de doldurulacak]
- **Müellif / Dönem:** [Aşama 1'de doldurulacak]
- **İlim Dalı:** [Kelâm / Fıkıh / Tasavvuf / Felsefe / Tarih vb.]
- **Hat Türü ve Nüsha Özellikleri:** [Nesih / Ta‘lîk / Rik‘a, satır sayısı, derkenar durumu]
- **Tercüme Üslubu:** Akademik, akıcı günümüz Türkçesi; teknik ıstılahların ilk geçtiği yerde parantez içinde özgün kavram gösterilir; varak/sayfa geçişleri `[Sayfa X]` olarak korunur; okunamayan yerler asla tahmin edilmez (`[...]`, `[kelime?]`).

## 2. Onaylı Istılahlar, Özel İsimler ve Kalıp İfadeler

| Asıl İbare (Arapça/Osmanlıca) | Transkripsiyon | Onaylı Türkçe Karşılık | Açıklama / Bağlam Notu | İlk Sayfa |
| :--- | :--- | :--- | :--- | :---: |
| `المصنف رحمه الله` | el-muṣannif raḥimehullâh | Müellif (Allah ona rahmet etsin) | Şerhlerde ana metin yazarını işaret eder | 1 |
| `قوله` | ḳavluhû | Müellifin "..." sözü | Şerh/hâşiye başlangıç ibaresi | 1 |
| `صح` | ṣaḥḥ | [Kenar tashihi: sahh] | Müstensihin kenardan metne eklediği doğrulama kaydı | - |
"""


def extract_pdf_to_images(pdf_path: Path, img_dir: Path, dpi: int) -> list[Path]:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        sys.exit("Hata: PDF'ten sayfa görüntüsü çıkarmak için PyMuPDF gerekli: pip install pymupdf")

    img_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    with fitz.open(pdf_path) as doc:
        for idx, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=mat, alpha=False)
            out_file = img_dir / f"sayfa_{idx:04d}.png"
            pix.save(str(out_file))
            saved.append(out_file)
    return saved


def collect_images_from_path(src: Path, work_dir: Path, dpi: int) -> list[Path]:
    img_out = work_dir / "_ham_sayfalar"
    if src.is_file():
        ext = src.suffix.lower()
        if ext == ".pdf":
            return extract_pdf_to_images(src, img_out, dpi)
        if ext == ".zip":
            img_out.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(src, "r") as zf:
                members = zf.infolist()
                if len(members) > MAX_ZIP_FILES or sum(m.file_size for m in members) > MAX_ZIP_BYTES:
                    raise ValueError("ZIP arşivi güvenlik sınırını aşıyor.")
                base = img_out.resolve()
                for m in members:
                    dest = (img_out / m.filename).resolve()
                    if os.path.commonpath([str(base), str(dest)]) != str(base):
                        raise ValueError(f"Güvensiz ZIP yolu reddedildi: {m.filename}")
                    zf.extract(m, img_out)
            return sorted(p for p in img_out.rglob("*") if p.suffix.lower() in IMAGE_EXTS)
        if ext in IMAGE_EXTS:
            return [src]
        raise ValueError(f"Desteklenmeyen dosya türü: {src}")

    if src.is_dir():
        return sorted(p for p in src.rglob("*") if p.suffix.lower() in IMAGE_EXTS)

    raise FileNotFoundError(f"Girdi bulunamadı: {src}")


def normalize_pages(raw_pages: list[Path], final_img_dir: Path, split_folios: bool) -> list[dict]:
    final_img_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    seq = 1
    for raw in raw_pages:
        with Image.open(raw) as im:
            im = im.convert("RGB")
            w, h = im.size
            if split_folios and w > h:
                # Arapça/Osmanlıca çift varaklı pozlarda önce Sağ sayfa, sonra Sol sayfa okunur
                halves = [
                    ("sag_varak", im.crop((int(w * 0.47), 0, w, h))),
                    ("sol_varak", im.crop((0, 0, int(w * 0.53), h))),
                ]
                for label, sub in halves:
                    out_name = f"sayfa_{seq:04d}.png"
                    out_path = final_img_dir / out_name
                    sub.save(out_path)
                    records.append({
                        "sayfa_no": seq,
                        "kaynak": f"{raw.name} ({label})",
                        "gorsel": str(out_path),
                        "boyut": [sub.width, sub.height],
                        "ceviri_dosyasi": f"ceviriler/sayfa_{seq:04d}.md",
                    })
                    seq += 1
            else:
                out_name = f"sayfa_{seq:04d}.png"
                out_path = final_img_dir / out_name
                im.save(out_path)
                records.append({
                    "sayfa_no": seq,
                    "kaynak": raw.name,
                    "gorsel": str(out_path),
                    "boyut": [w, h],
                    "ceviri_dosyasi": f"ceviriler/sayfa_{seq:04d}.md",
                })
                seq += 1
    return records


def cmd_prepare(args: argparse.Namespace) -> None:
    src = Path(args.input).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ceviriler").mkdir(exist_ok=True)
    (out_dir / "kesitler").mkdir(exist_ok=True)

    raw_pages = collect_images_from_path(src, out_dir, args.dpi)
    pages = normalize_pages(raw_pages, out_dir / "sayfa_gorselleri", args.split_folios)

    batch_size = max(1, int(args.batch_size))
    batches = []
    for i in range(0, len(pages), batch_size):
        chunk = pages[i : i + batch_size]
        batches.append({
            "dalga_no": len(batches) + 1,
            "sayfa_araligi": f"{chunk[0]['sayfa_no']}-{chunk[-1]['sayfa_no']}",
            "ajan_sayisi": len(chunk),
            "sayfalar": chunk,
        })

    manifest = {
        "kaynak_girdi": str(src),
        "toplam_sayfa": len(pages),
        "paralel_grup_boyutu": batch_size,
        "toplam_dalga": len(batches),
        "ortak_sozluk": "glossary.md",
        "dalgalar": batches,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    glossary_path = out_dir / "glossary.md"
    if not glossary_path.exists():
        glossary_path.write_text(GLOSSARY_TEMPLATE, encoding="utf-8")

    print(f"Hazırlık tamamlandı: {len(pages)} sayfa, {len(batches)} paralel dalga (grup boyutu={batch_size}).")
    print(f"Manifest : {manifest_path}")
    print(f"Sözlük   : {glossary_path}")


def cmd_crop(args: argparse.Namespace) -> None:
    src = Path(args.image).resolve()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    vals = [float(v.strip()) for v in args.box.split(",")]
    if len(vals) != 4:
        sys.exit("Hata: --box 'x1,y1,x2,y2' biçiminde 4 değer olmalıdır.")

    with Image.open(src) as im:
        im = im.convert("RGB")
        w, h = im.size
        if all(0.0 <= v <= 1.0 for v in vals):
            box = (int(vals[0] * w), int(vals[1] * h), int(vals[2] * w), int(vals[3] * h))
        else:
            box = tuple(int(v) for v in vals)
        cropped = im.crop(box)
        if args.zoom > 1.0:
            cropped = cropped.resize(
                (int(cropped.width * args.zoom), int(cropped.height * args.zoom)),
                Image.Resampling.LANCZOS,
            )
        cropped.save(out)
    print(f"1:1 kesit kaydedildi: {out} ({cropped.width}x{cropped.height} px)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Yazma eser paralel tercüme hazırlık ve kesit aracı.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_prep = sub.add_parser("prepare", help="PDF/ZIP/klasörü sayfalara böler ve 10'lu paralel dalga planı üretir.")
    p_prep.add_argument("input", help="PDF dosyası, ZIP arşivi veya görsel klasörü")
    p_prep.add_argument("--out", default="./proje_ciktisi", help="Çalışma çıktı klasörü")
    p_prep.add_argument("--batch-size", type=int, default=10, help="Paralel alt-ajan dalga boyutu (varsayılan: 10)")
    p_prep.add_argument("--dpi", type=int, default=220, help="PDF sayfa çözünürlüğü (varsayılan: 220 DPI)")
    p_prep.add_argument("--split-folios", action="store_true", help="Çift varaklı pozları Sağ -> Sol sırasıyla ikiye böl")
    p_prep.set_defaults(func=cmd_prepare)

    p_crop = sub.add_parser("crop", help="Şüpheli ibareden 1:1 piksel kesiti alır.")
    p_crop.add_argument("image", help="Kaynak sayfa görseli")
    p_crop.add_argument("--box", required=True, help="x1,y1,x2,y2 (0.0-1.0 oran veya piksel)")
    p_crop.add_argument("--zoom", type=float, default=1.5, help="Yakınlaştırma oranı")
    p_crop.add_argument("--out", required=True, help="Çıktı kesit dosyası")
    p_crop.set_defaults(func=cmd_crop)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
