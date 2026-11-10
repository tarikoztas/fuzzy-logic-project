# Claude Code Başlangıç Promptu

## Nasıl kullanılır

1. `fuzzy-logic-project/` klasörünü bilgisayarında istediğin yere koy.
2. Terminalde klasöre gir ve Claude Code'u başlat:
   ```bash
   cd fuzzy-logic-project
   claude
   ```
3. Aşağıdaki promptu yapıştır (tek parça).

## Prompt (kopyala-yapıştır)

```
Merhaba! Bu klasör, Bulanık Mantık dersi dönem projem için hazırlanmış proje klasörü. Projeyi yönergeye birebir uygun şekilde, adım adım beraber yürüteceğiz.

ÖNCE OKU (sırayla):
1. CLAUDE.md
2. docs/04_FAZLAR_VE_YOL_HARITASI.md
3. docs/06_KARARLAR.md
4. docs/01_YONERGE.md, docs/02_MAKALE_ANALIZI.md, docs/03_MIMARI.md, docs/05_KURALLAR.md, docs/07_DENEY_PLANI.md
Orijinal PDF'ler references/papers/ altında (yönerge + makale). .md özetleri ile PDF çelişirse PDF esastır; fark bulursan bana söyle ve .md'yi düzelt.

PROJE ÖZETİ: Wu et al. (2024, ESWA 256:124943) "Adaptive sparse regularized fuzzy clustering noise image segmentation..." makalesini inceleyip yeniden gerçekleştireceğiz (FCM + ödül/ceza kümeli yerel bilgi + DTCWT alanında non-local bilgi + adaptif α,β,γ + ℓ0 seyrek düzenlileştirme), üzerine özgün bir katkı geliştirip kontrollü deneylerle baseline ile karşılaştıracağız; sonra rapor (8-12 sf, IEEE), GitHub ve sunum hazırlayacağız. Son teslim 27.10.2026, sunumlar 03.11.2026. Bugün 18.10.2026.

KURALLAR (docs/05_KURALLAR.md'nin özeti):
- Uydurma kaynak, yapılmamış deney, üretilmemiş sonuç YOK. Her atıfı DOI ile doğrula. Rapordaki her sayı ya bizim koşumuzdan ya da "makalede raporlanan" etiketli.
- Yazdığın her kodu ben savunmada açıklayabilmeliyim: kısa yorumlar yaz, yeni kavramları sohbet tonunda ve gerektiğinde benzetmelerle anlat; ben anlamadan bir sonraki modüle geçme.
- Küçük ve sık git commit'leri at (faz<N>: ...). Gizli bilgi commit'leme.
- Makaleden her sapmayı kodda "# DEVIATION:" ile işaretle ve docs/06_KARARLAR.md'ye yaz.
- Claude'un katkılarını docs/genai_usage_log.md'ye kaydet.
- Bekleyen/Açık kararları (docs/06_KARARLAR.md B ve C bölümü) bana sorulmadan kesinleştirme.

İLK GÖREVİN (henüz kod yazma):
1. Yukarıdaki dosyaları oku ve bana 10 satırı geçmeyen bir anlayış özeti çıkar (proje, puanlama, takvim, şu anki faz).
2. docs/02_MAKALE_ANALIZI.md içindeki denklemleri ve parametreleri references/papers/Wu_2024_ASRFCM_ESWA.pdf ile karşılaştır; bulduğun hataları/tutarsızlıkları listele (özellikle §9'daki belirsizlikler).
3. docs/06_KARARLAR.md'deki "Öneri" ve "Açık" maddeleri için bana kısa, net sorular sor (hocadan teyit gerekenleri ayrı listele; hocaya gönderebileceğim kısa bir mesaj taslağı da hazırla).
4. Faz 0'ın adımlarını (git init, ortam kurulumu, ilk commit, import testi) 5-6 maddelik plan olarak sun ve onayımı bekle.

Onayımdan sonra Faz 0'ı yap, sonra sırayla Faz 1, 2, 3... ilerleyelim. Her faz sonunda: ne yapıldı, neyi benim doğrulamam gerek, sıradaki adım.
```

## Sonraki oturumlar için kısa prompt

```
Devam ediyoruz. CLAUDE.md, docs/04_FAZLAR_VE_YOL_HARITASI.md ve docs/06_KARARLAR.md'yi oku, nerede kaldığımızı özetle, sıradaki adımı 3-6 maddelik planla öner ve onayımı bekle.
```

## Faz bazlı hazır promptlar (ihtiyaç oldukça kullan)

**Faz 1 (makale + literatür):**
```
Faz 1'e geçelim. 1) Makale analizini PDF ile doğrula, CP1 için 1-2 sayfalık özet çıkar. 2) Literatür için references/README.md'deki B listesini DOI'leriyle doğrula (WebSearch/WebFetch), ardından 2022-2026 arası en az 5 gerçek ek çalışma bul; her birini DOI ile doğrula ve karşılaştırma tablosunu doldur. Doğrulayamadığını listeye ALMA. Sonunda Related Work taslağı yaz.
```

**Faz 2 (altyapı):**
```
Faz 2: src/data/synthetic.py (sy1-3), src/data/noise.py, src/eval/metrics.py + matching.py ve testlerini yaz (docs/03_MIMARI.md ve docs/06_KARARLAR.md D-008, D-009'a göre). Her modülü yazdıktan sonra bana kısaca anlat, testleri çalıştır, commit at.
```

**Faz 3 (baseline + yeniden gerçekleştirme):**
```
Faz 3a: baseline_fcm.py'yi yaz, test et, sy1-3 üzerinde çalıştır ve makale FCM sütunuyla (results/tables/paper_reported_fcm_vs_ours.csv) karşılaştır. Sonra sırayla 3b (local_info), 3c (nonlocal_wavelet), 3d (adaptive_params), 3e (sparse_fcm). Her modül sonrası dur, bana anlat, ben onaylayınca devam et.
```

**Faz 4-5 (katkı + deney):**
```
Katkı olarak [C1+C2 / seçimim] ile devam ediyorum. Önce 1 sayfalık katkı öneri metni (gerekçe, hipotez, başarı ölçütü, deney tasarımı) yaz; onayımdan sonra variants.py ve experiments/ betiklerini yaz. 10 seed ile çalıştır, CSV'leri üret, tablo/figürleri betikle oluştur. Sonuç beklediğimiz gibi çıkmazsa olduğu gibi raporla ve nedenlerini analiz et.
```

**Faz 6-7 (rapor + sunum):**
```
docs/08_RAPOR_ISKELETI.md'ye göre raporu yaz (İngilizce, IEEE, 8-12 sf, kaynakça hariç) ve GenAI Disclosure bölümünü docs/genai_usage_log.md'ye göre doldur. Sonra docs/09_SUNUM_SAVUNMA.md'ye göre sunumu hazırla. Tüm sayılar results/tables/*.csv'den gelsin.
```

**Faz 8 (teslim kontrolü):**
```
docs/01_YONERGE.md §20 teslim kontrol listesini tek tek doğrula: temiz ortamda klonla→kur→çalıştır, gizli bilgi taraması, README başlıkları, rapor sayfa sayısı, kaynak doğrulaması. Eksikleri listele ve düzelt.
```
