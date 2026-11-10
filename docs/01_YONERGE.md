# 01 — Dönem Projesi Yönergesi (Yapılandırılmış Özet)

> Kaynak: `references/papers/Yonerge_Bulanik_Mantik_Donem_Projesi.pdf` (11 sayfa). Çelişkide PDF esastır.

## 1. Amaç ve akış

Derste anlatılan teori; güncel bir bilimsel çalışma üzerinden uygulanır. Proje yalnızca makale sunumu değildir: makale incelenir, yöntem (veya temel bileşeni) yeniden gerçekleştirilir, üzerine deneysel bir katkı geliştirilir, kontrollü deneylerle değerlendirilir, raporlanır, tekrar üretilebilir şekilde GitHub'da paylaşılır.

`İNCELE → ANLA → UYGULA → GELİŞTİR → DENEY YAP → KARŞILAŞTIR → ANALİZ ET → SUN → RAPORLA`

## 2. Puan dağılımı

| Bileşen | Puan |
|---|---|
| Sunum ve Sözlü Savunma | 20 |
| Uygulama / Yeniden Gerçekleştirme | 30 |
| Özgün Katkı / Geliştirme | 30 |
| Teknik Rapor ve GitHub | 20 |
| **Toplam** | **100** |

## 3. Süreç aşamaları

1. Referans makalenin incelenmesi (problem, amaç, yöntem, veri seti, deneyler, sonuçlar, sınırlılıklar)
2. Literatür araştırması (konu ve yöntemle ilişkili güncel çalışmalar)
3. Yöntemin (belirlenen bölümün) yeniden gerçekleştirilmesi
4. Özgün katkının geliştirilmesi
5. Deneysel değerlendirme (baseline vs geliştirilen, kontrollü deneyler)
6. Raporlama ve dokümantasyon (teknik rapor + GitHub)
7. Sunum ve savunma (canlı demo + sözlü savunma)

## 4. Sunum ve sözlü savunma — 20 puan

15–20 dk sunum + ~5 dk soru-cevap/demo/savunma. Sadece makale özeti DEĞİL.

**İçerik:** Problem tanımı ve motivasyon · Literatür araştırması (karşılaştırmalı) · Teorik altyapı · Referans makalede kullanılan yöntem (girdi/çıktı, üyelik fonksiyonları, kural yapısı, inference, defuzzification, optimizasyon/ML bileşenleri, mimari) · Deneysel çalışma (veri seti, ortam, parametreler, karşılaştırılan yöntemler, ölçütler) · Referans makalenin sonuçları (tablo/grafik) · Eleştirel değerlendirme (güçlü yönler, sınırlılıklar, başarısızlık durumları) · Gerçekleştirilen uygulama ve özgün katkı (karşılaştırmalı sonuçlar)

| Ölçüt | Puan |
|---|---|
| Problem ve motivasyonun açıklanması | 2 |
| Güncel literatür araştırması | 3 |
| Bulanık Mantık teorik altyapısı | 3 |
| Yöntem ve sistem mimarisinin açıklanması | 4 |
| Deney ve veri setinin açıklanması | 2 |
| Sonuçların analizi | 2 |
| Sınırlılıkların ve geliştirmelerin tartışılması | 2 |
| Sunum kalitesi ve sorulara verilen cevaplar | 2 |

## 5. Uygulama / Yeniden gerçekleştirme — 30 puan

- Amaç yalnızca mevcut kodu çalıştırmak değil; yöntem incelenir, sistem tasarlanır, temel bileşenler uygulanır.
- Araçlar: Python, MATLAB, Simulink, Jupyter, Colab vb.
- **MRR (Minimum Reproduction Requirement):** Her proje için belirlenecek; çalışır durumda gerçekleştirilmesi gereken minimum teknik sistem. Makale kapsamlıysa tamamı şart değil; belirlenen temel Bulanık Mantık bileşeni/alt sistem yapılır.
- **Uygulama kapsamı (5.2):**
  - Sistem girdileri ve çıktıları tanımlanacak
  - Membership function yapıları oluşturulacak
  - Fuzzy rule base ve inference mekanizması gerçekleştirilecek
  - Gerekli defuzzification yöntemi uygulanacak
  - Sistem farklı giriş değerleriyle test edilecek
  - Makaledeki **en az bir temel deney** yeniden gerçekleştirilecek
  - Sonuçlar referans çalışmanın sonuçlarıyla karşılaştırılacak

| Ölçüt | Puan |
|---|---|
| Referans yöntemin doğru modellenmesi | 6 |
| Fuzzy sistemin doğru gerçekleştirilmesi | 6 |
| Yazılımın çalışabilirliği | 6 |
| En az bir deneyin yeniden gerçekleştirilmesi | 5 |
| Sonuçların referans çalışmayla karşılaştırılması | 4 |
| Kod kalitesi ve tekrar üretilebilirlik | 3 |

> ⚠️ Bu proje FCM tabanlı (kural tabanlı Mamdani/Sugeno değil). "Rule base / defuzzification / membership function" maddelerinin FCM'deki karşılığı `docs/02_MAKALE_ANALIZI.md` §8'de eşlendi; **hocadan teyit** edilmeli (bkz. `docs/06_KARARLAR.md`).

## 6. Özgün katkı / geliştirme — 30 puan

Yeniden gerçekleştirmeden sonra mevcut sistem üzerinde katkı/değişiklik/yeni deneysel yaklaşım. Tamamen yeni algoritma ZORUNLU DEĞİL. Teknik/bilimsel gerekçe olmalı; etki deneysel değerlendirilmeli.

**Katkı türleri:** yeni input/output değişkeni · membership function türlerinin değiştirilmesi/karşılaştırılması · Mamdani–Sugeno veya Type-1–Type-2 karşılaştırması · farklı defuzzification yöntemlerinin karşılaştırılması · rule base değişikliği/optimizasyonu · yeni veri seti/senaryo · gürültü/robustness analizi · farklı optimizasyon veya ML yöntemleriyle karşılaştırma · parametre optimizasyonu veya ablation study · hesaplama maliyeti/performans optimizasyonu

**Baseline vs geliştirilen tablo (örnek şablon):**

| Performans Ölçütü | Baseline | Geliştirilen | Değişim |
|---|---|---|---|
| Accuracy | … | … | … |
| RMSE | … | … | … |
| Execution Time | … | … | … |

Geliştirilen yöntemin baseline'dan iyi olması zorunlu DEĞİL; iyileşme yoksa bilimsel olarak değerlendirilir, olası nedenler tartışılır.

| Ölçüt | Puan |
|---|---|
| Katkının bilimsel/teknik gerekçesi | 4 |
| Teknik gerçekleştirme | 8 |
| Deney tasarımı | 5 |
| Baseline ile adil karşılaştırma | 5 |
| Sonuçların analizi ve yorumlanması | 5 |
| Özgünlük / mühendislik değeri | 3 |

## 7–8. Teknik rapor — 8–12 sayfa (kaynakça hariç), IEEE kaynakça

Zorunlu bölümler (bu sırayla):
1. Introduction · 2. Related Work · 3. Theoretical Background · 4. Original Method · 5. Reproduction Methodology · 6. Proposed Extension · 7. Experimental Setup · 8. Results · 9. Discussion · 10. Limitations · 11. Conclusion · References
+ **Generative AI Usage Disclosure** (kısa bölüm, §15 gereği)

## 9. GitHub repository

Önerilen yapı (gerekirse değiştirilebilir):
```
fuzzy-logic-project/
├── README.md  LICENSE  requirements.txt  .gitignore
├── src/  data/
├── experiments/baseline/  experiments/proposed/
├── results/figures/  results/tables/
├── presentation/presentation.pdf
├── report/report.pdf
└── references/README.md
```
- Repo sürecin **commit geçmişiyle** izlenebilir olmalı; final haftasında tek seferde yükleme olmamalı.

## 10. README zorunlu başlıkları

Project Title · Student Information · Original Paper · Problem Description · Method · Fuzzy System Architecture · Dataset · Installation · Requirements · How to Run · Reproduction Experiments · Proposed Extension · Experimental Results · Limitations · References

## 11. Tekrar üretilebilirlik

`Repo klonla → Bağımlılıkları kur → Baseline çalıştır → Geliştirileni çalıştır → Sonuçları üret`. Kütüphane sürümleri belirtilir (requirements.txt). Veri repoda paylaşılamıyorsa kaynak + hazırlama adımları README'de. **API anahtarı/parola/token repoda paylaşılmaz.**

## 12. Rapor + GitHub puanı — 20

| Ölçüt | Puan |
|---|---|
| Akademik yapı ve anlatım | 4 |
| Literatür ve kaynak kullanımı | 3 |
| Yöntemin teknik açıklaması | 3 |
| Deneylerin ve sonuçların raporlanması | 3 |
| Tartışma ve sınırlılıkların değerlendirilmesi | 3 |
| GitHub organizasyonu ve README | 2 |
| Kod/veri/çalıştırılabilirlik | 2 |

## 13. Dönem içi checkpoint'ler

| # | Ad | İçerik |
|---|---|---|
| CP1 | Makale ve Problem Analizi | Problem, amaç, kullanılan BM yöntemi, girdi/çıktılar, temel deneysel yapı |
| CP2 | Uygulama Planı | Geliştirme ortamı, veri seti, membership yapıları, rule base, deney planı |
| CP3 | Baseline Sistem | Temel yöntem çalışır + ilk deney sonuçları |
| CP4 | Katkı Önerisi | Ne, neden değişecek; başarı nasıl ölçülecek |
| CP5 | Deneysel Sonuçlar | Baseline ve geliştirilen çalışır; karşılaştırmalı tablo/grafik |
| FINAL | Teslim ve Savunma | Sunum, canlı uygulama, sözlü savunma, rapor, GitHub |

> Checkpoint **tarihleri yönergede yok** → hocadan/Classroom'dan öğren ve `docs/04` içine yaz.

## 14. Canlı uygulama ve sözlü savunma

Demo canlı; hazır deneylere ek olarak **farklı giriş değerleri/yeni koşullar** denenebilir. Öğrenciden şunları açıklaması beklenir: kullanılan fuzzy rule'ların işlevi · membership function seçimleri · parametrelerin etkisi · algoritmalar · değişikliklerin gerekçesi · sonuçların nedenleri · kodun belirli bölümlerinin görevi · sınırlılıklar. **Teslim edilen kodun ve yöntemin açıklanabilir olması değerlendirmenin parçasıdır.**

## 15. Üretken YZ kullanımı

ChatGPT, Copilot vb. yardımcı araç olarak serbest; kod/bilgi/kaynak doğruluğu öğrencinin sorumluluğunda; teslim edilen her şey öğrenci tarafından anlaşılmış ve doğrulanmış olmalı. Raporda **"Generative AI Usage Disclosure"** bölümü (kod geliştirme, hata ayıklama, kavram açıklama, dil düzenleme, literatür yardımı vb. kullanıldı mı). **Doğrulanmamış / var olmayan kaynak kullanılmayacak.**

## 16. Akademik etik

Başka öğrencinin kodu/raporu kaynaksız kullanılamaz. İnternet/açık kaynak kod → kaynak belirt. Makale yazarlarının resmi kodu kullanılırsa rapor + repo'da açık belirt; öğrencinin kodu ile dış kod ayırt edilebilir olsun. **Var olmayan kaynak, yapılmamış deneyi yapılmış gibi gösterme, üretilmemiş sonuç raporlama = etik ihlal.**

## 17. Teslim çıktıları

Bilimsel makale analizi · Literatür araştırması · Baseline uygulama · Özgün katkı · Deneysel karşılaştırma · Grafik ve tablolar · Teknik rapor (8–12 sf) · Sunum · GitHub repo · Canlı demo · Sözlü savunma

## 18. Genel değerlendirme ilkesi

Sadece yüksek performans veya çalışan uygulama değerlendirilmez. Esas: problemin doğru anlaşılması, literatür, BM yöntemlerinin doğru uygulanması, referansın yeniden gerçekleştirilebilmesi, katkı, kontrollü deneyler, karşılaştırmalı değerlendirme, eleştirel yorum, teknik dokümantasyon, tekrar üretilebilirlik.

## 19. Takvim

| Aşama | Tarih | Açıklama |
|---|---|---|
| **Proje son teslimi** | **27.10.2026** | Tüm doküman/bağlantılar Classroom'a eksiksiz yüklenir |
| **Sunumların başlangıcı** | **03.11.2026** | Son tesliminden sonraki ilk ders; sunum + sözlü savunma |

- Classroom'daki ilgili başlıklara dosya ve bağlantılar yüklenir; dosyaların açılabilir/okunabilir/doğru sürümde olması **öğrencinin sorumluluğu**.

## 20. Teslim kontrol listesi (27.10 öncesi)

- [ ] report.pdf (8–12 sf, IEEE kaynakça, GenAI Disclosure dahil) Classroom'da, açılıyor
- [ ] presentation.pdf (ve varsa .pptx) yüklendi
- [ ] GitHub repo bağlantısı yüklendi; repo public/erişilebilir; commit geçmişi düzenli
- [ ] README tüm zorunlu başlıkları içeriyor
- [ ] requirements.txt + temiz ortamda "klonla→kur→çalıştır" denendi
- [ ] Repoda gizli bilgi yok
- [ ] Tüm atıflar gerçek ve doğrulanmış
- [ ] Raporlanan her sayı bizim çalıştırmamızdan geliyor (veya "makaleden" diye etiketli)
