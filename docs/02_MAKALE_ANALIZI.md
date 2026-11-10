# 02 — Referans Makale Analizi

**Makale:** J. Wu, X. Wang, Y. Liu, C. Fang — *Adaptive sparse regularized fuzzy clustering noise image segmentation algorithm based on complementary spatial information*, Expert Systems With Applications 256 (2024) 124943. DOI: 10.1016/j.eswa.2024.124943
**Kurum:** Lanzhou Jiaotong University. **Kısaltma (bu projede):** ASRFCM-CSI (makalede yöntemin resmi bir kısaltması yok; "Ours" olarak geçer).
**Orijinal PDF:** `references/papers/Wu_2024_ASRFCM_ESWA.pdf` (26 sayfa). Sayfa numaraları aşağıda PDF sayfalarıdır.

> Bu özet PDF'ten çıkarılmıştır. Denklem numaraları makaledeki numaralardır. Kodlamadan önce §9 (belirsizlikler) mutlaka okunmalı.

---

## 1. Problem ve motivasyon

- Görüntü segmentasyonu: görüntüyü renk/parlaklık/doku gibi özniteliklere göre bölgelere ayırma.
- Klasik (hard) kümeleme: piksel tek kümeye ait. **FCM** (soft): piksel birden fazla kümeye üyelik derecesiyle ait.
- Sorun: Klasik FCM **uzamsal bilgiyi kullanmaz** → gürültüye duyarlı.
- Mevcut FCM türevlerinin eksikleri (makalenin iddiası):
  1. Yerel uzamsal işlem **ortalama (averaging)** mantığına dayanır: komşuluktaki tüm pikseller eşit önemde sayılır; oysa gürültü pikselleri farklı derecede bozar.
  2. Yerel-olmayan (non-local) işlemler **uzamsal alanda** yapılır → detay/kenar kaybı olabilir.
  3. Hem yerel hem yerel-olmayan bilgiyi **birlikte** kullanan yöntem az.
- Uygulama alanları: uzaktan algılama, tıbbi görüntü, hedef tanıma, insan akışı sayımı, kaynak araştırması vb.

## 2. Katkılar (makalenin 4 iddiası)

1. **Tamamlayıcı uzamsal bilgi içeren FCM amaç fonksiyonu:** yeni yerel işlem (ödül/ceza kümeleri, non-averaging) + dalgacık (DTCWT) alanında yerel-olmayan işlem.
2. **Adaptif kısıt katsayıları (α_j, β_j, γ_j):** orijinal piksel ile yerel/yerel-olmayan bilgi arasındaki mutlak farktan otomatik hesaplanır (elle parametre ayarı yok).
3. **Seyrek (ℓ0) düzenlileştirme:** üyelik matrisi güçlü seyrek olur → iterasyon sayısı azalır.
4. **Üç adımlı iteratif çözüm:** Lagrange çarpanı → hard threshold → normalizasyon.

## 3. Teorik altyapı (makalenin §2)

### 3.1 Klasik FCM
```
J_FCM = Σ_{i=1..K} Σ_{j=1..N} (u_ij)^m ||y_j − c_i||² ,   Σ_i u_ij = 1                      (1)
u_ij  = 1 / Σ_{r=1..K} ( ||y_j − c_i|| / ||y_j − c_r|| )^{2/(m−1)}                          (2)
c_i   = Σ_j (u_ij)^m y_j / Σ_j (u_ij)^m                                                      (3)
```
K: küme sayısı, N: piksel sayısı, m: bulanıklık indeksi (=2), y_j: j. pikselin gri değeri.
**Algoritma 1 (FCM):** görüntüyü [0,1]'e normalize et → U'yu rastgele başlat → tekrarla {c (3), U (2), J (1), |J^(a) − J^(a−1)| ≤ ε veya a>T ise dur}.

### 3.2 DTCWT (Dual-Tree Complex Wavelet Transform, Kingsbury 2001)
- İki bağımsız DWT ağacı (Tree A gerçek, Tree B sanal katsayı) → **kaymaya (shift) karşı daha az duyarlı**, yönsel.
- Görüntü: 1 düşük frekanslı yaklaşım alt-görüntüsü + **6 yüksek frekanslı detay alt-görüntüsü** (yönler ±π/12, ±π/4, ±5π/12).

## 4. Yöntem (makalenin §3)

### 4.1 Yeni yerel uzamsal işlem — Algoritma 2 (ξ_i)
Her piksel için w×w komşuluk:
1. Komşuları gri değere göre artan sırala (merkez hariç).
2. **Altın oran** (0.618) ile **ortadaki** ⌈0.618·(N_R − 1)⌉ piksel = **ödül kümesi (reward)**; uçlardaki (gürültü olma olasılığı yüksek) kalanlar = **ceza kümesi (penalty)**. N_R: komşuluk eleman sayısı.
3. Gri benzerlik:
```
Sg_ij = (1+σ)·S_ij  , j ∈ N^R_i
        (1−σ)·S_ij  , j ∈ N^P_i                                                              (5)
S_ij  = exp( −||x_j − x_i||² / τ_i² ) , j≠i ;  0 , j=i                                       (6)
τ_i   = sqrt( Σ_{p∈N} ||x_p − x_i||² / N_R )
```
4. Uzamsal benzerlik: `Ss_ij = exp(−d_ij)`, d_ij = piksel koordinatları arası Öklid uzaklığı (7)
5. Nihai benzerlik: `SS_ij = Sg_ij · Ss_ij (j≠i), 0 (j=i)` (8)
6. Yerel bilgi: `ξ_i = Σ_{j∈N_i} SS_ij x_j / Σ_{j∈N_i} SS_ij` (9)

Makale, benzer ölçütlerle (Cai 2007: S_ij ve Zhao 2019: SS'_ij) farkı Fig. 2–3'te 3×3'lük sayısal örnekle gösterir (merkez piksel gerçek 170; S→156/177, SS'→163/178, SS (ours)→166/175).

### 4.2 Dalgacık alanında yerel-olmayan işlem (ϑ_j)
1. Görüntüyü DTCWT ile 1 yaklaşım + 6 detay alt-görüntüsüne ayır.
2. **Her bir (toplam 7) alt-görüntüye** yerel-olmayan (NLM benzeri) işlem uygula:
```
r_j = (1/Z_j) Σ_{y_q ∈ R_j, q≠j} y_q · exp( − Gauss[ M(y_q) − M(y_j) ]²_{2,υ} / (g·w²) )     (10)   [bkz. §9-3: makalede y_j yazıyor]
Z_j = Σ_{y_q ∈ R_j, q≠j} exp( − Gauss[ M(y_q) − M(y_j) ]²_{2,υ} / (g·w²) )                    (11)
```
R_j: S×S arama penceresi; M(·): w×w komşuluk penceresi; Gauss[...]: υ standart sapmalı Gauss ağırlıklı kare farkı toplamı; g: düzgünlük parametresi.
3. Ters DTCWT ile yeniden oluştur → ϑ_j (nihai yerel-olmayan bilgi).

Makale (Fig. 5) bilateral filtre, klasik NLM ve morfolojik rekonstrüksiyon ile kıyaslayıp dalgacık tabanlısının kenarı daha iyi koruyarak gürültüyü bastırdığını gösterir (görsel kıyas).

### 4.3 Tamamlayıcı bilgili FCM amaç fonksiyonu
```
J_m = Σ_i Σ_j (u_ij)^m ( α_j ||y_j − c_i||² + β_j ||ξ_j − c_i||² + γ_j ||ϑ_j − c_i||² )     (12)
```
Gürültü fazlaysa: orijinal görüntüye güven azalmalı (α küçük), düzeltilmiş bilgilere (ξ, ϑ) güven artmalı (β, γ büyük); az gürültüde tersi.

### 4.4 Adaptif katsayılar
```
ΔG1 = |y_j − ξ_j| + eps ;  ΔG2 = |y_j − ϑ_j| + eps                                           (13)(14)
ΔG1 = k·exp( y_j − ξ_j ) + eps ;  ΔG2 = k·exp( y_j − ϑ_j ) + eps                            (15)(16)   [bkz. §9-4]
α_j = 1/(ΔG1 + ΔG2) ;  β_j = ΔG1 ;  γ_j = ΔG2                                               (17)(18)(19)
```
k: gürültü bastırma faktörü. Fikir: gürültü çoksa fark büyür → β,γ büyür, α küçülür.

### 4.5 Seyrek düzenlileştirmeli FCM (§3.4)
```
J_m = Σ_i Σ_j (u_ij)^m ( α_j||y_j−c_i||² + β_j||ξ_j−c_i||² + γ_j||ϑ_j−c_i||² ) + δ·||U||_ℓ0   (20)
||U||_ℓ0 = Σ_i Σ_j ||u_ij||_0 ,  ||u||_0 = 1 (u≠0) / 0 (u=0)                                  (21)(22)
```
δ: seyreklik faktörü. **Üç adımlı çözüm (Wang et al. 2021 çerçevesi):**
- **Adım 1** — Lagrange ile "kaba" üyelik η ve merkezler C (sparsity yok, Eq. 23; türetim Ek A):
```
η_ij = 1 / Σ_r ( d_ij / d_rj )^{1/(m−1)} ,  d_ij = α_j||y_j−c_i||² + β_j||ξ_j−c_i||² + γ_j||ϑ_j−c_i||²   (28)
c_i  = Σ_j (α_j y_j + β_j ξ_j + γ_j ϑ_j)(η_ij)^m / Σ_j (α_j + β_j + γ_j)(η_ij)^m               (29)
```
- **Adım 2** — Hard threshold: `Ũ = hard_δ(η)`; `ũ_ij = η_ij (η_ij ≥ √δ), 0 (η_ij < √δ)` (24–26); makale ayrıca `0 < √δ ≤ min_j max_i η_ij` koşulunu belirtir.
- **Adım 3** — Normalizasyon: `U = normalize(Ũ)` (27) (her sütun toplamı 1).

Etki (Fig. 6–7): FCM üyelikleri [0,1] arası yoğun; ℓ0'lı sürüm seyrek (çoğu 0/1) ve daha az iterasyonla yakınsar (örnekte ~8 iterasyon).

### 4.6 Tam algoritma — Algoritma 3 (Fig. 8 akış şeması)
Girdiler: gürültülü görüntü I; K; w; S; g; σ; k; δ; m; T; ε.
1. I'yi [0,1]'e normalize et. 2. ξ_j'yi Algoritma 2 ile hesapla. 3. I'yi DTCWT ile 1+6 alt-görüntüye ayır. 4. 7 alt-görüntüye yerel-olmayan işlem (10)(11). 5. Ters DTCWT → ϑ_j. 6. α_j, β_j, γ_j (13)–(19). 7. U'yu rastgele başlat. 8. a=1.
9. **Tekrarla:** 9.1 c_i (29) → 9.2 η_ij (28) → 9.3 hard threshold (24–26) → 9.4 normalize (27) → 9.5 J_m (20) → 9.6 a←a+1 → 9.7 `|J^(a) − J^(a−1)| ≤ ε` veya a>T ise dur.
Çıktı: U, c.

### 4.7 Karmaşıklık (§3.5)
Makale adım sayısı: `5N + N·w² + 5t·K·N + 7·N·S²·w²` (makale §3.5'te önce `5tKN` (t = yakınsama iterasyonu) sonra `5TKN` yazıyor, Tablo 11'de de `5TKN`; iki yazım da PDF'te var) ve "tüm değişkenler n yapılınca" **O(n⁵)** der (FCM O(n³), ADFLICM/DSFCM_N/FSC_LNML de O(n⁵)). *(Bu soyutlama kaba — bkz. §9-7; raporda gerçek ölçülen süreyi ayrıca ver.)*

## 5. Deneysel kurulum (makalenin §4)

- **Karşılaştırılan yöntemler (9):** FCM, FGFCM, ADFLICM, FRFCM, DSFCM_N, FCM_SICM, SRFCM, CGFFCM, FSC_LNML (+ Ours).
- **Veri setleri:** 3 sentetik görüntü (sy1, sy2, sy3; Fig. 9) · BSDS500'den 8 gerçek görüntü (100007, 118035, 167062, 201080, 241004, 42049, 67079, 86016; Fig. 22) · genelleme için AID (uzaktan algılama), MSRC, NASA Earth Observation, COCO (Tablo 10).
- **Gürültü (§4.3):** **karışık gürültü** = eşit oranlarda **Gaussian + tuz-biber + çarpımsal (multiplicative)**. Yoğunluklar: sentetikte %1, 5, 10, 15; gerçek görüntülerde %5 (kararlılık analizinde %0–20).
- **Ortak parametreler:** ε=1e-6, T=100, m=2.
- **Önerilen yöntem parametreleri:** yerel pencere **w=5** (⚠ §4.1 metni w=7 diyor, §4.4 w=5 seçiyor — bkz. §9-13), yerel-olmayan arama penceresi **S=15**, Gauss std **υ=4**, düzgünlük **g=10**, ödül faktörü **σ=0.3**, gürültü bastırma **k=15**, seyreklik **δ=0.4** (parametre duyarlılık analizi §4.4: σ∈(0.2,0.4) kararlı; w=5 hız/kalite dengesi; k>5 kararlı, k=15 en az iterasyon; δ=0.4).
- **Metrikler (Eq. 30–35):**
```
V_PC = (1/N) ΣΣ u_ij² ×100%   (büyük=iyi)      V_PE = −(1/N) ΣΣ u_ij ln(u_ij) ×100%   (küçük=iyi)
ACC  = Σ_i Num_i / N ×100%                      F    = 2TP / (2TP + FN + FP)
NMI  = 2·MI(I1,I2) / (H(I1)+H(I2))              Kappa = (p0 − pe)/(1 − pe)
```
+ iterasyon sayısı, çalışma süresi.

## 6. Makalede raporlanan temel sonuçlar (hedef değerler — makaleden aktarılmıştır)

> Sayılar PDF Tablo 1–9'dan elle aktarıldı. **Raporda "makalede raporlanan" etiketiyle kullan; kendi sonuçlarımızla karıştırma.** Makine-okunur kopya: `results/tables/paper_reported_fcm_vs_ours.csv`.

### 6.1 Ablasyon (Tablo 1; sy görüntüsü, %5 karışık gürültü)
| Yerel | Yerel-olmayan | Seyrek reg. | V_PC | V_PE | ACC | F | NMI | Kappa | İter. |
|---|---|---|---|---|---|---|---|---|---|
| ✗ | ✗ | ✗ | 70.58 | 51.85 | 75.10 | 81.09 | 43.35 | 44.38 | 20 |
| ✓ | ✗ | ✗ | 87.51 | 22.98 | 82.26 | 78.51 | 48.47 | 60.48 | 17 |
| ✗ | ✓ | ✗ | 95.83 | 9.48 | 99.47 | 99.34 | 96.53 | 98.86 | 13 |
| ✗ | ✗ | ✓ | 94.74 | 7.47 | 82.48 | 78.60 | 48.78 | 60.96 | 24 |
| ✓ | ✓ | ✗ | 96.08 | 8.80 | 99.50 | 99.34 | 96.57 | 98.88 | 12 |
| ✓ | ✗ | ✓ | 94.99 | 7.15 | 78.49 | 72.52 | 48.30 | 52.00 | 19 |
| ✗ | ✓ | ✓ | 99.24 | 1.08 | 99.42 | 99.26 | 96.18 | 98.72 | 13 |
| ✓ | ✓ | ✓ | 99.26 | 1.05 | 99.52 | 99.40 | 96.56 | 98.89 | 11 |

Makale yorumu: yerel-olmayan işlem en etkili bileşen; seyrek reg. iterasyonu düşürür. (Not: yalnız-seyrek satırda iterasyon 24'e **çıkıyor** — metindeki "sparse reg. iterasyonu azaltır" ifadesiyle tam örtüşmüyor; raporda eleştirel değerlendirme için not.)

### 6.2 Sentetik görüntüler: FCM vs Ours (Tablo 2–8)
Satırlar: sy1/sy2/sy3 × gürültü %1/5/10/15.

| Metrik | Yöntem | sy1 (1/5/10/15) | sy2 (1/5/10/15) | sy3 (1/5/10/15) |
|---|---|---|---|---|
| V_PC | FCM | 98.55 / 92.55 / 89.03 / 88.65 | 92.25 / 85.83 / 86.57 / 87.60 | 89.26 / 84.11 / 85.28 / 86.48 |
| V_PC | Ours | 99.72 / 99.55 / 99.43 / 99.32 | 99.38 / 99.30 / 99.07 / 98.13 | 99.15 / 98.97 / 98.11 / 96.45 |
| V_PE | FCM | 3.63 / 13.66 / 18.79 / 19.42 | 15.63 / 26.05 / 24.75 / 22.85 | 20.88 / 29.29 / 27.20 / 24.96 |
| V_PE | Ours | 0.41 / 0.65 / 0.81 / 0.96 | 0.88 / 1.00 / 1.32 / 2.66 | 1.21 / 1.46 / 2.69 / 5.05 |
| ACC | FCM | 99.49 / 95.20 / 86.18 / 77.97 | 97.82 / 77.16 / 67.75 / 62.68 | 95.87 / 74.75 / 62.61 / 57.45 |
| ACC | Ours | 99.89 / 99.86 / 99.75 / 99.56 | 99.43 / 99.22 / 99.04 / 98.53 | 99.84 / 99.43 / 98.91 / 97.36 |
| F-score | FCM | 99.45 / 94.83 / 85.54 / 77.92 | 96.28 / 69.55 / 57.95 / 51.81 | 94.91 / 71.54 / 58.76 / 53.20 |
| F-score | Ours | 99.88 / 99.84 / 99.72 / 99.52 | 99.13 / 98.85 / 98.53 / 97.79 | 99.81 / 99.34 / 98.75 / 96.88 |
| NMI | FCM | 95.37 / 72.23 / 42.52 / 25.20 | 87.41 / 36.98 / 20.48 / 13.23 | 82.90 / 37.04 / 20.15 / 13.37 |
| NMI | Ours | 98.83 / 98.46 / 97.46 / 95.96 | 95.99 / 94.73 / 93.83 / 91.01 | 98.87 / 96.61 / 94.12 / 88.32 |
| Kappa | FCM | 98.97 / 90.36 / 72.34 / 56.20 | 95.09 / 48.60 / 27.44 / 16.04 | 90.70 / 43.18 / 15.88 / 4.27 |
| Kappa | Ours | 99.79 / 99.71 / 99.49 / 99.12 | 98.71 / 98.24 / 97.85 / 96.69 | 99.64 / 98.72 / 97.55 / 94.07 |
| İterasyon | FCM | 12 / 15 / 18 / 19 | 22 / 49 / 30 / 33 | 25 / 42 / 39 / 37 |
| İterasyon | Ours | 9 / 10 / 10 / 10 | 12 / 12 / 13 / 16 | 14 / 13 / 16 / 18 |

Ortalamalar (Tablo 2–7 "Mean"): V_PC FCM 88.85 / Ours 98.88 · V_PE 20.59 / 1.59 · ACC 79.58 / 99.23 · F 75.98 / 99.00 · NMI 45.57 / 95.35 · Kappa 54.92 / 98.30.
Makalenin kendi kabulü: bazı metrik/görüntülerde diğer yöntemler Ours'tan iyi (ör. FGFCM sy3 %10 ACC=98.94 > Ours 98.91; FRFCM sy1 %1 Kappa=99.96 > 99.79; FSC_LNML NMI varyansı en düşük).

### 6.3 Gerçek görüntüler (BSDS500, %5 karışık gürültü; Tablo 9) — FCM vs Ours
| Görüntü | V_PC FCM→Ours | ACC FCM→Ours | Kappa FCM→Ours |
|---|---|---|---|
| 100007 | 67.27 → 96.86 | 65.96 → 80.83 | 9.83 → 20.53 |
| 118035 | 54.77 → 96.57 | 73.08 → 96.24 | 39.42 → 91.54 |
| 167062 | 68.03 → 99.31 | 78.86 → 98.87 | 52.43 → 97.45 |
| 201080 | 52.57 → 97.61 | 62.72 → 85.12 | 16.12 → 66.52 |
| 241004 | 47.63 → 93.22 | 60.36 → 73.16 | 5.40 → 28.42 |
| 42049 | 68.04 → 97.21 | 81.67 → 96.36 | 53.97 → 88.22 |
| 67079 | 65.91 → 94.93 | 68.67 → 85.06 | 37.92 → 69.03 |
| 86016 | 65.01 → 97.50 | 62.89 → 83.26 | 23.03 → 56.39 |

Makale: Ours her zaman en iyi değil; FSC_LNML bazı görüntülerde (167062, 42049) daha yüksek; SRFCM 100007'de ACC=86.32 ile Ours'un (80.83) üstünde.

### 6.4 Süre/karmaşıklık
Ours, FSC_LNML ve CGFFCM'den hızlı ama diğer FCM türevlerinden pahalı (Fig. 29, Tablo 11).

## 7. Eleştirel değerlendirme (sunum + rapor için ham madde)

**Güçlü yönler:** gürültü altında yüksek ve kararlı V_PC/ACC/NMI/Kappa; düşük varyans; adaptif parametre (k, σ bir kez ayarlanır); seyreklikle daha az iterasyon; çoklu veri setinde genelleme gösterimi.
**Sınırlılıklar (makalenin kendi ifadesi):** (1) K önceden verilmeli; (2) hesaplama maliyeti yüksek (non-local × 7 alt-görüntü).
**Bizim gözlemlerimiz (doğrulanacak hipotezler):**
- Deneyler ağırlıkla tek tip karışık gürültü + 3 basit sentetik görüntü üzerinde; **gürültü türüne göre ayrı (Gaussian/S&P/multiplicative) analiz yok**.
- Gerçek görüntülerde iyileşme sentetiğe göre çok daha az (ör. 241004 ACC 73.16, Kappa 28.42); sentetik başarı gerçekte aynı büyüklükte geçmiyor.
- Parametre seçimi (σ, w, k, δ) 3 sentetik görüntüde yapılmış → gerçek görüntülere aşırı uyum riski.
- ACC/F/NMI/Kappa için **etiket eşleştirme (cluster→sınıf)** protokolü anlatılmamış.
- Rastgele başlatma → tekrar sayısı/ortalama±std verilmemiş (tek koşu gibi duruyor).
- Resmî kaynak kod bağlantısı makalede yok (kontrol et; varsa kullanım atıfla belirtilmeli).
- Ablasyonda yalnız-seyrek (✗✗✓) iterasyon 24 (> 20) çıkıyor; "seyreklik iterasyonu düşürür" iddiası kısmen bağlama bağlı.
- Hızı vurgularken karmaşıklığı O(n⁵) veriyor: pratik süre ölçümü şart.

## 8. Yönerge terimleriyle eşleme (FCM → "fuzzy sistem")

| Yönerge isteği | Bu projede karşılığı | Not |
|---|---|---|
| Sistem girdileri/çıktıları | Girdi: gürültülü gri-seviye görüntü (veya özellik: y, ξ, ϑ). Çıktı: üyelik matrisi U (K×N), kümeleme merkezleri c, etiket haritası | |
| Membership functions | **U matrisi** (veri-güdümlü üyelik dereceleri, Eq. 2/28) + Algoritma 2'deki Gauss tipi benzerlik çekirdekleri (S_ij, Ss_ij) | Kümeler "linguistic" değil (ör. "karanlık/orta/parlak" diye yorumlanabilir) |
| Fuzzy rule base / inference | FCM'de açık IF-THEN kuralı yok; kural yerine **amaç fonksiyonu minimizasyonu** (Eq. 12/20); pratik yorum: "piksel c_i'ye yakınsa u_ij yüksek" | **Hocadan teyit** |
| Defuzzification | `label_j = argmax_i u_ij` (üyelik → kesin etiket) | |
| Farklı girdilerle test | Farklı gürültü türü/yoğunluk/görüntü/K | |

## 9. ⚠️ Belirsizlikler ve uygulama tuzakları (KODLAMADAN ÖNCE OKU)

1. **Hard threshold sonrası boş sütun:** `η_ij < √δ` ise sıfırlanır. δ=0.4 → √δ≈0.632. K=2'de bir pikselin max üyeliği 0.632'den küçükse (ör. η=(0.6,0.4)) **tüm sütun sıfırlanır → normalizasyonda 0/0**. Makalenin `√δ ≤ min_j max_i η_ij` koşulu genelde sağlanmaz. **Uygulama kararı:** sütun tamamen sıfırlanırsa argmax elemanı 1 yap (veya η'yu koru). Bunu raporda açıkça belirt.
2. **Ödül kümesi boyutu:** Metin ⌈0.618·(N_R−1)⌉ der (N_R = pencere eleman sayısı, merkez dahil; 3×3 için N_R−1 = 8 komşu); Fig. 1 örneğinde 8 komşudan **4** piksel ödül kümesinde. Hesap: 0.618·8 = 4.94 → ceil=5, **round=5**, **floor=4**. Yani Fig. 1 ile yalnız **floor** uyumlu (PDF ile doğrulandı; önceki not "round ile 4" yanlıştı). **Karar gerek:** floor/ceil → ablasyonla karşılaştır.
3. **Eq. (10)'da y_j vs y_q:** Toplamda y_j yazıyor (j sabit → ağırlıkların ortalaması anlamsız). Mantıklı olan **y_q** (klasik NLM). y_q ile uygula, raporda not düş.
4. **Eq. (15)(16):** `exp(y_j − ξ_j)` işaretli fark; bölüm "mutlak fark"tan söz ediyor. Görüntü [0,1]'de olduğundan exp(·)∈[e⁻¹,e]. Seçenekler: (a) olduğu gibi, (b) `exp(|y_j − ξ_j|)`. Karar + test; ayrıca ΔG1/ΔG2 sembolleri (13)'te ve (15)'te yeniden kullanılmış (yeniden atama).
5. **Eq. (7) Ss_ij = exp(−d_ij):** ölçek parametresi yok (d=1…√(2)·⌊w/2⌋). Olduğu gibi uygula.
6. **Fig. 13 vs metin:** δ=0.4 "en iyi" denir ama Fig. 13 lejandında δ∈{0,0.02,…,0.1}. Tutarsız; δ taraması kendimiz yapılmalı.
7. **Karmaşıklık:** "n yerine tüm değişkenler" O(n⁵) kaba. Biz: ölçülen süre + N·S²·w² baskın terimi raporla.
8. **Sentetik görüntüler (sy1–sy3) verilmedi:** Fig. 9'dan elle (≈256×256) üretilecek; K ve gri seviyeleri belirle (tahmin: sy1 K=2; sy2 ve sy3 K=3). Raporda "yeniden oluşturuldu, birebir aynı değil" de.
9. **"%5 karışık gürültü" tanımı:** Gaussian + S&P + multiplicative eşit oranlı; yoğunluğun (varyans/oran) kesin tanımı yok. Kendi tanımımızı yaz (bkz. kararlar D-009).
10. **DTCWT kütüphanesi:** Python `dtcwt` (Kingsbury); filtre seçimi (near_sym_a/qshift_a vb.) ve seviye sayısı belirtilmemiş → 1 seviye varsayımı (ϑ için 1 yaklaşım + 6 detay).
11. **Metrik protokolü:** ACC/F/NMI/Kappa için küme etiketlerini ground-truth sınıflarına Macar algoritmasıyla eşle (ya da gri değere göre sırala). V_PC/V_PE `u` üzerinden (seyrek U'da V_PE ln(0)→0·ln0=0 kabul).
13. **w çelişkisi (PDF'te):** §4.1 "proposed algorithm: w, S, υ, g = **7**, 15, 4, 10" der; §4.4 (Fig. 11 analizi) "w = **5**" seçildiğini söyler. Biz w=5 kullanıyoruz (§4.4 ve Algoritma 3 örnekleri), w=7'yi ablasyonda da deneyeceğiz; raporda çelişkiyi belirt.
14. **Gri düzey / renkli görüntü:** BSDS500 renklidir; makale RGB→gri dönüşümünü veya kanal işlemini anlatmıyor (y_j "gri değer"). Varsayım: gri dönüşüm (D-karar gerekli). GT: BSDS çoklu insan anotasyonu içerir; hangisinin/nasıl kullanıldığı belirtilmemiş.
15. **Tablo numaraları:** PDF Tablo 10 = AID/MSRC/NASA/COCO ortalama metrikleri; Tablo 11 = karmaşıklık tablosu (§4.8 metni "Table 10" yazıyor — makale içi yazım hatası). Tablo 11'de w "yarıçap" olarak tanımlı, oysa metinde w×w pencere.
12. **Tablo 5'te sy1 FSC_LNML %5 F-score=96.33** gibi tutarsız görünen sayılar olabilir; makale verisini "referans" olarak alırken PDF'e bak.
