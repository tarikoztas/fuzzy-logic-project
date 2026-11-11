# CLAUDE.md — Bulanık Mantık Dönem Projesi

> Bu dosya Claude Code'un **her oturum başında** okuması gereken ana bağlam dosyasıdır.
> Ayrıntılar `docs/` altındadır. Bu dosyayı kısa ve güncel tut.

## 1. Proje özeti

- **Ders:** Bulanık Mantık — Dönem Projesi (İstanbul Üniversitesi-Cerrahpaşa, Bilgisayar Mühendisliği)
- **Öğrenci:** Tarık Öztaş, 1306230040 (README'ye işlendi)
- **Git:** commit'lere Claude co-author/trailer EKLENMEZ; yalnız öğrencinin hesabı (`tarikoztas`) — bkz. `docs/05_KURALLAR.md` §6
- **Referans makale:** J. Wu, X. Wang, Y. Liu, C. Fang, *"Adaptive sparse regularized fuzzy clustering noise image segmentation algorithm based on complementary spatial information"*, Expert Systems With Applications 256 (2024) 124943. DOI: 10.1016/j.eswa.2024.124943
- **Proje akışı:** İNCELE → ANLA → UYGULA → GELİŞTİR → DENEY YAP → KARŞILAŞTIR → ANALİZ ET → SUN → RAPORLA
- **Tarihler:** Bugün (plan başlangıcı) 18.10.2026 · **Son teslim 27.10.2026** (Classroom) · **Sunumlar 03.11.2026**
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
7. **GenAI şeffaflığı:** Claude'un katkısını `docs/genai_usage_log.md` içine işle (rapordaki "Generative AI Usage Disclosure" bölümü buradan beslenir).
8. **Dürüst raporlama:** Katkı baseline'dan kötü çıkarsa olduğu gibi raporla ve nedenini tartış (yönerge bunu açıkça kabul ediyor).
9. **Yönerge öncelikli:** Şüphede `docs/01_YONERGE.md` puan tablolarına bak; puan getirmeyen işe zaman harcama.

## 4. Teknik özet

- **Dil/ortam:** Python 3.10+ (numpy, scipy, scikit-image, opencv, matplotlib, pandas, dtcwt, numba). Bkz. `requirements.txt`.
- **Makalenin çekirdeği:** FCM + (a) ödül/ceza kümeli yerel uzamsal bilgi ξ (altın oran 0.618), (b) DTCWT alanında yerel-olmayan bilgi ϑ, (c) adaptif katsayılar α,β,γ, (d) ℓ0 seyrek düzenlileştirme (hard threshold √δ + normalize).
- **Makale parametreleri:** w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4, m=2, ε=1e-6, T=100.
- **Metrikler:** V_PC, V_PE, ACC, F-score, NMI, Kappa (+ iterasyon sayısı, süre).
- **Bilinen makale belirsizlikleri / tuzakları:** `docs/02_MAKALE_ANALIZI.md` §9 — kodlamadan ÖNCE oku (ör. hard threshold sonrası sıfırlanan sütunlar, Eq. 10'daki y_j/y_q, Eq. 15-16 işaret belirsizliği).

## 5. Komutlar (Faz 0'da doğrulandı: Python 3.12, Windows)

```bash
py -3.12 -m venv .venv                       # 3.13 değil; bkz. D-024
.venv/Scripts/python.exe -m pip install -r requirements.txt   # (Linux/mac: .venv/bin/python)
.venv/Scripts/python.exe -m pytest           # birim testler (pytest.ini: pythonpath=.)
PYTHONPATH=. .venv/Scripts/python.exe experiments/noise_check/check_noise_levels.py   # gürültü tanımı kontrolü
.venv/Scripts/python.exe -m src.data.bsds500  # BSDS500 8 görüntü kontrolü (veri: data/README.md)
# Not: numpy<2 zorunlu (dtcwt 0.13 np.asfarray kullanıyor); tam sürümler requirements.lock.txt
# Not: dtcwt 1 seviyede lowpass tam boyut (H×W), highpasses[0] (H/2×W/2×6) — Faz 3c'de dikkat
.venv/Scripts/python.exe experiments/baseline/run_baseline.py --config experiments/baseline/config.yaml   # E1, ~30 s
.venv/Scripts/python.exe experiments/baseline/plot_baseline.py                                           # E1 figürü
python experiments/proposed/run_proposed.py --config experiments/proposed/config.yaml
```

(Betik adları `docs/03_MIMARI.md`'deki planla uyumlu; oluşturulunca burayı güncelle.)

## 6. Durum takibi

- İlerleme: `docs/04_FAZLAR_VE_YOL_HARITASI.md` içindeki checkbox'lar (her faz sonunda işaretle).
- Kararlar: `docs/06_KARARLAR.md` (yeni karar → yeni satır; bekleyen kararları öğrenciye sor, kendin varsayma).
- Bu dosyadaki "Tarihler" ve "Komutlar" bölümlerini değişiklik olunca güncelle.

## 7. Çalışma biçimi

- Büyük bir adıma başlamadan önce kısa plan sun, öğrenci onayından sonra uygula.
- Her faz sonunda: ne yapıldı (2-3 cümle), neyi öğrenci doğrulamalı, sıradaki adım.
- Belirsiz noktada (özellikle hocadan teyit gereken: `docs/06_KARARLAR.md` "Açık") durup sor.
- İletişim dili: Türkçe. Kod, değişken adları, commit'ler ve rapor/README: İngilizce (rapor dili teyit bekliyor, bkz. kararlar).
