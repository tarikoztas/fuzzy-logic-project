# 03 — Yazılım Mimarisi

Hedef: makaledeki yöntemi **modüler** ve **açıklanabilir** biçimde yeniden gerçekleştirmek; baseline ve geliştirilen sistemi aynı altyapıda **adil** karşılaştırmak; tüm sonuçları tek komutla yeniden üretmek.

## 1. Klasör yapısı

```
fuzzy-logic-project/
├── CLAUDE.md                      # Claude Code ana bağlam dosyası
├── README.md                      # yönergedeki zorunlu başlıklarla
├── LICENSE  requirements.txt  .gitignore
├── docs/                          # proje dokümanları (bu klasör)
├── references/
│   ├── README.md                  # doğrulanmış kaynak listesi (IEEE)
│   └── papers/                    # yönerge + makale PDF'leri (yayıncı PDF'i git'e girmez)
├── src/
│   ├── fcm/
│   │   ├── __init__.py
│   │   ├── baseline_fcm.py        # Eq.1-3, Algoritma 1
│   │   ├── local_info.py          # Algoritma 2, Eq.5-9  (ξ)
│   │   ├── nonlocal_wavelet.py    # Eq.10-11 + DTCWT      (ϑ)
│   │   ├── adaptive_params.py     # Eq.13-19              (α,β,γ)
│   │   ├── sparse_fcm.py          # Eq.20-29, Algoritma 3 (ana yöntem)
│   │   └── variants.py            # katkı varyantları (bayraklarla açılır/kapanır)
│   ├── data/
│   │   ├── synthetic.py           # sy1, sy2, sy3 üretimi (Fig.9'dan)
│   │   ├── bsds500.py             # BSDS500 yükleme + GT
│   │   └── noise.py               # Gaussian / tuz-biber / multiplicative / karışık
│   ├── eval/
│   │   ├── metrics.py             # VPC, VPE, ACC, F, NMI, Kappa (Eq.30-35)
│   │   └── matching.py            # küme→sınıf eşleme (Macar algoritması)
│   ├── viz/
│   │   └── plots.py               # segmentasyon paneli, tablo→figür, yakınsama eğrisi
│   ├── utils/
│   │   ├── seed.py  timing.py  config.py  io.py
│   └── third_party/               # dış kod varsa (atıflı)
├── data/                          # ham/işlenmiş veri (büyük dosyalar .gitignore)
│   └── README.md                  # veri kaynağı + hazırlama adımları
├── experiments/
│   ├── baseline/    run_baseline.py   config.yaml
│   ├── proposed/    run_proposed.py   config.yaml
│   ├── ablation/    run_ablation.py
│   └── sensitivity/ run_sensitivity.py
├── results/
│   ├── figures/     tables/
├── notebooks/                     # keşif + demo (canlı sunum için)
├── tests/                         # pytest birim testleri
├── presentation/presentation.pdf
└── report/report.pdf  (+ kaynak: report.tex veya .docx)
```

## 2. Veri akışı

```
Temiz görüntü ──noise.py──► gürültülü görüntü I (normalize [0,1])
                                   │
          ┌────────────────────────┼─────────────────────────┐
          ▼                        ▼                         ▼
   local_info.py (ξ)     nonlocal_wavelet.py (ϑ)        y = I (orijinal)
          └──────────────┬─────────┴─────────────────────────┘
                         ▼
               adaptive_params.py → α, β, γ
                         ▼
        sparse_fcm.py (Algoritma 3: c→η→hard threshold→normalize→J)
                         ▼
          U (K×N), c, J geçmişi, iterasyon sayısı
                         ▼
   defuzzify: label = argmax_i u_ij ──► eval/metrics.py ──► results/{figures,tables}
```
**Önbellek:** ξ ve ϑ yalnız görüntüye + (w,S,σ,g,υ) parametrelerine bağlı, iterasyondan bağımsız → bir kez hesapla, diske/belleğe önbellekle (süre ölçümünde ayrı raporla: ön-işleme süresi vs. kümeleme süresi).

## 3. Modül arayüzleri (öneri)

```python
# baseline_fcm.py
def fcm(y: np.ndarray, K: int, m: float = 2.0, T: int = 100, eps: float = 1e-6,
        seed: int = 0) -> FCMResult   # U, c, J_hist, n_iter

# local_info.py
def local_spatial_info(img: np.ndarray, w: int = 5, sigma: float = 0.3,
                       reward_ratio: float = 0.618, rounding: str = "ceil") -> np.ndarray   # ξ

# nonlocal_wavelet.py
def nonlocal_wavelet_info(img: np.ndarray, S: int = 15, w: int = 5, g: float = 10.0,
                          upsilon: float = 4.0, levels: int = 1) -> np.ndarray   # ϑ

# adaptive_params.py
def adaptive_coeffs(y, xi, theta, k: float = 15.0, eps: float = 1e-8,
                    variant: str = "paper") -> tuple[np.ndarray, np.ndarray, np.ndarray]   # α,β,γ

# sparse_fcm.py
def asrfcm(y, xi, theta, alpha, beta, gamma, K: int, m: float = 2.0, delta: float = 0.4,
           T: int = 100, eps: float = 1e-6, seed: int = 0,
           empty_col_policy: str = "argmax") -> FCMResult

# metrics.py
def evaluate(U: np.ndarray, labels_pred: np.ndarray, labels_gt: np.ndarray) -> dict
# -> {"VPC":..., "VPE":..., "ACC":..., "F":..., "NMI":..., "Kappa":...}
```
`FCMResult` = dataclass: `U, centers, J_history, n_iter, time_s`.

## 4. Konfigürasyon

`experiments/*/config.yaml`: görüntü listesi, gürültü türü/yoğunluk, seed listesi, parametreler (makale varsayılanları), çıktı dizini. Aynı config + seed → aynı sonuç. Sonuçlar `results/` altına **yöntem_görüntü_gürültü_seed** adlandırmasıyla CSV olarak yazılır; tablo/figür betikleri CSV'den üretilir (elle sayı girilmez).

## 5. Performans notları

- Yerel işlem: pencere başına sıralama → `numpy.lib.stride_tricks.sliding_window_view` + `np.sort`/`argpartition`; N≈65k (256²) için vektörize.
- Yerel-olmayan: 7 alt-görüntü × N × S²(225) × w²(25) → **numba** (`@njit(parallel=True)`) veya patch-bazlı vektörizasyon; test için 128×128, deney için 256×256 (BSDS: 481×321, süre ölçerek).
- DTCWT: Python `dtcwt` paketi (`dtcwt.Transform2d`). Karmaşık katsayılarda işlem: gerçek ve sanal kısım ayrı ayrı veya genlik üzerinde → **karar gerekli** (D-010).

## 6. Test stratejisi (`tests/`)

| Test | Doğrular |
|---|---|
| `test_fcm_baseline.py` | U sütun toplamı=1; J monoton azalır; iki-küme basit veride doğru merkezler; sklearn/skfuzzy ile (kurulabilirse) karşılaştırma |
| `test_local_info.py` | Fig. 1 örneği (3×3, değerler 83…): ödül/ceza kümesi; Fig. 2–3 örneklerinde ξ ≈ 166 ve ≈175 (yaklaşık, ±birkaç) |
| `test_nonlocal.py` | Gürültüsüz sabit görüntüde ϑ≈görüntü; DTCWT perfect reconstruction (gidiş-dönüş hata ≈1e-10) |
| `test_adaptive.py` | α,β,γ > 0; gürültü artınca β+γ artar, α azalır |
| `test_sparse_fcm.py` | Çıktı U sütun toplamı 1 ve seyrek; boş sütun politikası NaN üretmez; J (20) kayda değer artmaz |
| `test_metrics.py` | Bilinen küçük örneklerde V_PC, V_PE, NMI, Kappa el hesabıyla eşleşir |
| `test_noise.py` | Yoğunluk/oran beklenen aralıkta; seed tekrarlanabilir |

## 7. Adil karşılaştırma ilkeleri (Puan: "Baseline ile adil karşılaştırma" 5)

- Aynı görüntüler, aynı gürültü gerçekleşimleri (aynı seed), aynı K, aynı m/ε/T.
- Baseline ve geliştirilen yöntem **aynı başlangıç üyeliği (seed)** ile ve **N tekrar** (öneri 10) çalıştırılır; ortalama ± std raporlanır.
- Tek parametre değişir (ablasyon mantığı); hiperparametre aramasını yalnız doğrulama kümesinde yap, test kümesinde sabit tut.
- Süre: aynı makinede, ön-işleme + kümeleme ayrı; ısınma (numba JIT) süreye dahil edilmez.
