# 09 — Sunum ve Sözlü Savunma Planı (20 puan)

15–20 dk sunum + ~5 dk soru-cevap/demo. Yönergenin 8 puan kalemi → slayt blokları.

## Slayt akışı (öneri ≈ 18 slayt)

| # | Slayt | Süre | Puan kalemi |
|---|---|---|---|
| 1 | Başlık, ad, ders, makale künyesi | 0:15 | — |
| 2 | Problem: gürültülü görüntü segmentasyonu; gerçek uygulamalar (uzaktan algılama, tıp) | 1:00 | Problem/motivasyon (2) |
| 3 | Neden bulanık mantık / FCM? Hard vs soft kümeleme; FCM'nin gürültü zayıflığı | 1:00 | Motivasyon |
| 4 | Literatür haritası (BCFCM→FGFCM→FLICM→FRFCM→SRFCM→FSC_LNML…) + güncel çalışmalar | 2:00 | Literatür (3) |
| 5 | Teori 1: fuzzy set, membership, FCM amaç fonksiyonu + Lagrange çözümü | 1:30 | Teori (3) |
| 6 | Teori 2: ℓ0 seyreklik/hard threshold, DTCWT (neden shift-invariant), defuzzification (argmax) | 1:30 | Teori |
| 7 | Makale yöntemi: genel mimari (akış şeması) | 1:00 | Yöntem (4) |
| 8 | Yerel işlem: ödül/ceza kümesi + altın oran, Sg/Ss/SS, ξ (3×3 örnekle) | 1:30 | Yöntem |
| 9 | Dalgacık alanında non-local (ϑ) ve adaptif α,β,γ | 1:30 | Yöntem |
| 10 | Seyrek FCM: üç adım (Lagrange → hard threshold → normalize) | 1:00 | Yöntem |
| 11 | Deney kurulumu: veri, gürültü, metrikler, karşılaştırılan yöntemler | 1:00 | Deney/veri (2) |
| 12 | Makalenin sonuçları (tablo/grafik) + eleştirel not | 1:00 | Sonuç analizi (2) |
| 13 | Bizim yeniden gerçekleştirmemiz: mimari, ne yaptık, sapmalar | 1:00 | Uygulama |
| 14 | Yeniden üretim sonuçları: bizim vs makale | 1:00 | Sonuç analizi |
| 15 | Özgün katkımız: gerekçe, hipotez, tasarım | 1:00 | Sınırlılık/geliştirme (2) |
| 16 | Katkı sonuçları: baseline vs geliştirilen tablo + figür | 1:30 | Sonuç analizi |
| 17 | Sınırlılıklar, başarısızlık durumları, gelecek çalışma | 1:00 | Sınırlılıklar (2) |
| 18 | Sonuç + canlı demo geçişi + teşekkür | 0:30 | Sunum kalitesi (2) |

Toplam ≈ 20 dk — kısaltmak gerekirse 5, 6, 9'u sıkıştır.

## Canlı demo planı (yönerge §14: farklı giriş değerleri istenebilir)

Hazırla: `notebooks/demo.ipynb` (veya terminal betiği) — parametre girişleriyle çalışır.
1. Görüntü seç (sy2 / BSDS bir görüntü) → gürültü türü + yoğunluk gir → FCM ve ASRFCM'yi çalıştır (≤1–2 dk; önbellek hazır, küçük görüntü).
2. Yan yana panel + metrik tablosu göster.
3. Hocanın isteği: "σ'yı 0.8 yap / δ=0 yap / k'yı 1 yap" → sonucu yorumla.
4. **Yedek:** internet/yavaş çalışma riskine karşı önceden üretilmiş figürleri hazır tut.

## Savunma soru bankası (yönerge §14 maddelerine göre) — çalış

**Fuzzy rule / membership**
- FCM'de "kural" nerede? (Cevap: açık IF-THEN yok; amaç fonksiyonu minimizasyonu; üyelik = merkeze yakınlık.)
- Üyelik derecesi nasıl hesaplanıyor? m=2 ne yapıyor? m→1 ve m→∞ ne olur?
- Sentezlenen "defuzzification" nedir bu projede? Neden argmax?

**Parametreler**
- σ'yı artırırsam ne olur? 0 olursa? (ödül/ceza ayrımı ortadan kalkar.)
- Neden altın oran? Başka oranla ne olur? (Kendi C2 sonucumuzla cevapla.)
- w=5 neden? S=15 neden? g, υ ne işe yarar?
- k (gürültü bastırma faktörü) α,β,γ'yı nasıl etkiler?
- δ büyürse seyreklik/iterasyon/doğruluk ne olur? Hard threshold ne işe yarıyor?

**Algoritma/kod**
- ξ'yi adım adım anlat (sıralama→ödül/ceza→Sg→Ss→SS→ξ).
- DTCWT neden DWT değil? 7 alt-görüntü neden? Ters dönüş neden gerekli?
- c ve η formülleri nereden geliyor? (Lagrange; Ek A.)
- Normalizasyon neden gerekli? Boş sütunu nasıl ele aldınız? (D-011)
- Bu fonksiyonun görevi nedir? (kodun herhangi bir yerinden)

**Sonuç/sınırlılık**
- Neden sonuçlarınız makaleden farklı? (sy görüntüleri, gürültü tanımı, seed, protokol.)
- Katkınız baseline'ı iyileştirdi mi? Neden/neden olmadı?
- Ne zaman başarısız oluyor? (K yanlış; çok yüksek gürültü; gerçek görüntülerde zayıf Kappa.)
- Karmaşıklık? Süre neden yüksek? Nasıl azaltılır?
- GenAI'yi nasıl kullandın? Neyi doğruladın?
