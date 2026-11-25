---
name: yazma-eser-paralel-tercume
description: >-
  Çok sayfalı Arapça, Osmanlıca ve Farsça el yazması (mahtût) veya nadir matbu
  eser PDF/görsel dosyalarını 10'arlı paralel alt-ajan (subagents) dalgaları,
  çakışma korumalı ortak terim sözlüğü (glossary.md), 1:1 piksel şerh aparatı ve
  son tutarlılık/tahkik editörü ajanıyla akademik Türkçeye tercüme ve tahkik
  etme becerisi. Kullanıcı el yazması tercümesi, çok sayfalı Arapça/Osmanlıca
  PDF çevirisi, paralel subagent çevirisi veya yazma eser tahkiki istediğinde
  etkinleştirin.
---

# Yazma Eser Paralel Alt-Ajan Tercüme ve Tahkik Becerisi

Bu beceri; **Arapça, Osmanlı Türkçesi ve Farsça** el yazması (*mahtût*) veya klasik matbu eserlerin (kelâm, fıkıh, usûl, tefsir, hadis, tasavvuf, felsefe/mantık, tarih, şerh ve hâşiyeler) yüzlerce sayfasını tek tek beklemek yerine **ana koordinatör oturum + 10'lu paralel alt-ajan (`subagent`) dalgaları + ortak ıstılah sözlüğü (`glossary.md`) + son tutarlılık editörü ajanı** mimarisiyle sıfır uydurma disipliniyle tercüme ve tahkik eder.

- **PDF / Görsel Hazırlama ve Dalga Planlayıcı:** [scripts/yazma_hazirla.py](./scripts/yazma_hazirla.py)
- **Sayfa Birleştirme, Şerh Denetimi ve İnteraktif HTML Kitapçık Üretici:** [scripts/birlestir_ve_denetle.py](./scripts/birlestir_ve_denetle.py)
- **Yazma Eser Anatomisi (Zahriye, Rekabe, Hâmiş, Sahh) ve Çeviri İlkeleri:** [references/01-yazma-eser-anatomisi-ve-tercume-ilkeleri.md](./references/01-yazma-eser-anatomisi-ve-tercume-ilkeleri.md)
- **Örnek Ortak Terim Sözlüğü (`Glossary`):** [examples/ornek_glossary.md](./examples/ornek_glossary.md)
- **Kopyala–Yapıştır Hazır İstem Şablonları:** [examples/ornek-kullanim-promptlari.md](./examples/ornek-kullanim-promptlari.md)

---

## 1. Altın Kurallar: Sıfır Halüsinasyon, Çakışma Koruması ve Tarayıcı Güvenliği

1. **Sıfır Tahmin ve Şerh Aparatı:** El yazmasında rutubet, siliklik, mürekkep dağılması, kurt yeniği veya ta‘lîk/şikeste istifi yüzünden net okunamayan hiçbir kelime uydurulmaz:
   - `[...]` → Okunamayan / hasarlı kısım (1:1 kesit + neden okunamadığı şerh düşülür).
   - `[kelime?]` → Harf iskeleti ve bağlam güçlü ama noktasız/tereddütlü okunuş (alternatifleriyle şerhe yazılır).
   - `(!)` → Müstensih hatası (*sehv-i kalem*) olan yer (asıldaki imlâ + doğru şekli şerhte gösterilir).
   - `[Hâmiş / Derkenar: ...]` ve `[Sahh / Tashih: ...]` → Sayfa kenarındaki müellif/müstensih tashihleri (`صح`) ve hâşiye notları ana metne karıştırılmaz, ayrı katman olarak gösterilir.
2. **Çakışma Korumalı Ortak Sözlük (`glossary.md`) Protokolü:**
   - Paralel çalışan 10 alt-ajan **aynı anda aynı `glossary.md` dosyasına doğrudan yazmaz** (yazma çakışmasını önlemek için!).
   - Her alt-ajan mevcut `glossary.md` dosyasını **salt-okunur** okur, kendi sayfasını `ceviriler/sayfa_XXX.md` dosyasına yazar ve o sayfada yeni karşılaştığı ıstılahları sayfa dosyasının sonundaki `## Yeni Terim Adayları` tablosuna ekler.
   - Her 10'lu dalga tamamlandığında **Ana Koordinatör Oturum** yeni terim adaylarını süzüp tek elden `glossary.md` dosyasına işler ve bir sonraki 10'lu dalgayı güncellenmiş sözlükle başlatır!
3. **YEK Portal & BOA İçin Yerleşik Tarayıcı Yasağı:** `portal.yek.gov.tr` veya `katalog.devletarsivleri.gov.tr` sitelerini **ASLA** Antigravity'nin kendi dahili tarayıcısında (`browser` alt-ajanı) açmayın (*"Web Sayfasına Erişim Engellendi"* hatası verir). Yalnızca **Chrome DevTools MCP** üzerinden kullanıcının açık **normal Google Chrome** sekmesine bağlanın ve sayfaları paralel değil, en az `1800 ms` aralıklı sıralı isteklerle inceleyin.

---

## 2. Beş Aşamalı Paralel Tercüme ve Tahkik İş Akışı

### Aşama 0 — Proje Hazırlığı, PDF Sayfa Ayırma ve Dalga Planı
Kullanıcı PDF veya görüntü klasörü verdiğinde `scripts/yazma_hazirla.py` aracını çalıştırın:
```bash
python scripts/yazma_hazirla.py prepare eser.pdf --out ./proje_ciktisi --batch-size 10 --dpi 220
```
- Çift varaklı pozlar (sağ `vr. Xa` ve sol `vr. Xb`) bir aradaysa `--split-folios` bayrağıyla sağdan sola doğru okuma sırasına (`R` → `L`) ayırın.
- Betik otomatik olarak `sayfa_gorselleri/`, `ceviriler/`, `kesitler/`, `manifest.json` (10'arlı dalga listesi) ve başlangıç `glossary.md` dosyasını oluşturur.

### Aşama 1 — Örneklem Keşfi ve Başlangıç `glossary.md` Kurulumu (Koordinatör)
Paralel ajanları başlatmadan önce koordinatör olarak ilk 2–3 sayfayı (*zahriye + dibâce/mukaddime*) ve son sayfayı (*ferağ kaydı / hâtime*) bizzat okuyun:
1. Eserin adını, müellifini, ilim dalını (ör. Mâtürîdî kelâmı, Hanefî fıkhı, Ekberî tasavvuf, İbn Sînâcı felsefe), hat türünü ve müstensih/tarih bilgisini tespit edin.
2. Eserin temel teknik ıstılahlarını (ör. *cevher, araz, mâhiyet, vücûd-ı zihnî, irâde-i cüz’iyye, illet-i tâmme*), kişi/eser adlarını ve çeviri üslup kurallarını `glossary.md` dosyasına işleyin.

### Aşama 2 — 10'arlı Paralel Alt-Ajan (`Subagent`) Dalgaları
`manifest.json` içindeki sayfa gruplarını **10'ar 10'ar** (`Dalga 1: Sayfa 1–10`, `Dalga 2: Sayfa 11–20` ...) ilerletin:
1. Her dalgada aynı anda en fazla **10 paralel `self` (veya yazma yetkili) alt-ajan** (`invoke_subagent`) başlatın.
2. Her alt-ajana şu net görevi verin:
   - Yalnızca kendisine atanan sayfa görselini (`sayfa_gorselleri/sayfa_XXX.png`) ve güncel `glossary.md` dosyasını okumak,
   - Gerekirse tereddütlü satırlardan 1:1 piksel kesiti almak,
   - Sayfanın sağ alt/sol alt köşesindeki **rekabe (müş‘ir kelime)** ile sayfa başı/sonu yarım cümle durumunu not etmek,
   - Çıktıyı standart şablonla `ceviriler/sayfa_XXX.md` dosyasına kaydetmek (`## Künye & Varak Durumu`, `## Asıl Metin (Arapça/Osmanlıca)`, `## Akademik Türkçe Tercüme`, `## Derkenar / Hâmiş Notları`, `## Şerh ve Kritik Aparat`, `## Yeni Terim Adayları`).
3. Dalga tamamlandığında 10 çıktıyı kontrol edin, `Yeni Terim Adayları` maddelerini `glossary.md` içine birleştirin ve bir sonraki 10'lu dalgaya geçin.

### Aşama 3 — Otomatik Bütünlük Denetimi ve Birleştirme
Tüm dalgalar tamamlandığında `scripts/birlestir_ve_denetle.py` betiğini çalıştırın:
```bash
python scripts/birlestir_ve_denetle.py ./proje_ciktisi --title "Eser Adı — Tahkikli Tercüme"
```
- Betik eksik sayfa olup olmadığını, sayfa sonu–sayfa başı yarım cümle işaretlerini, tüm `[...]` / `[kelime?]` şerhlerinin toplu listesini ve `glossary.md` terimlerinin sayfalardaki kullanım sıklığını denetler (`denetim_raporu.md`).

### Aşama 4 — Tutarlılık ve Tahkik Editörü Alt-Ajanı (Son Kontrol)
Son aşamada tek bir **Tutarlılık ve Tahkik Editörü Alt-Ajanı** görevlendirin:
1. `glossary.md` ve `denetim_raporu.md` rehberliğinde ardışık sayfalar arasında bölünen cümleleri akıcı biçimde birleştirir (*sayfa/varak geçiş işaretlerini `[vr. 12b]` köşeli parantezle koruyarak!*),
2. Aynı Arapça/Osmanlıca ıstılahın 1. sayfada farklı, 80. sayfada farklı çevrilmesini önleyerek kavram birliğini sağlar,
3. `scripts/birlestir_ve_denetle.py` ile nihai `tam_metin_tercume.md` ve çift sütunlu/sekmeli **İnteraktif HTML Tercüme Kitapçığı (`tercume_kitapcigi.html`)** çıktısını üretir.
