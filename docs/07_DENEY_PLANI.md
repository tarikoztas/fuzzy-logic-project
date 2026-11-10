# 07 — Deney Planı

Amaç: (1) makalenin temel deneyini yeniden üretmek (Uygulama 30p), (2) katkının etkisini baseline ile adil karşılaştırmak (Katkı 30p), (3) sonuçları analiz etmek.

## 1. Genel ayarlar

| Ayar | Değer |
|---|---|
| Görüntüler | sy1, sy2, sy3 (256×256, kendi ürettiğimiz; Fig.9'a benzer) · BSDS500 8 görüntü: 100007, 118035, 167062, 201080, 241004, 42049, 67079, 86016 |
| Gürültü | karışık (Gaussian + tuz-biber + multiplicative, eşit oran) %1/5/10/15 (sentetik), %5 (BSDS), kararlılık için %0–20; ayrıca C1 için her tür tek başına |
| Seed | 0–9 (gürültü gerçekleşimi sabit: seed → aynı gürültü; kümeleme başlatması da seed'e bağlı) |
| K | sy1=2, sy2=3, sy3=3; BSDS: görüntü başına belirle ve raporla (D-008) |
| Ortak | m=2, ε=1e-6, T=100 |
| ASRFCM parametreleri | w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4 (makale) |
| Metrikler | V_PC, V_PE, ACC, F-score, NMI, Kappa, iterasyon sayısı, süre (ön-işleme / kümeleme ayrı) |
| Çıktılar | `results/tables/*.csv`, `results/figures/*` (betikle üretilir) |

## 2. Deney listesi

### E0 — Doğruluk/Birim kontrolleri (CP3 öncesi)
Fig.1–3 örnek 3×3 hesapları; DTCWT gidiş-dönüş; FCM'nin bilinen basit veride doğruluğu. **Çıktı:** testler yeşil.

### E1 — Baseline FCM yeniden üretimi (CP3)
sy1–3 × %1/5/10/15, 10 seed. Bizim FCM sonuçlarını makale Tablo 2–8 FCM sütunuyla (`paper_reported_fcm_vs_ours.csv`) karşılaştır.
**Beklenti:** eğilim aynı (gürültü↑ → V_PC↓, ACC↓); sayılar yaklaşık (görüntü/gürültü tanımı farkı).

### E2 — ASRFCM-CSI yeniden üretimi (CP3/CP5) — *makaledeki en az bir temel deney*
Aynı ızgara. Bizim "Ours" vs makale "Ours" (Tablo 2–8). **Çıktı:** karşılaştırma tablosu + fark analizi (neden farklı).

### E3 — Ablasyon (Tablo 1 yeniden üretimi)
8 kombinasyon (yerel/yerel-olmayan/seyrek reg.) × sy (%5 gürültü), 10 seed. **Çıktı:** Tablo 1 benzeri + makale yan yana.
Özel dikkat: yalnız-seyrek satırında iterasyonun neden arttığı (24) bizde tekrar ediyor mu?

### E4 — Parametre duyarlılığı (Fig.10–13 yeniden)
σ∈{0.05…0.9}, w∈{3,5,7,9}, k∈{1,5,10,15,20,25,30}, δ∈{0,0.02,…,0.1,0.2,0.4,0.6,0.8} × sy1–3 (%5). Metrik: V_PC, V_PE, ACC, iterasyon, süre.

### E5 — Katkı deneyleri (CP4→CP5)
**C1 (Robustness):** gürültü türü {Gaussian, S&P, multiplicative, karışık} × yoğunluk {0,1,5,10,15,20%} × yöntem {FCM, ASRFCM(makale)} × sy1–3 (+ BSDS alt küme).
**C2 (Ablasyon/parametre):** ödül oranı ρ∈{0.5,0.618,0.7,0.8}; yuvarlama {ceil,round,floor}; ΔG {işaretli, mutlak}; boş sütun politikası {argmax, η koru}; tek değişken değişir.
**(Opsiyonel) C4 (Hız):** S∈{5,9,15}, alt-örnekleme; süre–ACC eğrisi.
**Çıktı:** yönerge 6.2 biçiminde baseline-vs-geliştirilen tablo (Metrik | Baseline | Geliştirilen | Değişim) + figürler.

### E6 — Gerçek görüntüler (BSDS500, %5)
8 görüntü × {FCM, ASRFCM, katkılı}; ACC/F/NMI/Kappa/V_PC/V_PE; görsel panel (orijinal / gürültülü / her yöntem / GT). Makale Tablo 9 (FCM, Ours) ile kıyas.

### E7 — Süre ve karmaşıklık
Görüntü boyutu {128²,256²,481×321} × yöntem; ön-işleme vs kümeleme süresi; teorik N·S²·w² ile ölçülen süre ilişkisi.

## 3. Karşılaştırma tablosu şablonu (yönerge §6.2)

| Metrik | Baseline | Geliştirilen | Değişim (Δ, %) |
|---|---|---|---|
| ACC (%) | μ ± σ | μ ± σ | … |
| Kappa (%) | … | … | … |
| V_PC (%) | … | … | … |
| Iterasyon | … | … | … |
| Süre (s) | … | … | … |

Her tabloda: görüntü, gürültü, K, seed sayısı, kaynak etiketi (bizim/makale).

## 4. Kabul ölçütleri (iç hedef)

- E2: Ours > FCM tüm gürültü seviyelerinde ve metriklerin çoğunda; V_PC>%95 (sy, %≤10) hedeflenir — **tutmazsa neden araştırılır, sonuç uydurulmaz**.
- Her deneyin CSV'si ve üretim komutu README "Reproduction Experiments" bölümünde.
- Beklenmedik/negatif sonuç → `docs/06_KARARLAR.md` + Discussion bölümüne.

## 5. Zaman bütçesi (öneri)

E0–E2: 20–22.10 · E3–E4: 22–23.10 · E5: 23–24.10 · E6–E7: 24–25.10 · Rapor yazımı paralel.
Süre kısıtında öncelik: E0, E1, E2, E3, E5(C1+C2), E6; sonra E4, E7.
