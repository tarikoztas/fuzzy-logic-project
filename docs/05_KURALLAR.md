# 05 — Kurallar (Claude Code ve Öğrenci için)

Bu kurallar yönergenin puanlama ve etik maddelerinden türetilmiştir. İhlal = puan kaybı veya akademik etik sorunu.

## 1. Akademik etik (yönerge §16)

- Uydurma kaynak, yapılmamış deney, üretilmemiş sonuç **kesinlikle yok**.
- Raporlanan her sayı şu ikisinden biri olmalı: (a) bizim koşturduğumuz deneyden (CSV + seed + commit ile izlenebilir) (b) makaleden aktarılmış ve **"makalede raporlanan"** diye etiketli.
- Başka öğrencinin kodu/raporu kullanılmaz. Dış kod: dosya başında kaynak URL + lisans + değişiklik notu; `src/third_party/` altında.
- Makalenin resmi kodu bulunursa: kullanılıp kullanılmadığı rapor + README'de **açıkça** belirtilir. Kendi kodumuz ile dış kod ayırt edilebilir olur. (Tavsiye: sıfırdan yaz; resmi kodu yalnızca doğrulama için karşılaştır ve belirt.)
- Telif: yayıncı PDF'ini (Elsevier) public repoya **koyma** (`.gitignore`'da); makaleden alıntıyı kısa tut, kendi cümlenle yaz.

## 2. Kaynak/atıf doğrulama (yönerge §15)

- Hiçbir atıf hafızadan yazılmaz. Her kaynak için: başlık+yazar+yıl+yayın yeri+**DOI** doğrulanır (DOI bağlantısı açılır, başlık eşleşir).
- Doğrulanamayan kaynak → kullanma.
- Makalenin kaynakçasındaki kaynaklar, makalede verilen DOI ile kullanılabilir; yine de DOI'nin açıldığı kontrol edilir.
- Biçim: IEEE (`[1] A. Author, "Title," *Journal*, vol. x, no. y, pp. a–b, Year, doi: ...`).

## 3. Üretken YZ şeffaflığı (yönerge §15)

- Bu projede Claude (chat + Claude Code) kullanılıyor. Kullanım şekilleri `docs/genai_usage_log.md` içinde **tarihli** tutulur: kod geliştirme, hata ayıklama, kavram açıklama, dil düzenleme, literatür yardımı.
- Rapor sonunda **"Generative AI Usage Disclosure"** bölümü bu log'dan yazılır; gerçeği yansıtır (kullanılmayanı kullanılmış gibi, kullanılanı gizleyerek yazma).
- Öğrenci, YZ'nin ürettiği her kod/algoritma/grafik/açıklamayı **anlar ve doğrular**; savunmada açıklayabilir olmalı.

## 4. Kod standartları

- Python 3.10+, tür ipuçları, kısa docstring (ne yapar + hangi denklem/algoritma: `# Eq. (12)`).
- **Denklem izlenebilirliği:** her ana fonksiyon makale denklem numarasını yorumda belirtir.
- Küçük, test edilebilir fonksiyonlar; global durum yok; seed parametresi açık.
- Sihirli sayı yok: parametreler config/varsayılan argüman (makale değerleri `src/utils/config.py` içinde adlandırılmış sabit).
- Biçim: `black` + `ruff` (opsiyonel). Gereksiz karmaşıklık yok — savunmada anlatabileceğin kadar basit.
- Makaleden sapma (ör. boş sütun politikası, y_q düzeltmesi) kodda `# DEVIATION:` yorumu + `docs/06_KARARLAR.md` kaydı.

## 5. Deney standartları (puan: "deney tasarımı", "adil karşılaştırma")

- Aynı veri/gürültü/seed/K/m/ε/T; tek değişken değişir.
- Rastgele başlatma → **≥10 seed**, ortalama ± std; tek koşu sonucu "kanıt" sayılmaz.
- Parametre ayarı (σ, k, δ, w) ayrı doğrulama görüntülerinde; test görüntülerinde sabit.
- Ölçülen süre: ön-işleme ile kümeleme ayrı; aynı makine; JIT ısınması hariç.
- Sonuçlar betikle CSV'ye yazılır; tablo/figürler CSV'den üretilir (elle kopyalama yok).
- Baseline'dan kötü sonuç çıkarsa **olduğu gibi raporla**, olası nedenleri tartış (yönerge buna puan verir).

## 6. Git kuralları (yönerge §9)

- Küçük ve sık commit; her mantıksal adım ayrı commit. Final haftasına yığılma yok.
- Mesaj: `faz<N>: <özet>` (ör. `faz3: add local_info (Alg.2) + unit test`).
- `main` dalı çalışır durumda kalsın; büyük denemeler `exp/<ad>` dalında.
- Yüklenmeyecekler: `.venv/`, büyük veri, gizli bilgiler, yayıncı PDF'i, geçici dosyalar (`.gitignore`).
- Gizli bilgi: API anahtarı, parola, token **asla** commit'lenmez; `git grep` ile teslim öncesi kontrol.

## 7. Dokümantasyon standartları

- README yönergedeki 15 başlığı eksiksiz içerir; **"How to Run"** temiz ortamda doğrulanmış olmalı.
- Her figür: başlık, eksen/birim, hangi deney/seed; her tablo: kaynak etiketi (makale/bizim).
- Rapor: 8–12 sayfa (kaynakça hariç), yönergedeki 11 bölüm sırası + GenAI Disclosure.

## 8. Claude Code çalışma protokolü

1. Oturum başında: `CLAUDE.md` → `docs/04` → `docs/06` oku; mevcut fazı özetle.
2. Büyük adımdan önce 3–6 maddelik plan sun; onay al.
3. Kodu yaz, test et, **çalıştır**; sonucu göster. "Çalışır" demeden önce komutu gerçekten koştur.
4. Bitirince: ne yapıldı + öğrencinin doğrulaması gerekenler + sıradaki adım (kısa).
5. Öğrenme modu: yeni bir kavramı (ör. DTCWT, ℓ0 norm, hard threshold) sohbet tonunda, gerektiğinde gündelik bir benzetmeyle açıkla. Öğrenci "anladım" demeden o modülü "bitti" sayma.
6. Belirsizlikte tahmin yürütüp ilerleme; `docs/06_KARARLAR.md`'ye "Açık" olarak yaz ve öğrenciye sor.
7. Makale ile PDF çelişirse **PDF** esas; `.md` dosyasını düzelt.
8. Sonuç uydurma, "makalede böyle çıkıyor" diye kendi çıktıyı eşitleme, metrik hesabını sonuca göre ayarlama **yasak**.
9. Her anlamlı YZ katkısını `docs/genai_usage_log.md`'ye kısa not düş.

## 9. Savunma odaklı yazım

Kod şu soruları cevaplatabilmeli: bu satır ne yapıyor? neden bu parametre? parametre değişirse ne olur? hangi denklem? başarısız olduğu durum? Gerekirse `docs/` altına "modül açıklama" notu ekle (kısa, kendi cümlenle).
