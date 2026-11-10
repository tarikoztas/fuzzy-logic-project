# 04 — Fazlar ve Yol Haritası

**Bugün:** 18.10.2026 (Pazar) · **Teslim:** 27.10.2026 (Salı) → **9 gün** · **Sunum:** 03.11.2026
**Not:** Checkpoint tarihleri yönergede yok. Hocadan öğrenilince aşağıdaki "Checkpoint" sütunu güncellenmeli. Aşağıdaki gün planı bizim *öneri* takvimimizdir.

> Her faz bitince kutuları işaretle, `CLAUDE.md`'deki durumu güncelle, commit at.

## Özet takvim

| Faz | Ad | Tarih (öneri) | Checkpoint | Puan odağı |
|---|---|---|---|---|
| 0 | Kurulum + doküman + açık sorular | 18.10 | — | Rapor/GitHub |
| 1 | Makale analizi + literatür | 18–19.10 | CP1 | Sunum(literatür/teori), Rapor |
| 2 | Uygulama planı + veri/gürültü/metrik altyapısı | 19–20.10 | CP2 | Uygulama |
| 3 | Baseline (FCM) + ASRFCM yeniden gerçekleştirme | 20–22.10 | CP3 | **Uygulama 30** |
| 4 | Katkı önerisi (netleştirme) | 21–22.10 | CP4 | **Katkı 30** |
| 5 | Deneyler (baseline vs katkı, ablasyon, duyarlılık) | 22–24.10 | CP5 | Katkı + Uygulama |
| 6 | Rapor + README + figür/tablo | 23–26.10 | — | **Rapor 20** |
| 7 | Sunum hazırlığı | 25–26.10 | — | **Sunum 20** |
| 8 | Final kontrol + Classroom teslimi | 26–27.10 | FINAL | Hepsi |
| 9 | Demo provası + savunma çalışması | 27.10–03.11 | — | Sunum/Savunma |

---

## Faz 0 — Kurulum ve temel (18.10)
- [ ] `git init`, ilk commit (doküman + klasör iskeleti); GitHub'da repo oluştur (private→teslimde erişilebilir yap)
- [ ] `.venv` + `pip install -r requirements.txt`; `import dtcwt, numba, skimage, cv2` testi
- [ ] `docs/06_KARARLAR.md` "Açık" maddelerini gözden geçir; **hocaya sorulacak soruları gönder** (MRR, FCM uygunluğu, rapor dili, checkpoint tarihleri, resmi kod kullanımı)
- [ ] README iskeleti (zorunlu 15 başlık, içi yer tutucu)
- **Çıktı:** çalışan ortam, ilk commit
- **Biter:** `python -c "import dtcwt, numba, skimage"` hatasız

## Faz 1 — Makale analizi + literatür (CP1)
- [ ] `docs/02_MAKALE_ANALIZI.md`'yi PDF ile karşılaştırarak doğrula (özellikle denklemler, parametreler)
- [ ] Problem/amaç/girdi-çıktı/deneysel yapı özeti (CP1 teslimi için 1–2 sayfa)
- [ ] **Literatür:** makalenin kaynakçasından gerçek çalışmalar (BCFCM 2002, FGFCM 2007, FLICM 2010, FRFCM 2018, FSC_LNML 2022, SRFCM 2021, FCM_SICM 2020, DSFCM_N 2019 …) + **en az 5 ek güncel çalışma** (2022–2026) web araştırmasıyla bul. Her biri için: yazar/yıl/yayın/DOI doğrulanmış, 2–3 cümle yöntem, güçlü/zayıf yön
- [ ] `references/README.md` (IEEE formatında doğrulanmış liste) + karşılaştırma tablosu (yöntem × spatial bilgi × non-local × sparse × adaptif × süre)
- **Çıktı:** CP1 notu; literatür tablosu; Related Work taslağı
- **Biter:** her kaynağın DOI'si açılıp kontrol edildi (`docs/05_KURALLAR.md` §2)

## Faz 2 — Uygulama planı + altyapı (CP2)
- [ ] MRR'yi netleştir (öneri bkz. `docs/06_KARARLAR.md` D-005)
- [ ] `src/data/synthetic.py`: sy1, sy2, sy3 (≈256×256) üret; `noise.py`: Gaussian/S&P/multiplicative/karışık; `bsds500.py`: 8 görüntü + GT (indirme kaynağı README'de)
- [ ] `src/eval/metrics.py` + `matching.py` + testler
- [ ] Deney planı (`docs/07_DENEY_PLANI.md`) güncelle: görüntüler, gürültü, seed, K
- **Çıktı:** veri+gürültü+metrik altyapısı, testler yeşil, CP2 planı
- **Biter:** `pytest tests/test_metrics.py tests/test_noise.py` geçer

## Faz 3 — Baseline + yeniden gerçekleştirme (CP3) — 30 puan
- [ ] **3a** `baseline_fcm.py` (Eq.1–3) + test; sy1–3 üzerinde gürültüsüz/gürültülü FCM → makale FCM sütunuyla (`results/tables/paper_reported_fcm_vs_ours.csv`) ilk karşılaştırma
- [ ] **3b** `local_info.py` (Algoritma 2) + Fig.1–3 örnek testi
- [ ] **3c** `nonlocal_wavelet.py` (DTCWT + Eq.10–11) + yeniden-oluşturma testi
- [ ] **3d** `adaptive_params.py` (Eq.13–19)
- [ ] **3e** `sparse_fcm.py` (Eq.20–29, Alg.3; boş-sütun politikası)
- [ ] **3f** Yeniden üretim deneyi: makaledeki **en az bir temel deney** (öneri: Tablo 2–8'in sy1–3 × %5 gürültü alt kümesi + Tablo 1 ablasyon) → bizim sonuçlar vs makale (CSV'den otomatik tablo)
- [ ] Tutarsızlıkları kayda geç (neden farklı çıktı: sy görüntüleri birebir değil, gürültü tanımı, seed…)
- **Çıktı:** çalışan baseline + ASRFCM, ilk karşılaştırma tablosu/figürü, CP3 raporu
- **Biter:** `python experiments/baseline/run_baseline.py` uçtan uca çalışır; sonuç tablosu üretilir

## Faz 4 — Katkı önerisi (CP4) — 30 puan
- [ ] `docs/06_KARARLAR.md` D-006 aday katkılarından seçim (öğrenci kararı)
- [ ] Bilimsel gerekçe (neden?), hipotez, başarı ölçütü (hangi metrik, hangi eşik), deney tasarımı — 1 sayfa CP4 metni
- [ ] `variants.py`: katkı bayrakla açılıp kapanır (baseline ile aynı kod yolu)
- **Çıktı:** CP4 öneri metni + kodda katkı bayrağı
- **Biter:** hipotez ve ölçüm planı yazılı, öğrenci onaylı

## Faz 5 — Deneyler (CP5)
- [ ] Ana karşılaştırma: baseline (FCM + ASRFCM makale hali) vs katkılı yöntem; N=10 seed; ortalama±std
- [ ] Ablasyon (bileşen kapat/aç) + parametre duyarlılığı (σ, k, δ, w; makale Fig.10–13'ü kendi sonuçlarımızla yeniden)
- [ ] Gürültü türü/yoğunluk analizi; gerçek görüntü (BSDS 8 görüntü) deneyi
- [ ] Süre ve iterasyon ölçümü
- [ ] Tablolar `results/tables/*.csv` + figürler `results/figures/*.png|pdf` (betikle üretilir); **baseline vs geliştirilen** tablo (yönerge 6.2 biçiminde: Metrik | Baseline | Geliştirilen | Değişim)
- [ ] İstatistiksel kontrol (std, mümkünse eşleşik test/Wilcoxon); iyileşme yoksa nedenleri tartış
- **Çıktı:** tüm sonuç tabloları/figürler, CP5 raporu
- **Biter:** her rapor sayısı bir CSV satırına izlenebilir

## Faz 6 — Rapor + GitHub dokümantasyonu — 20 puan
- [ ] `docs/08_RAPOR_ISKELETI.md`'yi izleyerek 8–12 sayfa rapor (IEEE kaynakça, **GenAI Disclosure**)
- [ ] README: 15 zorunlu başlık dolu; "How to Run" temiz ortamda denendi
- [ ] Her figür/tablo için başlık, eksen/birim, kaynak (makale vs bizim)
- [ ] `references/README.md` son hal
- **Biter:** rapor PDF'i 8–12 sayfa (kaynakça hariç); README kontrol listesi tam

## Faz 7 — Sunum — 20 puan
- [ ] `docs/09_SUNUM_SAVUNMA.md` iskeletiyle 15–20 dk sunum (yönergedeki 8 başlık)
- [ ] Canlı demo notebook'u (farklı gürültü/parametreyle çalışır; ~2 dk içinde sonuç)
- [ ] Savunma soru listesi çalışıldı (yönerge §14)
- **Çıktı:** `presentation/presentation.pdf`, demo notebook

## Faz 8 — Final kontrol + teslim (26–27.10)
- [ ] `docs/01_YONERGE.md` §20 teslim kontrol listesi (hepsi ✓)
- [ ] Temiz klasörde klonla→kur→çalıştır testi
- [ ] Repoda gizli bilgi taraması (`git grep -i "key\|token\|password"`)
- [ ] Classroom'a: rapor PDF + sunum PDF + GitHub bağlantısı; yükleme sonrası dosyalar açılıyor mu kontrol et
- [ ] Teslim **27.10.2026'dan önce** (son dakikaya bırakma; hedef 26.10 akşamı)

## Faz 9 — Savunma hazırlığı (27.10–03.11)
- [ ] Kodu satır satır anlatma provası (her modül: ne yapar, neden)
- [ ] Beklenen sorular: "Neden altın oran?", "σ artınca ne olur?", "hard threshold ne işe yarıyor?", "δ büyürse?", "neden DTCWT?", "FCM'den farkı?", "başarısız olduğu durumlar?"
- [ ] Demo yedek planı (internet/GPU gerekmeden çalışır; önceden üretilmiş figürler yedek)

---

## Risk kaydı

| Risk | Olasılık | Etki | Önlem |
|---|---|---|---|
| Süre kısıtı (9 gün) | Yüksek | Yüksek | MRR'yi dar tut (FCM + ASRFCM tam + 1 katkı); non-local'i numba ile hızlandır; Faz 3–5'i önceliklendir |
| Makale sonuçlarıyla sayısal fark | Yüksek | Orta | sy görüntüleri/gürültü tanımı belirsiz; fark nedenlerini raporla (yönerge bunu kabul ediyor) |
| DTCWT/numba kurulum sorunu | Orta | Orta | Faz 0'da kontrol; yedek: PyWavelets (SWT) ile yaklaşık non-local (belgeleyerek) |
| Non-local hesap süresi | Orta | Orta | Küçük test görüntüsü, numba, önbellek |
| FCM'nin "kural/defuzzification" beklentisine uymaması | Orta | Orta | Hocadan teyit (D-004), eşleme tablosu (02 §8) |
| Doğrulanmamış kaynak/uydurma riski (GenAI) | Orta | Yüksek | Her atıf DOI ile elle kontrol; `docs/05` §2 |
