# 11 — Literatür Notları (savunma için, Türkçe)

Künyeler ve köşeli parantez numaraları: `references/README.md`. Bu dosya **anlamak** için; rapora girecek İngilizce metin `report/drafts/related_work.md`.
Kaynak: klasik yöntemler için makalenin [1] kendi anlatımı (§1, §4), yeni çalışmalar için abstract'lar. Abstract'ı okunamayanlar ayrıca işaretli.

## Büyük resim: hikâye 4 adımda

1. **FCM (1984)** — her piksel her kümeye bir derecede ait. Sorun: pikseli yalnız başına değerlendirir, gürültüye çok hassas.
2. **"Komşulara bak" dönemi (2002–2019)** — yerel uzamsal bilgi. BCFCM komşuları amaç fonksiyonuna ekledi; FCM_S1/S2 önceden ortalama/medyan filtreli görüntü kullanarak hızlandırdı; FGFCM gri seviye histogramıyla daha da hızlandı; FLICM parametre gerektirmeyen bir "bulanık faktör" getirdi ve bir aile doğurdu (KWFLICM, ADFLICM, DSFCM_N).
   *Benzetme:* Bir öğrencinin notundan emin değilsen sıra arkadaşlarına bakarsın. Ama sıradakilerin de bir kısmı kopya çekmişse (gürültü), ortalama yanıltır.
3. **"Uzaktaki benzerlere de bak" dönemi** — yerel-olmayan (non-local) bilgi. FCM_SNLS: görüntünün başka yerlerinde *benzer desenli* bloklar varsa onlardan öğren. FALRCM, FSC_LNML: yerel + yerel-olmayan birlikte.
   *Benzetme:* Sıra arkadaşları güvenilmezse, başka sınıflardaki benzer profildeki öğrencilere bakarsın.
4. **"Dönüşüm alanı + seyreklik" dönemi** — WFCM ve SRFCM dalgacık (wavelet frame) alanında çalıştı; SRFCM üyelik matrisine seyreklik ekledi; DSFCM_N sapmayı seyrek modelledi.

**Bizim makale [1]** bu dört çizgiyi birleştiriyor: ortalama yerine ödül/ceza kümeli yerel bilgi + DTCWT alanında yerel-olmayan bilgi + piksel başına adaptif ağırlık + ℓ0 seyreklik.

## Yöntem kartları (her biri: ne yapar / güçlü / zayıf)

| Yöntem | Ne yapar (1–2 cümle) | Güçlü | Zayıf |
|---|---|---|---|
| FCM [2] | Merkezlere uzaklığa göre üyelik dağıtır, merkezleri üyelik ağırlıklı ortalamayla günceller | Basit, hızlı, O(n³) | Uzamsal bilgi yok → gürültüye hassas |
| BCFCM [8] | Komşuluk terimini amaç fonksiyonuna ekler + MR görüntüde bias alanı düzeltir | Uzamsal bilgiyi ilk ekleyen ([1]'e göre) | Yavaş: her iterasyonda komşuluk hesabı |
| FCM_S1/S2 [9] | Komşuluk terimini önceden hesaplanmış ortalama/medyan filtreli görüntüyle değiştirir; çekirdek uzaklığı | BCFCM'den hızlı | Komşuluk ağırlığı elle ayarlanır |
| FGFCM [10] | Uzamsal + gri benzerlikle yeni görüntü üretir, gri seviye histogramı üzerinde kümeler | Çok hızlı (histogram < piksel) | Katsayılar adaptif değil |
| FLICM [11] | Parametresiz bulanık faktörle komşu etkisini uzaklığa göre ayarlar | Ayarlanacak parametre yok, kararlı | Komşular gürültülüyse yetmez |
| FCM_SNLS [12] | Benzer bloklardan yerel-olmayan bilgi, kendi ayarlanan parametreyle | Yüksek gürültüde yerelden daha dayanıklı | Pahalı; uzamsal alanda kenar kaybı ([1]'in eleştirisi) |
| KWFLICM [13] | FLICM + çekirdek metrik | Doğrusal olmayan ayrım | Daha pahalı |
| ADFLICM [14] | Piksel uzay çekim modeliyle adaptif FLICM | Adaptif | [1] tablolarında yüksek gürültüde düşük (ör. sy2 %10 V_PC 40.20) |
| FRFCM [15] | Morfolojik rekonstrüksiyonla ön-işleme + üyelik filtresi, histogramda kümeleme | Çok hızlı, O(n³) | Karışık/yüksek gürültüde zayıf ([1]'e göre) |
| DSFCM_N [16] | Gürültüyü seyrek bir sapma (deviation) olarak modelleyip gerçek değeri tahmin eder | Seyreklik fikri | [1] tablolarında bazı görüntülerde çöküyor (sy2 %10 ACC 15.00) |
| WFCM [17] | Dalgacık çerçevesi (wavelet frame) alanında FCM | Dönüşüm alanında gürültü bastırma | — |
| FCM_SICM [18] | Bilateral filtreyle uzamsal/yoğunluk bilgisi, adaptif kısıt, üyelik bağlama (hız) | Az iterasyon | O(n⁴) |
| SRFCM [19] | Morfolojik rekonstrüksiyon + dalgacık çerçevesi + üyeliğe seyrek düzenlileştirme | [1]'in seyreklik çözüm çerçevesi buradan (Eq. 23–27) | Ters dönüşüm kusursuz değilse hata ([1] §4.6.1) |
| FALRCM [20] | Yerel + bölge düzeyi bilgi, medyan üyelik | Yerel-olmayanın gürültüyü "aşırı korumasını" azaltır | — |
| CGFFCM [21] | Küme ve öznitelik ağırlıklarını öğrenen renkli FCM | Otomatik ağırlık | Uzamsal bilgi yok → gürültüye hassas ([1]) |
| FSC_LNML [22] | Bulanık alt-uzay + adaptif yerel varyans + yerel-olmayan bilgi + ortalama üyelik bağlama | [1]'e en yakın rakip; NMI varyansı en düşük (2.48) | En yavaş yöntem ([1] Fig. 29) |

## Yeni çalışmalar (2022–2026) — ne söylüyorlar

| # | Kısaca | Neden bizim için önemli |
|---|---|---|
| [24] Jiao 2023 (TFS) | Bölgesel + yerel filtreyle "ağırlıklı görüntü"; orijinal ile ağırlıklı görüntü arasındaki farka göre piksel piksel adaptif kısıt; yakınsamayı hızlandırma | Aynı laboratuvar (Lanzhou Jiaotong). α, β, γ fikrinin kardeşi. Ayrıca "yerel bilgi yüksek gürültüde yetmez, yerel-olmayan bilgi gürültüyü fazla korur" tespiti [1]'in motivasyonunu destekliyor |
| [25] Chen 2023 (TIP) | Seyrek alt-uzay kümeleme + bulanık üyelik, kızılötesi görüntü | "Seyreklik" kelimesinin farklı anlamı: global ilişki için seyrek öz-temsil. Bizde seyreklik = üyelik matrisinde sıfır sayısı. Savunmada karıştırma |
| [26] Lei 2023 (Appl. Intell.) | Derin bulanık K-means + komşu medyan/ortalama + çekirdek | Derin öğrenme yönü; [1] ise yorumlanabilir ve eğitimsiz |
| [27] Wu & Zhou 2024 (Symmetry) | "Harmonik" bulanık bölümleme (toplam=1 kısıtı yerine), yakınsama ispatı | Bulanık kümenin tanımını değiştiriyor → derste gördüğümüz bulanık küme teorisine bağlanır |
| [28] Das 2025 (CBM) | Histogram tepelerinden **K'yı otomatik bulma** + yerel uzlaşı üyeliği | [1]'e atıf yapıyor ve [1]'in "K önceden bilinmeli" sınırlılığını hedefliyor → katkı adayı C3 için dayanak |

Abstract'ı okunamayanlar ([29]–[33]): künyesi doğrulandı, içerik iddiası yok. Özellikle **[29] Wu 2023 (CVIU)** aynı ilk yazarın bir yıl önceki makalesi; üniversite erişiminle okunmalı.

## Savunmada çıkabilecek sorular

- *"FLICM'den farkı ne?"* → FLICM komşuları uzaklığa göre ağırlıklandırır ama hepsini eşit güvenilir sayar; [1] komşuları gri değere göre sıralayıp uçtakileri (muhtemel gürültü) cezalandırır.
- *"SRFCM'den farkı ne?"* → İkisi de seyreklik + dalgacık kullanır. SRFCM morfolojik rekonstrüksiyon ve wavelet frame kullanır, yerel-olmayan bilgisi ve adaptif ağırlığı yok. [1] DTCWT alanında yerel-olmayan bilgi kullanır ve α, β, γ'yı piksel başına hesaplar.
- *"Neden en yakın rakip FSC_LNML?"* → Yerel + yerel-olmayan + adaptif kullanıyor ama uzamsal alanda ve seyreklik yok; en yavaş yöntem.
- *"Literatürde hangi yön var?"* → Tip-2 bulanık kümeler ([30], [33]), sezgisel bulanık kümeler ([31]), derin bulanık kümeleme ([26]), otomatik K ([28]).
