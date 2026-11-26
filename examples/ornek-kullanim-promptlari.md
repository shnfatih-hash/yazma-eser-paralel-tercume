# Hazır Kullanım İstemleri (`yazma-eser-paralel-tercume`)

## 1. 100+ Sayfalık Arapça / Osmanlıca El Yazması PDF'i 10 Paralel Alt-Ajan ile Tercüme Etme (Ana İstem)

```markdown
Bu proje klasöründeki el yazması PDF dosyamı (`eser.pdf`) `yazma-eser-paralel-tercume` becerisini kullanarak paralel alt-ajan orkestrasyonuyla tercüme et:

1. **Hazırlık ve Ortak Sözlük (`glossary.md`):**
   - `scripts/yazma_hazirla.py` ile sayfaları yüksek çözünürlüklü görsellere ayır (çift varaklı ise `--split-folios` kullan) ve 10'arlı dalga planını (`manifest.json`) oluştur.
   - Önce ilk 2–3 sayfayı (zahriye ve mukaddime) ve son sayfayı (ferağ kaydı) okuyarak eserin müellifini, ilim dalını ve temel ıstılahlarını (TDV İA imlâ standardıyla) proje klasöründeki ortak `glossary.md` dosyasına yaz.

2. **10'arlı Paralel Alt-Ajan (`Subagents`) Dalgaları ("Sıfır Kayıp" & "Sıfır Uydurma"):**
   - Sayfaları **10'ar 10'ar paralel alt-ajanlara** dağıt. Aynı anda çalışan 10 ajan kendi sayfasını çevirip `ceviriler/sayfa_0001.md` ... şeklinde kaydetsin ve `glossary.md` dosyasını salt-okunur okusun.
   - **Tam Metin Sadakati:** Osmanlıca veya karma (*mülemma*) cümleleri "zaten Türkçe" diyerek atlamasın; dibâce/hamdele/salvele dualarından beyitlere, ferağ, vakıf ve temellük kayıtlarına kadar hiçbir yeri özetlemeden eksiksiz günümüz akademik Türkçesine aktarsın.
   - **Katman ve Şerh Hassasiyeti:** Okunamayan yerleri asla uydurmayıp `[...]` veya `[kelime?]` şerhi düşsün; kenardaki `sahh (صح)` tashihlerini doğrudan ait olduğu cümleye yerleştirsin; `minhu (منه)` ve derkenar notlarını sona yığmadan ilgili paragrafın hemen altında göstersin; zamir mercii veya doktriner çift anlamlılıklarda paragraf altına kısa `Not:` açsın ve yeni terimleri sayfa sonundaki `Yeni Terim Adayları` tablosuna yazsın.
   - Her 10'lu dalga bittiğinde yeni terim adaylarını ortak `glossary.md` içine sen birleştir ve sonraki 10'lu dalgaya geç.

3. **Son Tutarlılık ve Tahkik Editörü Ajanı (Tahkikli + Akıcı Çift Çıktı):**
   - Tüm sayfalar tamamlanınca `scripts/birlestir_ve_denetle.py` ile bütünlük ve şerh raporunu çıkar; ardından ayrı bir **Tutarlılık Editörü Alt-Ajanı** görevlendirerek rekabe tekrarlarını temizletip bölünen cümleleri birleştir ve hem atıflı `tam_metin_tercume.md` hem kesintisiz `tam_metin_akici_okuma.md` hem de `tercume_kitapcigi.html` çıktısını üret.
```

---

## 2. Kelâm, Şerh–Hâşiye ve Tasavvuf Uzmanlık İstemi (*Kasîde-i Nûniyye, Dâvûd-i Karsî, Şerhu'l-Akâid ve Ekberî Metinler*)

```markdown
Bu proje klasöründeki kelâm / akaid / tasavvuf şerh-hâşiye yazmasını (`eser.pdf`) `yazma-eser-paralel-tercume` becerisi ve `examples/kelam_nuniyye_karsi_glossary.md` uzmanlık sözlüğüyle paralel alt-ajanlarla tercüme et:

- **Rol ve Doktriner Hassasiyet:** Mâtürîdî–Eş‘arî–Mu‘tezilî kelâmı, Hızır Bey'in *el-Kasîdetü'n-Nûniyye* şerh/tercümeleri (Bosna/Rumeli nüshaları dâhil), Dâvûd-i Karsî ve Osmanlı medrese geleneği, mantık/felsefe ve Ekberî tasavvuf (*vahdet-i vücûd* ve kelâmî tenkitler) terminolojisini TDV İslâm Ansiklopedisi standardında kullan (*hüsün ve kubuh, teklîf-i mâ lâ yutâk, kesb, irâde-i cüz'iyye, îkâ‘, hâl, tekvîn, taalluk, cevher, araz, mâhiyet, vücûd-ı zihnî, devir, teselsül, hulûl, ittihâd*). Bir ıstılahın kelâm, mantık ve tasavvufta farklı anlamları varsa bağlama en uygun karşılığı seç.
- **Metin–Şerh–Hâşiye Ayrımı ve Diyalektik Akıcılık:** Ana metin beytini veya `"Müellifin '...' sözü"` (`ḳavluhû`) ibaresini şârihin açıklamasından çift tırnakla net biçimde ayır; *"Eğer dersen ki... Ben de derim ki..."* (`fe-in ḳulte ... ḳultü`) diyalektiğini ve uzun Osmanlıca inşâ cümlelerini anlam zincirini koparmadan berrak akademik Türkçeye çevir. Âyet/hadis/eser referans parantezlerini (`[Mü'min: 55]`, `(Şerhu'l-Akâid, 45)`) aynen koru.
- **Sıfır Kayıp ve Kenar Notları:** Hiçbir Osmanlıca cümleyi "zaten Türkçe" veya "klasik hamdele/dua" diyerek atlama; `sahh` kayıtlarını ait olduğu cümleye yerleştir, `minhü`/derkenar notlarını ilgili paragrafın hemen altında ver; çok ihtimalli zamir mercii veya kelâmî/tasavvufî yorum farklarını paragraf altında `Not:` ile belirt. Sonunda hem `[vr. Xa]` atıflı tahkik nüshasını hem de varak kesintileri arındırılmış kesintisiz akıcı okuma metnini üret.
```

---

## 3. Türkiye Yazma Eserler Kurumu (`portal.yek.gov.tr`) Üzerinden Chrome MCP ile İnceleme

```markdown
Bilgisayarımdaki normal Google Chrome tarayıcımda `chrome://inspect/#remote-debugging` ayarını açtım ve `https://portal.yek.gov.tr` üzerinde incelemek istediğim yazma eseri açtım.

ÖNEMLİ: Antigravity'nin kendi dahili tarayıcısını ASLA açma; doğrudan `chrome-devtools` MCP ile açık Google Chrome sekmeme bağlan, zahriye (temellük/vakıf kayıtları dâhil), dibâce ve ferağ varaklarını güvenli/sıralı şekilde inceleyip eserin künyesini ve başlangıç `glossary.md` ıstılah listesini bu proje klasörüne çıkar.
```
