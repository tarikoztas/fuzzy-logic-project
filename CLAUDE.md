# CLAUDE.md — Bulanık Mantık Dönem Projesi

> Bu dosya Claude Code'un **her oturum başında** okuması gereken ana bağlam dosyasıdır.
> Ayrıntılar `docs/` altındadır (**yerel, git'e girmez — D-034**). Herkese açık kayıt: `report/decisions.md` (İngilizce karar/sapma listesi) ve `report/checkpoints/` (CP notları). Bu dosyayı kısa ve güncel tut.

## 1. Proje özeti

- **Ders:** Bulanık Mantık — Dönem Projesi (İstanbul Üniversitesi-Cerrahpaşa, Bilgisayar Mühendisliği)
- **Öğrenci:** Tarık Öztaş, 1306230040 (README'ye işlendi)
- **Git:** commit'lere Claude co-author/trailer EKLENMEZ; yalnız öğrencinin hesabı (`tarikoztas`) — bkz. `docs/05_KURALLAR.md` §6. Öğrenci commit + `git push origin main` yetkisi verdi (12.11.2026); force push / history rewrite yok
- **Referans makale:** J. Wu, X. Wang, Y. Liu, C. Fang, *"Adaptive sparse regularized fuzzy clustering noise image segmentation algorithm based on complementary spatial information"*, Expert Systems With Applications 256 (2024) 124943. DOI: 10.1016/j.eswa.2024.124943
- **Proje akışı:** İNCELE → ANLA → UYGULA → GELİŞTİR → DENEY YAP → KARŞILAŞTIR → ANALİZ ET → SUN → RAPORLA
- **Tarihler:** Yönergede son teslim 27.10.2026, sunum 03.11.2026; hocaya sorulmayacak (D-026) → proje en kısa sürede eksiksiz tamamlanır
- **Puan:** Sunum+Savunma 20 · Uygulama/Yeniden Gerçekleştirme 30 · Özgün Katkı 30 · Rapor+GitHub 20 (toplam 100)

## 2. Oturum başında okunacaklar (sırayla)

1. `CLAUDE.md` (bu dosya)
2. `docs/04_FAZLAR_VE_YOL_HARITASI.md` → hangi fazdayız, sıradaki iş ne
3. `docs/06_KARARLAR.md` → alınmış / bekleyen kararlar
4. İş gerektiriyorsa: `docs/01_YONERGE.md`, `docs/02_MAKALE_ANALIZI.md`, `docs/03_MIMARI.md`, `docs/05_KURALLAR.md`, `docs/07_DENEY_PLANI.md`

Orijinal PDF'ler: `references/papers/` (yönerge ve makale). Çelişki olursa **PDF orijinali** esastır, `.md` özetleri değil.

## 3. Değişmez kurallar (özet — tam hali `docs/05_KURALLAR.md`)

1. **Uydurma yok:** Var olmayan kaynak, yapılmamış deney, üretilmemiş sonuç ASLA. Makaledeki sayılar "makalede raporlanan" diye etiketlenir; bizim ürettiklerimiz "bizim sonuç" diye. Doğrulanmamış atıf kullanma (DOI/yayıncı sayfasıyla kontrol et).
2. **Açıklanabilirlik:** Yazılan her kod öğrenci tarafından savunmada açıklanabilmeli. Karmaşık kısımlara kısa, net Türkçe/İngilizce yorum ekle; yeni bir kavramı sohbet tonunda, gerekirse benzetmeyle anlat. Öğrenci anlamadan bir sonraki faza geçme.
3. **Git geçmişi:** Küçük, anlamlı, sık commit (günde en az birkaç). Tek seferlik toplu yükleme YASAK (yönerge istiyor). Commit mesajı: `faz<N>: <ne yapıldı>`.
4. **Gizli bilgi yok:** API anahtarı, parola, token repoya girmez.
5. **Kaynak ayrımı:** Dışarıdan alınan kod `src/third_party/` veya dosya başında açık atıfla; öğrencinin kodundan ayırt edilir. Makale yazarlarının resmi kodu kullanılırsa rapor + README'de belirtilir.
6. **Tekrar üretilebilirlik:** Sabit seed, `requirements.txt` sürümleri, tek komutla deney çalıştırma.
7. **GenAI şeffaflığı:** Claude'un katkısını `docs/genai_usage_log.md` içine işle (rapordaki "Generative AI Usage Disclosure" bölümü buradan beslenir; docs yerel olduğu için açıklama raporda yer almalı).
8. **Dürüst raporlama:** Katkı baseline'dan kötü çıkarsa olduğu gibi raporla ve nedenini tartış (yönerge bunu açıkça kabul ediyor).
9. **Yönerge öncelikli:** Şüphede `docs/01_YONERGE.md` puan tablolarına bak; puan getirmeyen işe zaman harcama.

## 4. Teknik özet

- **Dil/ortam:** Python 3.12 (numpy<2, scipy, scikit-image, opencv, matplotlib, pandas, dtcwt, pyyaml; python-pptx sunum için). numba kullanılmıyor (NLM vektörize). Bkz. `requirements.txt`.
- **Makalenin çekirdeği:** FCM + (a) ödül/ceza kümeli yerel uzamsal bilgi ξ (altın oran 0.618), (b) DTCWT alanında yerel-olmayan bilgi ϑ, (c) adaptif katsayılar α,β,γ, (d) ℓ0 seyrek düzenlileştirme (hard threshold √δ + normalize).
- **Katkı (kesin, D-006-final / D-033):** α,β,γ için açık Mamdani bulanık çıkarım sistemi (üyelik fonksiyonları, IF–THEN kural tabanı, min/max çıkarım, durulaştırma) + üyelik fonksiyonu / durulaştırma / Mamdani–Sugeno karşılaştırmaları; destekleyici: C1 gürültü türü robustness, C2 ablasyon. İkinci iterasyon (D-044/D-045, önceden kayıtlı): σ için 3 kurallı Mamdani (FIS-σ, `src/fcm/fis_sigma.py`) + sınırlı α (FIS-σ+A).
- **Makale parametreleri:** w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4, m=2, ε=1e-6, T=100.
- **Metrikler:** V_PC, V_PE, ACC, F-score, NMI, Kappa (+ iterasyon sayısı, süre).
- **Bilinen makale belirsizlikleri / tuzakları:** `docs/02_MAKALE_ANALIZI.md` §9 — kodlamadan ÖNCE oku (ör. hard threshold sonrası sıfırlanan sütunlar, Eq. 10'daki y_j/y_q, Eq. 15-16 işaret belirsizliği).

## 5. Komutlar (Faz 0'da doğrulandı: Python 3.12, Windows)

```bash
py -3.12 -m venv .venv                       # 3.13 değil; bkz. D-024
.venv/Scripts/python.exe -m pip install -r requirements.txt   # (Linux/mac: .venv/bin/python)
.venv/Scripts/python.exe -m pytest           # birim testler (pytest.ini: pythonpath=.)
.venv/Scripts/python.exe experiments/baseline/run_baseline.py --config experiments/baseline/config.yaml   # E1
.venv/Scripts/python.exe experiments/proposed/run_proposed.py --config experiments/proposed/config.yaml   # E2
.venv/Scripts/python.exe experiments/ablation/run_ablation.py --config experiments/ablation/config.yaml     # E3
.venv/Scripts/python.exe experiments/run_grid.py --config experiments/contribution/<main|bsds|bsds_rgb|fis_variants|robustness|ablation_c2>.yaml
.venv/Scripts/python.exe experiments/run_grid.py --config experiments/sensitivity/config.yaml             # E4
.venv/Scripts/python.exe experiments/timing/run_timing.py                                                  # E7 (boş makinede)
.venv/Scripts/python.exe experiments/run_grid.py --config experiments/contribution/<tuning|second_iteration|bsds_second|bsds_rgb_second|robustness_second>.yaml   # E8 (ikinci iterasyon; tuning yalnız seed 100-104)
.venv/Scripts/python.exe experiments/summarize_tuning.py; .venv/Scripts/python.exe experiments/analyze_second_iteration.py   # E8 ayar kaydı, H5/H6 kararları, figürler
.venv/Scripts/python.exe experiments/analyze_contribution.py      # özet, Wilcoxon, figürler
.venv/Scripts/python.exe experiments/plot_reproduction.py; .venv/Scripts/python.exe experiments/plot_panels.py
.venv/Scripts/python.exe report/build_report.py                   # report.html -> report.pdf + README sonuç blokları
.venv/Scripts/python.exe report/build_report.py --lang tr         # Türkçe rapor: report_tr.pdf
.venv/Scripts/python.exe presentation/build_slides.py [--lang tr]  # slides[_tr].html -> presentation[_tr].pdf + .pptx + konuşmacı notları
.venv/Scripts/python.exe demo/demo.py --image sy3 --level 10 --pixel 120 80   # canlı demo
# Geçici dosyalar: .tmp/ (gitignore; C dolu). pip önbelleği .venv/pip.ini ile .tmp/pip-cache, pytest temp .tmp/pytest.
# Not: numpy<2 zorunlu (dtcwt 0.13 np.asfarray). run_grid paralel ve kaldığı yerden devam eder; cache/ ξ,ϑ önbelleği.
```


## 6. Durum takibi

- **Durum (14.11.2026):** Faz 0–8 + ikinci iterasyon (docs/14; D-044–D-046, CP6) tamam: H5/H6 tuttu; İngilizce ve Türkçe rapor (report.pdf, report_tr.pdf) ve sunum (24 slayt, PDF+PPTX, iki dil; D-047: [1]'de raporlanan değerlerle açık karşılaştırma); son kontrol tamamı PASS. Öğrenciye kalan: rapor/sunum okuma ve onay, DOI kontrolü, demo provası, `docs/13` çalışması, Classroom yüklemesi.

- İlerleme: `docs/04_FAZLAR_VE_YOL_HARITASI.md` içindeki checkbox'lar (her faz sonunda işaretle).
- Kararlar: `docs/06_KARARLAR.md` (yeni karar → yeni satır) **ve** herkese açık özeti `report/decisions.md`. Hocaya bağlı sorular kapatıldı (öğrenci hocaya sormayacak); yeni belirsizlikte en savunulabilir seçimi yap, gerekçesiyle iki dosyaya da yaz.
- Bu dosyadaki "Tarihler" ve "Komutlar" bölümlerini değişiklik olunca güncelle.

## 7. Çalışma biçimi

- Büyük bir adıma başlamadan önce kısa plan sun, öğrenci onayından sonra uygula.
- Her faz sonunda: ne yapıldı (2-3 cümle), neyi öğrenci doğrulamalı, sıradaki adım.
- Belirsiz noktada kendin karar ver ve belgele; yalnız yıkıcı/geri alınamaz işlem, ücretli/giriş gerektiren kaynak veya etik belirsizlikte dur ve sor.
- İletişim dili: Türkçe. Kod, değişken adları, commit'ler ve rapor/README/sunum: İngilizce (D-019).
