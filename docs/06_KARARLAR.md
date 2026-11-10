# 06 — Kararlar ve Açık Sorular

Durumlar: **Alındı** (öğrenci onayladı/belirtti) · **Öneri** (Claude önerdi, onay bekliyor) · **Açık** (bilgi/teyit gerekli)
Yeni karar → yeni satır. Claude "Öneri/Açık" kararları öğrenci onaylamadan kesinleştirmez.

## A. Alınan kararlar

| ID | Karar | Tarih |
|---|---|---|
| D-001 | Proje yönergeye (puan tablolarına) birebir uygun yürütülecek | 18.10.2026 |
| D-002 | Referans makale: Wu et al. 2024, ESWA 256:124943 (öğrencinin sorumlu olduğu makale) | 18.10.2026 |
| D-003 | Uygulama Claude Code ile terminalde yürütülecek; bağlam bu `docs/` dosyaları ve `CLAUDE.md` ile taşınır | 18.10.2026 |
| D-023 | Öğrenci, B bölümündeki önerileri (D-005, D-007…D-016) "en mantıklı şekilde" uygulama yetkisini Claude'a devretti → hepsi önerilen haliyle kabul edildi (D-014: varsayılan `floor`). Hocaya bağlı C maddeleri yine **Açık**; hoca cevabıyla çelişirse güncellenir. D-006 (katkı) seçimi CP4'te kesinleşir; çalışma varsayımı C1+C2 | 10.11.2026 |
| D-024 | Python ortamı: **Python 3.12** ile `.venv` (sistemdeki 3.13 yerine; dtcwt/numba uyumluluğu için daha güvenli) | 10.11.2026 |
| D-025 | GitHub: makinede `gh` CLI yok → repo şimdilik yalnız yerel git; uzak repo öğrenci tarafından oluşturulup `git remote add origin …` ile bağlanacak | 10.11.2026 |

## B. Öneriler (onay bekliyor)

| ID | Konu | Öneri | Gerekçe |
|---|---|---|---|
| D-005 | **MRR** | (1) Baseline FCM (Alg.1) tam; (2) ASRFCM-CSI tam: Alg.2 (ξ) + DTCWT non-local (ϑ) + adaptif α,β,γ + sparse FCM (Alg.3); (3) yeniden üretim deneyi: sy1–3 × {%1,5,10,15} karışık gürültü, metrikler V_PC/V_PE/ACC/F/NMI/Kappa + iterasyon; (4) Tablo 1 ablasyonu; (5) BSDS500'den 8 görüntü (%5 gürültü) | Makalenin tam çekirdeği ve en az bir temel deneyi karşılar; 9 günde yapılabilir. Hocadan onay alınmalı |
| D-006 | **Özgün katkı** (öğrenci seçecek; aşağıda aday listesi) | Birincil: **C1+C2 paketi** (aşağıda) | Yönerge katkı türleriyle uyumlu, ucuz ve savunması kolay, makalenin boşluğuna (gürültü türüne göre analiz, ödül oranı varsayımı, K belirleme) dokunur |
| D-007 | Dil | Kod/commit/README/rapor: İngilizce; sohbet ve iç dokümanlar: Türkçe | Yönergedeki rapor başlıkları İngilizce; hocadan teyit |
| D-008 | Görüntü boyutu ve K | sy1–3: 256×256 üret; K: sy1=2, sy2=3, sy3=3 (tahmin, Fig.9/14/16/18'e göre). BSDS500: K=GT segment sayısına göre (makalede görüntü başına K belirtilmemiş → görüntü başına 2–3, ayrıca raporla) | Makale K'yı açıkça vermiyor |
| D-009 | Karışık gürültü tanımı | Her gerçekleşimde piksellerin p oranı bozulur; bozulan pikseller 3 türe eşit bölünür: Gaussian (sabit std; değeri Faz 2'de belirle, raporla), tuz-biber (eşit tuz/biber), multiplicative (speckle; varyans Faz 2'de belirle, raporla). Ayrıca 3 türün tek başına versiyonu | Makalede kesin tanım yok; aynı tanım tüm yöntemlere uygulanır |
| D-010 | DTCWT karmaşık katsayıları | Her yön alt-görüntüsüne (karmaşık) NLM'yi gerçek ve sanal bileşen için ayrı ayrı (aynı ağırlıklarla) uygula; ağırlıkları genlikten hesapla; 1 seviye | Makale ayrıntı vermiyor; ters DTCWT için karmaşık yapıyı koru |
| D-011 | Hard threshold boş sütun | Sütun tamamen sıfırlanırsa argmax elemanı 1 yap (`empty_col_policy="argmax"`); deviation raporlanacak | Makale koşulu (`√δ ≤ min max η`) genelde sağlanmıyor; 0/0'dan kaçınmak için |
| D-012 | Eq. (10) | y_q ile uygula (y_j yazım hatası olarak yorumlanır) | Klasik NLM tanımı |
| D-013 | Eq. (15)(16) | Varsayılan: makaledeki gibi `k·exp(y_j − ξ_j)+eps`; varyant: `k·exp(|y_j − ξ_j|)+eps`; ikisini ablasyonla karşılaştır | İşaret belirsizliği |
| D-014 | Ödül kümesi boyutu | Varsayılan `floor(0.618·(N_R−1))` (Fig.1: 8 komşu→4; PDF'te doğrulandı, round 5 verir); `ceil` (metin) ablasyonda | Metin ceil diyor, şekil 4 gösteriyor |
| D-015 | Seed ve tekrar | ≥10 seed (0–9), ortalama±std | Adil karşılaştırma |
| D-016 | Yayıncı PDF'i | `references/papers/*.pdf` yerelde dursun, **git'e eklenmesin** (.gitignore) | Telif; repo public olabilir |

### Özgün katkı adayları (D-006 detay)

| Kod | Katkı | Yönerge karşılığı | Hipotez | Maliyet |
|---|---|---|---|---|
| **C1** | **Gürültü türü/yoğunluk bazlı robustness analizi** (Gaussian, S&P, multiplicative ayrı + karışık; %0–20) — makalede yalnız karışık gürültü var | "Gürültü/robustness analizi" | ASRFCM bazı türlerde (ör. S&P) belirgin daha iyi, multiplicative'de zayıf; FCM ile fark türe göre değişir | Düşük |
| **C2** | **Ablasyon + parametre**: ödül oranı ρ (0.618 altın oran vs 0.5/0.7/0.8), σ, w, δ, ΔG varyantı (D-013), hard-threshold politikası | "Parametre optimizasyonu veya ablation study" | Altın oran optimal değil; sonuçlar ρ'ya zayıf duyarlı | Düşük |
| C3 | **Otomatik K seçimi** (V_PC/V_PE/Xie-Beni ile) — makalenin 1. sınırlılığı | "Yeni giriş/çıkış değişkeni", "rule/optimizasyon" | V_PC tabanlı K seçimi sentetikte doğru K'yı bulur, gerçekte zorlanır | Orta |
| C4 | **Hız**: yerel-olmayan işlemi alt-örnekleme/kısıtlı arama ile hızlandırma; süre–kalite eğrisi | "Hesaplama maliyeti ve performans optimizasyonu" | S=15→9 süreyi çok azaltır, ACC az düşer | Orta |
| C5 | Defuzzification karşılaştırması: argmax vs eşikli/yumuşak (ör. ağırlıklı oy, `u` ile komşu düzeltme) | "Farklı defuzzification yöntemleri" | Seyrek U'da argmax yeterli; FCM'de fark var | Düşük |
| C6 | Ek veri seti (ör. tıbbi/uzaktan algılama alt kümesi) | "Yeni veri seti" | Genelleme sentetikteki kadar iyi değil | Orta (veri bulma) |

**Önerilen paket: C1 + C2** (+ süre kalırsa C4). Gerekçe: 9 günlük sürede güvenli, deney tasarımı güçlü, "baseline ile adil karşılaştırma" ve "analiz" puanlarına doğrudan hizmet eder, başarısız sonuç bile yorumlanabilir. *Karar CP4'te öğrencinindir.*

## C. Açık sorular (hocadan teyit)

| ID | Soru | Neden önemli | Durum |
|---|---|---|---|
| D-004 | FCM tabanlı bu makale "fuzzy system" istekleriyle (membership, rule base, inference, defuzzification) uyumlu sayılacak mı? Eşleme (`02 §8`) kabul edilir mi? | Uygulama puanı (6+6) | **Açık** |
| D-017 | MRR resmi olarak ne? (D-005 önerisi yeterli mi?) | Uygulama puanı | **Açık** |
| D-018 | Checkpoint tarihleri ve teslim biçimi (her CP için ne yüklenecek)? | Takvim | **Açık** |
| D-019 | Rapor dili (İngilizce mi Türkçe mi)? Şablon (IEEE konferans/dergi)? | Rapor | **Açık** |
| D-020 | Makalenin resmi kodu varsa kullanım izni/şekli? (Biz sıfırdan yazıyoruz) | Etik | **Açık** |
| D-021 | Sunum biçimi (PPTX/PDF), canlı demo için kendi laptop mu? | Sunum | **Açık** |
| D-022 | Öğrenci bilgisi (ad-soyad, numara) README için | README | **Açık** |
