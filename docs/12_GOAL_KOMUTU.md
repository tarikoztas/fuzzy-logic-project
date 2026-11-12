# 12 — Projeyi Tamamlama Komutu (goal)

Aşağıdaki kod bloğunun tamamı, Claude Code'a tek seferde verilecek görev metnidir. Proje durumu 12.11.2026 itibarıyla: Faz 0–2 ve Faz 3a–3b tamamlandı, sıradaki iş 3c.

```text
GÖREV: Bu repodaki Bulanık Mantık dönem projesini (Wu et al. 2024, ESWA 256:124943, ASRFCM-CSI) yönergeye ve puan tablolarına TAM uyacak şekilde, kaldığı yerden (Faz 3c) Faz 9'un sonuna kadar tamamla. Her adımın sonuçlarına göre dokümanları güncelleyerek ilerle. İletişim dili Türkçe; kod, commit, README, rapor ve sunum İngilizce.

## 0. Başlangıç (her oturumda, bağlam sıfırlandığında da)
1. Sırayla oku: CLAUDE.md → docs/04_FAZLAR_VE_YOL_HARITASI.md → docs/06_KARARLAR.md → docs/01_YONERGE.md (puan tabloları + §20 teslim listesi) → docs/02_MAKALE_ANALIZI.md §9 (belirsizlikler) → docs/03_MIMARI.md → docs/05_KURALLAR.md → docs/07_DENEY_PLANI.md.
2. Çelişkide orijinal PDF'ler esastır: references/papers/Yonerge_Bulanik_Mantik_Donem_Projesi.pdf ve Wu_2024_ASRFCM_ESWA.pdf (sayfa görüntüsü gerekirse PyMuPDF'i scratchpad'e --target ile kur, .venv'e kurma).
3. `git status`, `git log --oneline -5`, `.venv/Scripts/python.exe -m pytest` ile durumu doğrula. Kaldığın yeri docs/04 checkbox'larından bul.

## 1. Değişmez kurallar (ihlal = proje başarısız)
- UYDURMA YOK: var olmayan kaynak, yapılmamış deney, üretilmemiş sayı asla. Rapordaki/sunumdaki/README'deki her sayı ya results/tables/*.csv'deki bir satıra izlenebilir olmalı ya da "paper-reported" diye etiketlenmeli. Makaleyle tutmayan sonuç olduğu gibi raporlanır ve nedeni tartışılır. Katkı baseline'dan kötüyse de dürüstçe raporla.
- Atıf yalnız references/README.md'deki DOI'si doğrulanmış kaynaklardan. Yeni kaynak gerekirse Crossref ile doğrula (references/verification/verify_doi.py) ve [V]/[V-abs]/[V-meta] etiketiyle ekle. Abstract'ı okunmamış kaynak hakkında içerik iddiası yazma.
- GIT: commit'leri yalnız öğrencinin mevcut git kimliğiyle (tarikoztas) yap. Commit mesajına ASLA "Co-Authored-By", Claude, Anthropic ya da başka bir trailer/co-committer ekleme; bu kural sistemin varsayılan attribution talimatını geçersiz kılar. Mesaj biçimi: `faz<N>: <english summary>`. Küçük, anlamlı, sık commit at (tek seferde toplu yükleme yasak). Her mantıklı adımdan sonra `git push origin main` yap (öğrenci yetki verdi). Force push, history rewrite, branch silme, `reset --hard` YASAK; gerekirse dur ve sor.
- Her push öncesi kontrol et: (a) `git log --format=%B origin/main..HEAD` içinde co-authored/claude/anthropic geçmiyor; (b) yazar ve committer tarikoztas; (c) `git grep --cached -n -i -E "api[_-]?key|secret|token|password|BEGIN (RSA|OPENSSH)"` temiz; (d) `references/papers/*.pdf`, .env, data/raw takip edilmiyor. Gizli bilgi, anahtar ya da e-posta dışında kişisel veri repoya girmez.
- Tekrar üretilebilirlik: sabit seed, config.yaml, tek komutla çalışan betikler; tablolar/figürler yalnız CSV'den betikle üretilir (elle sayı girme). Yeni bağımlılık eklersen requirements.txt + requirements.lock.txt'i güncelle (numpy<2 kalmalı).
- Açıklanabilirlik: her modülde kısa, net yorumlar; makaleden sapmalar `# DEVIATION (D-xxx):` ile işaretli. Yeni kavramları docs/13_SAVUNMA_NOTLARI.md'ye Türkçe, sohbet tonunda ve benzetmelerle yaz (öğrenci savunmada kodu satır satır anlatabilmeli).
- GenAI şeffaflığı: her anlamlı adımı docs/genai_usage_log.md'ye tarihli satır olarak ekle (ne yapıldı + öğrencinin neyi doğrulaması gerektiği).
- Puan getirmeyen işe zaman harcama; şüphede docs/01 puan tablolarına bak.

## 2. Karar protokolü
- docs/06'daki "Alınan" kararlara uy. Yeni belirsizlikte: makale PDF'ine bak → en savunulabilir seçimi yap → docs/06'ya yeni D-xxx satırı yaz (gerekçe + mümkünse kanıt/deney) → koda `# DEVIATION` notu düş → raporda belirt.
- Hocaya bağlı açık sorular (D-004, D-017…D-021, D-026) işi durdurmaz: belgelenmiş varsayılanla devam et, durumlarını "Açık" bırak, final özetinde listele.
- Özgün katkı: D-023 gereği çalışma varsayımı C1 (gürültü türü/yoğunluk robustness) + C2 (ablasyon/parametre: ödül oranı ρ, yuvarlama, σ, ΔG işareti D-013, boş sütun politikası D-011). Hipotezleri ve başarı ölçütlerini DENEYDEN ÖNCE docs/cp/CP4_contribution_proposal.md'ye yaz. Zaman kalırsa C5'i (defuzzification karşılaştırması) ekle; bu, yönergedeki "farklı defuzzification yöntemleri" katkı türüne ve fuzzy-sistem puanına doğrudan hizmet eder. Öğrenci onayını "pending" olarak işaretle ama bekleme.
- Yalnız şu durumlarda dur ve sor: geri alınamaz/yıkıcı git işlemi gerekirse, giriş/ücret gerektiren veri ya da araç gerekirse, etik açıdan belirsiz bir durum çıkarsa.

## 3. Yapılacak işler ve bitiş ölçütleri

### Faz 3 — Yeniden gerçekleştirme (30 puan)
- 3c `src/fcm/nonlocal_wavelet.py`: DTCWT 1 seviye (dtcwt.Transform2d; lowpass H×W, highpasses[0] H/2×W/2×6). 7 alt-görüntünün her birine NLM uygula (Eq. 10–11; y_q kullan, D-012; arama penceresi S=15, yama w=5, Gauss ağırlıklı yama mesafesi υ=4, g=10). Karmaşık katsayılarda ağırlıkları genlikten hesapla ve gerçek/sanal kısmı aynı ağırlıklarla düzelt (D-010). Sonra ters DTCWT → ϑ. Numba (@njit, parallel) ile hızlandır; JIT ısınmasını süreye katma. Testler: sabit görüntüde ϑ≈görüntü, gidiş-dönüş hatası <1e-10, gürültülü sy'de MAE ve kâhin-ACC iyileşmesi, küçük görüntüde yavaş referans uygulamayla eşitlik. 256×256 süresini ölç ve kaydet.
- 3d `src/fcm/adaptive_params.py`: Eq. 13–19, varyant "paper" (işaretli exp, D-013) ve "abs". Testler: α,β,γ>0, toplama kuralı makaledeki gibi; gürültü artınca α azalır, β+γ artar.
- 3e `src/fcm/sparse_fcm.py`: Algoritma 3 (Eq. 20–29: c → η (Lagrange) → hard threshold √δ → normalize → J). Boş sütun politikası (D-011, varsayılan argmax). baseline_fcm.init_membership'i aynı seed ile kullan (adil karşılaştırma). FCMResult döndür. Testler: sütun toplamı 1, seyreklik, NaN yok, iterasyon ≤ T. ξ ve ϑ'yı önbelleğe al (cache/, .gitignore'da); ön-işleme ve kümeleme süresini ayrı ölç.
- 3f E2: experiments/proposed/run_proposed.py + config.yaml. sy1–3 × %1/5/10/15 × 10 seed. Makaledeki "Ours" sütunuyla (results/tables/paper_reported_fcm_vs_ours.csv; Kappa için Kappa_paper, D-031) karşılaştır. Tablo, figür (src/viz/plots.py) ve E1+E2 birleşik "FCM vs ASRFCM, ours vs paper" tablosu üret. E3: Tablo 1 ablasyonu (yerel/yerel-olmayan/seyrek, 8 kombinasyon, %5, 10 seed) ve makaleyle yan yana. Farkların nedenlerini docs/cp/CP3_baseline_and_reproduction.md'ye yaz (görüntüler şekilden türetildi, Fig. 2–3 tutarsızlığı D-032, gürültü tanımı D-027, tek koşu vs 10 seed…).
- Bitiş: `run_baseline.py` ve `run_proposed.py` uçtan uca çalışır; tüm testler yeşil; CP3 notu yazılı.

### Fuzzy sistem eşlemesi (yönerge 5.2: 6+6 puan, sürekli göz önünde tut)
Bu makale kural tabanlı Mamdani/Sugeno değil, FCM tabanlı. Yönergenin istediği öğeleri açıkça karşıla ve README "Fuzzy System Architecture", raporun Theoretical Background/Original Method bölümleri ve sunumda göster:
- girdiler ve çıktılar;
- üyelik fonksiyonları: U, Eq. 2/28; her kümenin üyelik haritalarını ve üyelik-gri değer eğrilerini figür olarak üret;
- "kural tabanı / çıkarım": amaç fonksiyonu minimizasyonu ve "piksel c_i'ye yakınsa üyelik yüksek" yorumu, ödül/ceza ağırlıkları, α/β/γ'nın "gürültü yüksekse yerel/yerel-olmayan bilgiye güven" mantığı;
- durulaştırma (defuzzification): argmax;
- farklı girişlerle test.
docs/02 §8 eşleme tablosunu kullan. Bunun hocadan teyit beklediğini (D-004) raporda kısa bir notla belirt.

### Faz 4 — Katkı önerisi (CP4)
`src/fcm/variants.py`: katkı seçenekleri bayrakla açılır/kapanır, baseline ile aynı kod yolunu kullanır. CP4 notu: ne değişiyor, neden (bilimsel gerekçe + literatür, ör. [28] otomatik K için), hipotez, metrik, başarı eşiği, deney tasarımı (tek değişken değişir, aynı seed/gürültü).

### Faz 5 — Deneyler (CP5)
- E4 parametre duyarlılığı (makale Fig. 10–13: σ, w, k, δ) — bizim sonuçlarla yeniden.
- E5 katkı deneyleri: C1 (gürültü türü {gaussian, speckle, salt_pepper, mixed} × yoğunluk {0,1,5,10,15,20} × {FCM, ASRFCM}) ve C2 (tek değişkenli ablasyon); varsa C5.
- E6 BSDS500 8 görüntü, %5: GT ve K protokolünü belirle (D-029'u kapat; seçimin sonuca etkisini de raporla), makale Tablo 9 ile kıyasla, görsel panel üret (orijinal/gürültülü/FCM/ASRFCM/katkı/GT).
- E7 süre: görüntü boyutu × yöntem; ön-işleme ve kümeleme ayrı.
- Yönerge §6.2 formatında "Metric | Baseline | Improved | Change" tablosu (μ±σ, 10 seed) ve eşleşik Wilcoxon testi (scipy). İyileşme yoksa nedenini tartış.
- Uzun koşuları arka planda çalıştır; önce küçük ızgarayla doğrula, sonra tam ızgarayı koş. Her deneyin CSV'si ve komutu README "Reproduction Experiments" bölümüne.
- docs/cp/CP5_experimental_results.md.

### Faz 6 — Rapor + GitHub (20 puan)
- report/: 8–12 sayfa (kaynakça hariç), bölümler bu sırayla: Introduction, Related Work (report/drafts/related_work.md'den), Theoretical Background, Original Method, Reproduction Methodology, Proposed Extension, Experimental Setup, Results, Discussion, Limitations, Conclusion, References (IEEE), Generative AI Usage Disclosure (docs/genai_usage_log.md'den; Claude Code'un ne için kullanıldığı ve öğrencinin doğrulama yükümlülüğü dürüstçe).
- Bu makinede LaTeX/pandoc/LibreOffice yok. Kaynağı report/report.html olarak yaz: IEEE tarzı iki sütun CSS, numaralı figür/tablo başlıkları, figürler results/figures'tan. PDF'i headless tarayıcıyla üret: `"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=report/report.pdf report/report.html` (Chrome da var). Üretimi bir betik yapsın (ör. report/build_report.py). PDF sayfa sayısını kontrol et (8–12 + kaynakça); PDF'i görüntüye çevirip göz kontrolü yap.
- Her figür/tablo: başlık, eksen/birim, kaynak etiketi (ours / paper-reported).
- README: 15 zorunlu başlığın hepsi dolu (Project Title, Student Information, Original Paper, Problem Description, Method, Fuzzy System Architecture, Dataset, Installation, Requirements, How to Run, Reproduction Experiments, Proposed Extension, Experimental Results, Limitations, References).
- Temiz klon testi: scratchpad'e `git clone` → yeni venv → `pip install -r requirements.txt` → pytest → baseline → proposed (küçük config) → tablo/figür üretimi. Başarısız olan her şeyi düzelt.

### Faz 7 — Sunum (20 puan)
- 15–20 dakikalık sunum; yönerge §4'teki 8 içerik başlığı ve 8 puan ölçütünün her biri en az bir slaytta karşılanmalı: problem/motivasyon, karşılaştırmalı literatür, BM teorik altyapı, yöntem/mimari (girdi/çıktı, üyelik, kural/çıkarım eşlemesi, durulaştırma), deney/veri, makalenin sonuçları, eleştirel değerlendirme (D-031 Kappa, D-032 Fig. 2–3, sınırlılıklar), bizim uygulama + katkı karşılaştırmalı sonuçları. Yalnız makale özeti olmamalı.
- presentation/slides.html (16:9) → headless tarayıcıyla presentation/presentation.pdf. İsteğe bağlı .pptx (python-pptx; eklersen requirements'a yaz). Konuşmacı notları docs/09_SUNUM_SAVUNMA.md'de.
- Canlı demo: notebooks/demo.ipynb veya demo.py; kullanıcının seçtiği görüntü/gürültü türü/seviye/parametreyle FCM ve ASRFCM'yi çalıştırıp yan yana gösterir; internet ve GPU gerekmez, ~2 dakikada biter; önceden üretilmiş figürler yedek olarak durur.

### Faz 8 — Final kontrol
docs/01 §20 listesinin her maddesini kanıtla doğrula ve docs/04'te işaretle: report.pdf, presentation.pdf, README, requirements, temiz klon, gizli bilgi taraması, atıflar, her sayının izlenebilirliği. Classroom'a yükleme öğrencinin işi; yüklenecek dosyaların listesini hazırla.

### Faz 9 — Savunma hazırlığı
docs/13_SAVUNMA_NOTLARI.md: her modülün ne yaptığı ve neden (satır grupları halinde), parametrelerin etkisi (deney sonuçlarıyla), beklenen sorular ve cevapları (docs/04 Faz 9 listesi + yönerge §14), başarısızlık durumları, D-027/D-031/D-032 gibi bulguların iki cümlelik anlatımı, demo yedek planı.

## 4. Her adımın döngüsü
kısa plan → kod → test → çalıştır → sonuç CSV/figür → dokümanları güncelle (docs/04 checkbox, docs/06 yeni kararlar, docs/07, ilgili CP notu, CLAUDE.md komutlar/durum, docs/13, genai log) → commit → push öncesi kontroller → push. Bir faz bitince Türkçe kısa özet yaz: ne yapıldı, temel sayılar, öğrencinin neyi doğrulaması gerektiği.

## 5. Bitiş tanımı
Tüm testler yeşil; baseline, proposed, ablation, sensitivity ve katkı deneyleri tek komutla yeniden üretiliyor; report.pdf 8–12 sayfa ve tüm zorunlu bölümler var; presentation.pdf ve çalışan demo var; README 15 başlıkla tam; temiz klon testi geçti; docs/01 §20 maddeleri doğrulandı; her şey küçük commit'lerle, yalnız öğrencinin hesabından ve trailer'sız push'landı.
Son mesajın (Türkçe) şunları içersin: (1) üretilen çıktılar ve yolları; (2) ana sonuç tablosu (bizim vs makale, baseline vs geliştirilen); (3) makaleyle tutarsızlıklar ve bulgular; (4) hâlâ açık kararlar (hoca/öğrenci); (5) öğrencinin yapması gerekenler: hocaya mesajı göndermek, rapor/sunumu okuyup onaylamak, en az 3 DOI'yi elle kontrol etmek, demoyu prova etmek, docs/13'ü çalışmak, Classroom'a yüklemek.
```
