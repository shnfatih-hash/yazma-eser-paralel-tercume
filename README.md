---
title: Yazma Eser Paralel Tercüme & Tahkik AI Skill
emoji: 📖
colorFrom: green
colorTo: yellow
sdk: static
pinned: true
license: mit
short_description: 10 paralel alt-ajan ve ortak sözlükle yazma eser tercümesi
---

# Yazma Eser Paralel Alt-Ajan Tercüme ve Tahkik AI Skill (`yazma-eser-paralel-tercume`)

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Bir%20Kahve%20Ismarla-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/shnfatih8)
[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Projeye%20Destek%20Ol-ea4aaa?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/shnfatih-hash)
[![Hugging Face Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Canlı%20Web%20Aracı-FFD21E?style=for-the-badge)](https://huggingface.co/spaces/sahanfatih/yazma-eser-paralel-tercume)
[![GitHub Repo](https://img.shields.io/badge/GitHub-shnfatih--hash%2Fyazma--eser--paralel--tercume-181717?style=for-the-badge&logo=github)](https://github.com/shnfatih-hash/yazma-eser-paralel-tercume)

Çok sayfalı **Arapça, Osmanlıca ve Farsça el yazması (*mahtût*)** veya klasik matbu eser PDF/görsel dosyalarını tek tek sayfa beklemek yerine **10'arlı paralel alt-ajan (`subagents`) dalgaları**, **çakışma korumalı ortak terim sözlüğü (`glossary.md`)**, **1:1 piksel şerh aparatı** ve **son Tutarlılık & Tahkik Editörü Ajanı** ile akademik Türkçeye çeviren açık kaynaklı yapay zekâ becerisi (*Agent Skill* + *Canlı Web Aracı*).

> **Kardeş Projeler:**  
> - 1500'lere kadar Osmanlı soy kütüğü ve köy tarihi araştırması için: **[`shnfatih-hash/devlet-arsivleri-soykutugu`](https://github.com/shnfatih-hash/devlet-arsivleri-soykutugu)**  
> - Osmanlıca Ferman, Berat, İrade, Hüccet ve Tahrirat okuma için: **[`shnfatih-hash/osmanlica-resmi-evrak`](https://github.com/shnfatih-hash/osmanlica-resmi-evrak)**

---

## Nasıl Çalışır? (100 Sayfalık Bir Yazma Eser Örneği)

```text
  [100 Sayfalık PDF / Varak Klasörü]
                 │
                 ▼
  1. yazma_hazirla.py  ──► Sayfa görselleri (Sağ/Sol varak ayırma) + 10'arlı dalga planı
                 │
                 ▼
  2. Ana Koordinatör   ──► Zahriye & Mukaddimeyi okur, başlangıç `glossary.md` sözlüğünü kurar
                 │
                 ▼
  3. 10 Paralel Ajan   ──► Dalga 1 (Sayfa 1–10), Dalga 2 (Sayfa 11–20) ... aynı anda çevirir;
     (Arka Planda)         her dalga sonunda yeni ıstılahlar `glossary.md` sözlüğüne eklenir
                 │
                 ▼
  4. Tutarlılık Ajanı  ──► `birlestir_ve_denetle.py` ile eksik sayfa/şerh denetimi yapar,
     (Son Editör)          bölünmüş cümleleri ve kavram birliğini sağlayıp HTML Kitapçık üretir
```

---

## Temel Özellikler

1. **10'arlı Paralel Alt-Ajan Orkestrasyonu:** Ana sohbet oturumu koordinasyonu yürütür; arka planda çalışan 10 alt-ajan her sayfayı ayrı dosyaya (`ceviriler/sayfa_0001.md`) çevirip işi bitince kapanır.
2. **Çakışma Korumalı Ortak Terim Sözlüğü (`glossary.md`):** Paralel ajanlar aynı anda sözlük dosyasını ezmez; `glossary.md` dosyasını salt-okunur okur, yeni terim adaylarını dalga sonunda koordinatöre teslim eder.
3. **Yazma Eser Diplomatik ve Tahkik Disiplini:**
   - **Rekabe (*müş‘ir kelime*)** takibiyle varak sonu–varak başı cümle bağlama,
   - Kenar **tashih (`صح` / *sahh*)** kayıtları ile **derkenar hâşiye (`منه` / *minhu*)** notlarını ana metinden ayrı katmanda gösterme,
   - Silik, rutubetli veya okunamayan yerleri asla uydurmadan `[...]`, `[kelime?]`, `(!)` ile şerh aparatına alma.
4. **Yerleşik Python Araçları & İnteraktif HTML Kitapçığı:**
   - `scripts/yazma_hazirla.py` — PDF/ZIP/klasörden yüksek çözünürlüklü sayfa çıkarma, çift varak (`a/b`) ayırma, `manifest.json` ve `glossary.md` üretimi.
   - `scripts/birlestir_ve_denetle.py` — Eksik sayfa ve şerh denetimi (`denetim_raporu.md`), birleşik Markdown (`tam_metin_tercume.md`) ve aranabilir terim sözlüklü **İnteraktif HTML Tercüme Kitapçığı (`tercume_kitapcigi.html`)** üretimi.

---

## Kurulum

```bash
# Python bağımlılıkları
pip install Pillow pymupdf
```

```powershell
# Windows (PowerShell) — Google Antigravity
git clone https://github.com/shnfatih-hash/yazma-eser-paralel-tercume.git "$HOME\.gemini\config\skills\yazma-eser-paralel-tercume"
```
```bash
# macOS / Linux — Google Antigravity veya Claude Code
git clone https://github.com/shnfatih-hash/yazma-eser-paralel-tercume.git ~/.gemini/config/skills/yazma-eser-paralel-tercume
git clone https://github.com/shnfatih-hash/yazma-eser-paralel-tercume.git ~/.claude/skills/yazma-eser-paralel-tercume
```

---

## Hızlı Başlangıç (Kopyala–Yapıştır Prompt)

Masaüstünde yeni bir proje klasörü (ör. `Yazma_Tercume_Projem`) açın, PDF dosyanızı içine koyun, Antigravity'de **`Open Folder`** ile açın ve şu komutu gönderin:

```markdown
Bu proje klasöründeki el yazması PDF dosyamı `yazma-eser-paralel-tercume` becerisiyle çevir:
1. `scripts/yazma_hazirla.py` ile sayfaları ayır ve mukaddimeden hareketle ortak `glossary.md` terim sözlüğünü oluştur.
2. Sayfaları **10'arlı paralel alt-ajan (`subagent`)** dalgalarıyla çevirip `ceviriler/sayfa_XXXX.md` olarak kaydet; her dalga sonunda yeni terimleri `glossary.md` içine işle, okunamayan yerleri uydurma (`[...]`).
3. Tüm sayfalar bitince `scripts/birlestir_ve_denetle.py` ve ayrı bir **Tutarlılık Editörü Alt-Ajanı** ile sayfalar arası kavram ve cümle birliğini sağlayıp nihai `tam_metin_tercume.md` ve `tercume_kitapcigi.html` dosyalarını oluştur.
```

---

## ♥ Projeye Gönüllü Destek

Bu proje tamamen ücretsiz ve açık kaynaklıdır. Çalışmayı faydalı bulduysanız bir kahve ısmarlayarak veya GitHub Sponsors üzerinden destek olabilirsiniz:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Bir%20Kahve%20Ismarla-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/shnfatih8)
[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Projeye%20Destek%20Ol-ea4aaa?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/shnfatih-hash)

---

## Lisans

MIT Lisansı — bkz. [LICENSE](LICENSE).
