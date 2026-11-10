# Hocaya gönderilecek mesaj (taslak)

İlgili kararlar: `docs/06_KARARLAR.md` C bölümü (D-004, D-017…D-021) ve takvim. Cevap gelince oradaki "Durum" sütununu ve `docs/04` takvimini güncelle.
Gönderim: Classroom özel yorum veya e-posta. Konu satırı önerisi: **"Bulanık Mantık Dönem Projesi – Kapsam ve Teslim Teyidi (Tarık Öztaş, 1306230040)"**

---

Sayın Hocam,

Bulanık Mantık dönem projesi kapsamında sorumlu olduğum makale:

> J. Wu, X. Wang, Y. Liu, C. Fang, "Adaptive sparse regularized fuzzy clustering noise image segmentation algorithm based on complementary spatial information," *Expert Systems With Applications*, vol. 256, 124943, 2024. doi: 10.1016/j.eswa.2024.124943

Makale, gürültülü görüntülerin segmentasyonu için Fuzzy C-Means (FCM) tabanlı bir yöntem öneriyor: (i) ödül/ceza kümeleriyle yerel uzamsal bilgi, (ii) dual-tree karmaşık dalgacık (DTCWT) alanında yerel-olmayan bilgi, (iii) adaptif ağırlık katsayıları ve (iv) üyelik matrisine ℓ0 seyrek düzenlileştirme. Projeyi yönergeye uygun yürütebilmek için aşağıdaki noktalarda teyidinizi rica ediyorum.

**1. Bulanık sistem bileşenlerinin karşılığı.** Yöntem Mamdani/Sugeno gibi kural tabanlı bir çıkarım sistemi değil, bulanık kümeleme yöntemi. Yönergedeki maddeleri şöyle eşleyerek gerçekleştirmeyi planlıyorum:
- Girdi/çıktı: gürültülü gri seviye görüntü → üyelik matrisi, küme merkezleri ve etiket haritası
- Üyelik fonksiyonu: FCM üyelik dereceleri u_ij (ayrıca yöntemdeki Gauss tipi benzerlik çekirdekleri)
- Kural tabanı / çıkarım: açık IF–THEN kuralı yerine amaç fonksiyonunun minimizasyonu ("piksel bir küme merkezine ne kadar yakınsa o kümeye üyeliği o kadar yüksek")
- Durulaştırma (defuzzification): en yüksek üyelik (argmax) ile kesin etiket ataması

Bu eşleme "fuzzy sistemin gerçekleştirilmesi" ölçütü için yeterli midir, yoksa ek olarak açık bir kural tabanı/çıkarım bileşeni (ör. küçük bir Mamdani modülü) eklememi bekler misiniz?

**2. MRR (Minimum Reproduction Requirement).** Önerim:
- Baseline: klasik FCM
- Makalenin yöntemi eksiksiz: yerel bilgi + DTCWT alanında yerel-olmayan bilgi + adaptif katsayılar + seyrek düzenlileştirmeli üç adımlı çözüm
- Yeniden üretilecek deneyler: üç sentetik görüntüde %1/5/10/15 karışık gürültü altında FCM ile önerilen yöntemin karşılaştırılması (makale Tablo 2–8, altı metrik + iterasyon) ve üç bileşenin ablasyonu (Tablo 1); ek olarak BSDS500'den 8 gerçek görüntü (Tablo 9)
- Makaledeki diğer 8 karşılaştırma yöntemini (FGFCM, FRFCM, FSC_LNML vb.) yeniden yazmayı planlamıyorum; onlar için makalede raporlanan değerleri "makalede raporlanan" etiketiyle kullanacağım.

Bu kapsam uygun mudur?

**3. Veri ile ilgili not.** Makalenin sentetik görüntüleri ve karışık gürültünün tam tanımı (varyans/oran) paylaşılmamış. Görüntüleri makaledeki şekillere benzer biçimde yeniden üretip gürültü tanımını raporda açıkça belirteceğim; bu nedenle sayısal sonuçlar makaledekilerle birebir aynı çıkmayabilir. Bu yaklaşım kabul edilebilir mi?

**4. Özgün katkı planı.** (a) Gürültü türüne göre (Gaussian, tuz-biber, çarpımsal ayrı ayrı ve karışık; %0–20) dayanıklılık analizi — makalede yalnızca karışık gürültü var; (b) ablasyon ve parametre analizi: altın oran (0.618) ödül oranının ve diğer parametrelerin etkisi, makaledeki belirsiz noktalar için alternatif seçenekler. Bu kapsam "özgün katkı" için yeterli midir, yoksa yönteme yeni bir bileşen eklememi mi beklersiniz?

**5. Checkpoint'ler ve takvim.** CP1–CP5'in tarihleri ve her birinde Classroom'a ne yüklenmesi gerektiği nedir? Ayrıca son teslim (27.10.2026) ve sunum (03.11.2026) tarihlerinde bir değişiklik var mı?

**6. Rapor.** Rapor Türkçe mi İngilizce mi olmalı? IEEE konferans şablonu (iki sütun) uygun mu; 8–12 sayfa sınırı bu şablon için mi geçerli?

**7. Resmi kod ve yapay zekâ kullanımı.** Kodu sıfırdan yazıyorum. Yazarların resmi bir kodu bulunursa yalnızca doğrulama amacıyla kullanıp rapor ve README'de belirtmem yeterli midir? Geliştirme sürecinde Claude (Anthropic) kullanıyorum; kullanım şeklini tarihli olarak kayıt altına alıyorum ve raporda "Generative AI Usage Disclosure" bölümünde açıklayacağım.

**8. Sunum ve demo.** Sunum PDF mi PPTX mi olmalı? Canlı demo kendi bilgisayarımdan mı yapılacak? Ayrıca GitHub reposunun teslimde herkese açık (public) olması mı gerekiyor, yoksa size erişim vermem yeterli mi?

Zaman ayırdığınız için teşekkür ederim.

Saygılarımla,
Tarık Öztaş
1306230040 — Bilgisayar Mühendisliği
