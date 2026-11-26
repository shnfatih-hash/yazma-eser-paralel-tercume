#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hugging Face Spaces Canlı Web Aracı — Yazma Eser Paralel Alt-Ajan Tercüme ve Tahkik AI Skill
"""

from __future__ import annotations

import html
import math
import tempfile
from pathlib import Path
from PIL import Image

import gradio as gr

from scripts.birlestir_ve_denetle import build_interactive_html, parse_glossary_terms
from scripts.yazma_hazirla import GLOSSARY_TEMPLATE

ROOT = Path(__file__).resolve().parent

SUPPORT_BANNER_HTML = """
<div style="background: linear-gradient(135deg, #163836 0%, #264653 100%); color: #fff; padding: 20px 24px; border-radius: 12px; border-bottom: 4px solid #ffdd00; margin-bottom: 14px;">
  <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 14px;">
    <div>
      <h2 style="margin: 0 0 6px; font-size: 1.45rem; color: #fff;">📖 Yazma Eser Paralel Alt-Ajan Tercüme ve Tahkik AI Skill</h2>
      <p style="margin: 0; opacity: 0.92; font-size: 0.95rem;">
        Arapça, Osmanlıca ve Farsça el yazmalarını 10'lu paralel alt-ajan dalgaları ve ortak ıstılah sözlüğüyle (glossary.md) tercüme aracı.
      </p>
    </div>
    <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center;">
      <a href="https://buymeacoffee.com/shnfatih8" target="_blank" rel="noopener"
         style="background: #FFDD00; color: #111; font-weight: 700; padding: 9px 16px; border-radius: 8px; text-decoration: none; font-size: 0.92rem; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
        ☕ Bir Kahve Ismarla (Buy Me a Coffee)
      </a>
      <a href="https://github.com/sponsors/shnfatih-hash" target="_blank" rel="noopener"
         style="background: #ea4aaa; color: #fff; font-weight: 700; padding: 9px 16px; border-radius: 8px; text-decoration: none; font-size: 0.92rem;">
        💖 GitHub Sponsors
      </a>
      <a href="https://github.com/shnfatih-hash/yazma-eser-paralel-tercume" target="_blank" rel="noopener"
         style="background: #24292f; color: #fff; font-weight: 600; padding: 9px 14px; border-radius: 8px; text-decoration: none; font-size: 0.9rem; border: 1px solid #57606a;">
        ⭐ GitHub Deposu
      </a>
    </div>
  </div>
</div>
"""


def plan_parallel_waves(
    eser_adi: str,
    dil: str,
    ilim_dali: str,
    profil: str,
    toplam_sayfa: int,
    paralel_ajan: int,
    cift_varak: bool,
    pdf_file: str | None,
):
    first_page_img = None
    detected_note = ""
    pages = max(1, int(toplam_sayfa))
    batch = max(1, int(paralel_ajan))
    is_kelam_preset = "Kelâm" in (profil or "")

    if pdf_file:
        try:
            import fitz

            with fitz.open(pdf_file) as doc:
                pages = len(doc)
                pix = doc[0].get_pixmap(matrix=fitz.Matrix(1.8, 1.8), alpha=False)
                first_page_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            detected_note = f"*(Yüklenen PDF'ten otomatik tespit edildi: **{pages}** sayfa)*"
        except Exception as exc:
            detected_note = f"*(PDF önizleme uyarısı: {exc})*"

    effective_pages = pages * 2 if cift_varak else pages
    waves = math.ceil(effective_pages / batch)

    plan_md = [
        f"### Paralel Orkestrasyon Planı {detected_note}",
        f"- **Eser / Dil / İlim Dalı:** {eser_adi or 'Belirtilmedi'} • {dil} • {ilim_dali}",
        f"- **Uzmanlık Profili:** {profil}",
        f"- **Toplam İşlenecek Sayfa / Yüz:** **{effective_pages}** ({'çift varaklı pozlar Sağ/Sol ayrılacak' if cift_varak else 'tekil sayfa'})",
        f"- **Paralel Alt-Ajan (`Subagent`) Dalga Boyutu:** Aynı anda **{batch}** ajan",
        f"- **Toplam Dalga Sayısı:** **{waves} dalga** + **1 Son Tutarlılık Editörü Ajanı**",
        "",
        "| Dalga | Sayfa Aralığı | Paralel Ajan | Koordinatör Görevi |",
        "| :---: | :---: | :---: | :--- |",
    ]
    for w_idx in range(min(waves, 12)):
        s1 = w_idx * batch + 1
        s2 = min(effective_pages, (w_idx + 1) * batch)
        plan_md.append(
            f"| Dalga {w_idx + 1} | Sayfa `{s1:04d}–{s2:04d}` | {s2 - s1 + 1} subagent | Çeviri + yeni ıstılah adaylarını `glossary.md` içine birleştirme |"
        )
    if waves > 12:
        plan_md.append(f"| ... | *(Toplam {waves} dalga)* | ... | Tüm dalgalar bitince `birlestir_ve_denetle.py` + Tutarlılık Editörü Ajanı |")

    split_flag = " --split-folios" if cift_varak else ""
    profile_flag = " --profile kelam-serh-tasavvuf" if is_kelam_preset else ""
    preset_clause = (
        "\n   - Mâtürîdî–Eş‘arî–Mu‘tezilî kelâmı, Kasîde-i Nûniyye / Şerhu'l-Akâid şerhleri, Dâvûd-i Karsî geleneği, mantık ve Ekberî tasavvuf (vahdet-i vücûd) ıstılahlarında TDV İA standardını uygula; aynı ıstılahın kelâm, mantık ve tasavvuftaki anlam farklarını koru."
        if is_kelam_preset
        else ""
    )

    prompt = f"""Bu proje klasöründeki `{eser_adi or 'eser.pdf'}` ({dil} — {ilim_dali}) yazma eserini `yazma-eser-paralel-tercume` becerisini kullanarak paralel alt-ajan orkestrasyonuyla tercüme et:

1. **Hazırlık ve Başlangıç Sözlüğü (`glossary.md`):**
   - `python scripts/yazma_hazirla.py prepare eser.pdf --out ./proje_ciktisi --batch-size {batch}{split_flag}{profile_flag}` komutunu çalıştır.
   - İlk 2–3 sayfayı (zahriye + dibâce) ve son sayfayı (ferağ kaydı) okuyarak {ilim_dali} alanına ait temel ıstılahları ortak `proje_ciktisi/glossary.md` dosyasına işle.{preset_clause}

2. **{batch}'lu Paralel Alt-Ajan (`Subagents`) Dalgaları ("Sıfır Kayıp" & "Sıfır Uydurma" — Toplam {effective_pages} Sayfa / {waves} Dalga):**
   - Sayfaları **{batch}'ar {batch}'ar paralel alt-ajanlara** dağıt. Her ajan kendi sayfasını çevirip `proje_ciktisi/ceviriler/sayfa_XXXX.md` olarak kaydetsin ve ortak `glossary.md` sözlüğünü salt-okunur okusun.
   - **Tam Metin Sadakati:** Osmanlıca veya karma (*mülemma*) metinlerde hiçbir cümleyi "zaten Türkçe" ya da "klasik hamdele/dua" diyerek atlamasın; başlıklardan beyitlere, vakıf, temellük ve ketebe kayıtlarına kadar tamamını günümüz akademik Türkçesine eksiksiz aktarsın.
   - **Katman ve Şerh Hassasiyeti:** Ana metin (`ḳavluhû`) ile şerh katmanını çift tırnakla (`" "`) ayırsın; kenardaki `sahh (صح)` tashihlerini doğrudan ait olduğu cümleye yerleştirsin; `minhü (منه)` ve derkenar notlarını sona yığmadan ilgili paragrafın hemen altında göstersin; okunamayan yerleri uydurmayıp `[...]` veya `[kelime?]` şerhi düşsün; zamir mercii veya doktriner çift anlamlılıklarda paragraf altına `Not:` açsın ve yeni terimleri `Yeni Terim Adayları` tablosuna yazsın.
   - Her {batch}'lu dalga bittiğinde yeni terimleri `glossary.md` dosyasına tek elden sen ekle ve bir sonraki dalgayı başlat.

3. **Son Tutarlılık ve Tahkik Editörü Ajanı (Tahkikli + Varaksız Akıcı Saf Metin):**
   - Tüm sayfalar tamamlandığında `python scripts/birlestir_ve_denetle.py ./proje_ciktisi --title "{eser_adi or 'Yazma Eser Tahkikli Tercüme'}"` komutunu çalıştır.
   - Ayrı bir **Tutarlılık Editörü Alt-Ajanı** görevlendirerek rekabe tekrarlarını temizletip sayfa geçişlerindeki bölünmüş cümleleri birleştir; hem `[vr. Xa]` atıflı `tam_metin_tercume.md` hem kesintisiz saf okuma metni `tam_metin_akici_okuma.md` hem de `tercume_kitapcigi.html` çıktısını üret."""

    return "\n".join(plan_md), prompt, first_page_img


def preview_booklet(title: str, glossary_md: str, sample_page_md: str):
    terms = parse_glossary_terms(glossary_md)
    pages = [{"no": 1, "dosya": "sayfa_0001.md", "icerik": sample_page_md}]
    flags = [{"sayfa": 1, "isaret": "[kelime?]", "baglam": "Örnek şerh kontrol satırı"}] if "?" in sample_page_md or "[..." in sample_page_md else []
    rendered = build_interactive_html(title, pages, terms, flags)
    iframe = (
        f'<iframe srcdoc="{html.escape(rendered, quote=True)}" '
        f'style="width:100%; height:560px; border:1px solid #dfd6c5; border-radius:10px; background:#f7f4ec;"></iframe>'
    )
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_tercume_kitapcigi.html", mode="w", encoding="utf-8")
    tmp.write(rendered)
    tmp.close()
    return iframe, tmp.name


def build_ui() -> gr.Blocks:
    sample_glossary = (
        (ROOT / "examples" / "ornek_glossary.md").read_text(encoding="utf-8")
        if (ROOT / "examples" / "ornek_glossary.md").exists()
        else GLOSSARY_TEMPLATE
    )
    sample_page = (
        "## Varak 1b — Dibâce ve Konuya Giriş\n\n"
        "### Asıl Metin\n"
        "قوله: الحمد لله الواجب لذاته... أقول: افتتح المصنف رحمه الله كتابه بالحمد...\n\n"
        "### Akademik Türkçe Tercüme\n"
        "**Müellifin \"Zâtı gereği zorunlu varlık (Vâcibü'l-vücûd) olan Allah'a hamdolsun\" sözü:** "
        "Müellif (Allah ona rahmet etsin) kitabına hamdele ile başladı...\n\n"
        "### Derkenar / Hâmiş Notları\n"
        "- `[Kenar tashihi (sahh): ...]` Sağ kenarda müstensih doğrulama kaydı mevcuttur.\n\n"
        "### Şerh ve Kritik Aparat\n"
        "- Satır 9'da rutubet izi sebebiyle `[müreccih?]` ibaresi ihtiyatla okunmuştur."
    )
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    if readme_text.startswith("---"):
        parts = readme_text.split("---", 2)
        if len(parts) == 3:
            readme_text = parts[2].strip()

    init_iframe, _ = preview_booklet("Örnek Kelâm Risâlesi Şerhi — Tahkikli Tercüme", sample_glossary, sample_page)

    with gr.Blocks(title="Yazma Eser Paralel Tercüme & Tahkik AI Skill") as demo:
        gr.HTML(SUPPORT_BANNER_HTML)

        with gr.Tabs():
            with gr.Tab("⚡ 10'lu Paralel Dalga Planlayıcı & Prompt Üretici"):
                gr.Markdown(
                    "Elinizdeki yazma eserin bilgilerini girin (veya doğrudan PDF yükleyin); araç sayfa sayısına göre **10'arlı paralel alt-ajan dalga planını** ve Antigravity/Claude'a yapıştıracağınız hazır orkestrasyon istemini üretsin."
                )
                with gr.Row():
                    in_title = gr.Textbox(label="Eser Adı", value="Şerhu'l-Akâid Hâşiyesi")
                    in_lang = gr.Dropdown(
                        ["Arapça", "Osmanlı Türkçesi", "Farsça", "Karma / Mülemma (Arapça–Osmanlıca–Farsça)"],
                        value="Arapça",
                        label="Eser Dili",
                    )
                    in_field = gr.Dropdown(
                        ["Kelâm / Akâid", "Fıkıh & Usûl", "Tasavvuf", "Felsefe / Mantık", "Tefsir / Hadis", "Tarih / Tabakât"],
                        value="Kelâm / Akâid",
                        label="İlim Dalı",
                    )
                    in_profile = gr.Dropdown(
                        [
                            "Genel Yazma Eser Tahkiki",
                            "Kelâm, Şerh–Hâşiye & Tasavvuf (Nûniyye / Şerhu'l-Akâid / Karsî)",
                        ],
                        value="Kelâm, Şerh–Hâşiye & Tasavvuf (Nûniyye / Şerhu'l-Akâid / Karsî)",
                        label="Uzmanlık Sözlük Profili",
                    )
                with gr.Row():
                    in_pages = gr.Number(label="Toplam PDF Sayfa / Poz Sayısı", value=100, precision=0)
                    in_batch = gr.Slider(2, 15, value=10, step=1, label="Aynı Anda Çalışacak Paralel Alt-Ajan Sayısı")
                    in_split = gr.Checkbox(label="Çift varaklı poz (Her pozda Sağ vr. a + Sol vr. b var)", value=False)
                in_pdf = gr.File(label="İsteğe Bağlı: Otomatik Sayfa Sayımı ve Zahriye Önizlemesi İçin PDF Yükle", file_types=[".pdf"], type="filepath")
                btn_plan = gr.Button("🚀 10'lu Paralel Dalga Planı ve Orkestrasyon Promptu Üret", variant="primary")
                with gr.Row():
                    out_plan = gr.Markdown()
                    out_preview_img = gr.Image(label="PDF 1. Sayfa (Zahriye) Önizlemesi")
                out_orch_prompt = gr.Code(label="Antigravity / Claude Ana Oturumuna Yapıştıracağınız Orkestrasyon İstemi", language="markdown")
                btn_plan.click(
                    plan_parallel_waves,
                    inputs=[in_title, in_lang, in_field, in_profile, in_pages, in_batch, in_split, in_pdf],
                    outputs=[out_plan, out_orch_prompt, out_preview_img],
                )

            with gr.Tab("📖 Ortak Terim Sözlüğü (Glossary) & HTML Kitapçık Önizleme"):
                gr.Markdown(
                    "Paralel alt-ajanların ortak kullandığı `glossary.md` yapısını ve birleştirme sonrası üretilen **İnteraktif HTML Tercüme Kitapçığı**'nı canlı olarak deneyin."
                )
                b_title = gr.Textbox(label="Kitapçık Başlığı", value="Örnek Kelâm Risâlesi Şerhi — Tahkikli Tercüme")
                with gr.Row():
                    b_glossary = gr.Code(value=sample_glossary, language="markdown", label="Ortak glossary.md İçeriği", lines=12)
                    b_page = gr.Code(value=sample_page, language="markdown", label="Örnek Çevrilmiş Sayfa (sayfa_0001.md)", lines=12)
                btn_booklet = gr.Button("✨ İnteraktif Tercüme Kitapçığını Güncelle & İndir", variant="primary")
                out_booklet_html = gr.HTML(value=init_iframe)
                out_booklet_file = gr.File(label="İnteraktif HTML Kitapçığı İndir")
                btn_booklet.click(preview_booklet, inputs=[b_title, b_glossary, b_page], outputs=[out_booklet_html, out_booklet_file])

            with gr.Tab("📦 Kurulum & Yazma Eser Anatomisi Rehberi"):
                gr.Markdown(readme_text)

        gr.HTML(
            """
            <div style="text-align: center; margin-top: 18px; padding: 14px; background: #faf7f0; border: 1px solid #e2dac9; border-radius: 10px;">
              <strong>Projeyi faydalı buldunuz mu?</strong> Açık kaynaklı yazma eser tahkiki ve dijital beşerî bilimler AI araçlarına destek olmak için:
              <a href="https://buymeacoffee.com/shnfatih8" target="_blank" style="margin-left:8px; font-weight:700; color:#7a5200;">☕ Buy Me a Coffee (shnfatih8)</a> •
              <a href="https://github.com/sponsors/shnfatih-hash" target="_blank" style="margin-left:6px; font-weight:700; color:#b82578;">💖 GitHub Sponsors</a>
            </div>
            """
        )
    return demo


if __name__ == "__main__":
    app = build_ui()
    app.launch()
