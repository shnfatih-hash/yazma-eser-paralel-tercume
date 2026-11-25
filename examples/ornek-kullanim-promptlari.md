# Hazır Kullanım İstemleri (`yazma-eser-paralel-tercume`)

## 1. 100+ Sayfalık Arapça / Osmanlıca El Yazması PDF'i 10 Paralel Alt-Ajan ile Tercüme Etme (Ana İstem)

```markdown
Bu proje klasöründeki el yazması PDF dosyamı (`eser.pdf`) `yazma-eser-paralel-tercume` becerisini kullanarak paralel alt-ajan orkestrasyonuyla tercüme et:

1. **Hazırlık ve Ortak Sözlük (`glossary.md`):**
   - `scripts/yazma_hazirla.py` ile sayfaları yüksek çözünürlüklü görsellere ayır (çift varaklı ise `--split-folios` kullan) ve 10'arlı dalga planını (`manifest.json`) oluştur.
   - Önce ilk 2–3 sayfayı (zahriye ve mukaddime) ve son sayfayı (ferağ kaydı) okuyarak eserin müellifini, ilim dalını ve temel ıstılahlarını proje klasöründeki ortak `glossary.md` dosyasına yaz.

2. **10'arlı Paralel Alt-Ajan (`Subagents`) Dalgaları:**
   - Sayfaları **10'ar 10'ar paralel alt-ajanlara** dağıt. Aynı anda çalışan 10 ajan kendi sayfasını çevirip `ceviriler/sayfa_0001.md` ... şeklinde kaydetsin; `glossary.md` dosyasını salt-okunur okusun, okunamayan yerleri asla uydurmayıp `[...]` veya `[kelime?]` şerhi düşsün, derkenar (`sahh` / hâşiye) notlarını ayrı başlıkta göstersin ve yeni terimleri sayfa sonundaki `Yeni Terim Adayları` tablosuna yazsın.
   - Her 10'lu dalga bittiğinde yeni terim adaylarını ortak `glossary.md` içine sen birleştir ve sonraki 10'lu dalgaya geç.

3. **Son Tutarlılık ve Tahkik Editörü Ajanı:**
   - Tüm sayfalar tamamlanınca `scripts/birlestir_ve_denetle.py` ile bütünlük ve şerh raporunu çıkar; ardından ayrı bir **Tutarlılık Editörü Alt-Ajanı** görevlendirerek sayfa geçişlerindeki bölünmüş cümleleri ve tüm sayfalardaki kavram/üslup birliğini denetletip tek parça `tam_metin_tercume.md` ve `tercume_kitapcigi.html` çıktısını üret.
```

---

## 2. Şerh ve Hâşiyeli (Derkenarlı) Medrese Yazması Tercümesi

```markdown
Ekteki Arapça kelâm/fıkıh yazmasında hem ana metin (`kavluhû`) hem de yoğun sayfa kenarı (derkenar/hâmiş) ta‘lîkât notları bulunmaktadır. `yazma-eser-paralel-tercume` becerisiyle 10'arlı paralel alt-ajan görevlendir; her ajan sayfa gövdesindeki metin-şerh katmanını ve kenardaki `sahh (صح)` tashihleri ile `minhu (منه)` hâşiyelerini birbirine karıştırmadan ayrı alt başlıklarda tercüme etsin ve ortak `glossary.md` ıstılah birliğini korusun.
```

---

## 3. Türkiye Yazma Eserler Kurumu (`portal.yek.gov.tr`) Üzerinden Chrome MCP ile İnceleme

```markdown
Bilgisayarımdaki normal Google Chrome tarayıcımda `chrome://inspect/#remote-debugging` ayarını açtım ve `https://portal.yek.gov.tr` üzerinde incelemek istediğim yazma eseri açtım.

ÖNEMLİ: Antigravity'nin kendi dahili tarayıcısını ASLA açma; doğrudan `chrome-devtools` MCP ile açık Google Chrome sekmeme bağlan, zahriye, dibâce ve ferağ varaklarını güvenli/sıralı şekilde inceleyip eserin künyesini ve başlangıç `glossary.md` ıstılah listesini bu proje klasörüne çıkar.
```
