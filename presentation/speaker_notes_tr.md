# Konuşmacı notları

## 1. Gürültülü Görüntü Bölütleme için Uyarlamalı Seyrek Düzenlileştirilmiş Bulanık Kümeleme

Kendinizi ve makaleyi tanıtın. Neleri göstereceğinizi söyleyin: yeniden gerçekleştirme, yeniden üretim, bulanık kural tabanlı geliştirmenin iki iterasyonu ve dürüst bir değerlendirme.

## 2. Görüntü bölütleme: nedir, neden önemlidir?

Gündelik anlamdan başlayın: görüntüyü bölgelere göre boyamak. Şekli gösterin: düz FCM gürültüden şaşırıyor, referans yöntem bölgeleri geri kazanıyor. Sunumun tamamı bu problemle ilgili.

## 3. Referans makaleye genel bakış

Yazarları ve dergiyi söyleyin. Fikri tek cümleyle anlatın: tek bir gürültülü piksele güvenme; onu iki daha temiz kestirimle birleştir ve her piksel için hangisine ne kadar güvenileceğine karar ver. Ayrıntılar yöntem bölümünde.

## 4. Bu proje: ne yaptık, ne işe yarıyor?

Dinleyicinin ne kazandığını söyleyin: sınanmış bir uygulama, yorumlanabilir kurallar ve otomatik parametre seçimi. Yönergenin iyileşmeyi zorunlu tutmadığını, ama ikinci iterasyonumuzun yöntemi aynı koşullarda iyileştirdiğini belirtin.

## 5. Sunumun akışı

Kısa tutun (20 saniye).

## 6. Gürültülü görüntüler düz bulanık kümeleme için neden zor?

Gürültülü görüntüleri ve FCM'nin nasıl başarısız olduğunu gösterin. Sorulursa: FCM, Σ_i u = 1 koşuluyla Σ u^m (y − c)² değerini en küçükler; karışık gürültü Gauss + benek + tuz-biberdir (sy3, %15: ACC ≈ %56).

## 7. Önceki çalışmalar FCM'ye gürültüye karşı nasıl yardım ediyor?

İsim sorulursa: yerel — BCFCM, FCM_S, FGFCM, FLICM, FRFCM; yerel-olmayan — FCM_SNLS, FALRCM, FSC_LNML; dalgacık/seyrek — WFCM, SRFCM, DSFCM_N.

## 8. Üç fikirde bulanık mantık

Derslerle bağ kurun. Sorulursa: VE = min, çıkarım = min (kırpma), birleştirme = max; durulaştırma ağırlık merkezi, açıortay ya da maksimumların ortalamasıyla; Sugeno sabit çıktılar ve ağırlıklı ortalama kullanır.

## 9. Yöntem nasıl çalışıyor?

Şekli soldan sağa anlatın. Turuncu kutu = ilk iterasyonumuz (ağırlıklar); ikinci iterasyon 1. görüşün içindeki σ'yı değiştiriyor. Sorulursa: uzaklık d = α(y−c)² + β(ξ−c)² + γ(ϑ−c)², ξ = yerel, ϑ = yerel-olmayan kestirim.

## 10. 1. görüş: komşuların adil oylaması

Sorulursa: ödül ağırlığı 1+σ, ceza ağırlığı 1−σ, bunlar exp(−Δgri²/τ²)·exp(−uzaklık) ile çarpılır; ödül kümesi boyutu ⌊0.618·(N_R−1)⌋; makalenin Şekil 1'i birebir yeniden üretildi (D-014).

## 11. 2. görüş: dalgacık alanında temizleme

Sorulursa: çift ağaçlı karmaşık dalgacık dönüşümü (DTCWT), 1 alçak geçiren + ±15°, ±45°, ±75°'de 6 alt bant; 15×15 arama penceresi ve 5×5 yamalarla yerel-olmayan ortalama, h² = 250.

## 12. Üç görüşü tartmak

Sorulursa: ΔG1 = k·exp(y − ξ), ΔG2 = k·exp(y − ϑ); α = 1/(ΔG1+ΔG2), β = ΔG1, γ = ΔG2, k = 15; amaç Σ u^m d + δ‖U‖₀, sert eşik √δ = 0.63, ardından normalize; w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4, m=2.

## 13. Projedeki bulanık sistemler bir bakışta

Bu slayt yönergenin istediği öğeleri karşılıyor: girdi/çıktı, üyelik fonksiyonları, kural tabanı, çıkarım, durulaştırma — makale ve iki iterasyon için.

## 14. Nasıl test ettik?

Sorulursa: karışık gürültü %p = Gauss(varyans p) → benek(varyans p) → tuz-biber(p); ölçütler V_PC, V_PE, ACC, F, NMI, Kappa; etiketlerin Macar yöntemiyle eşlenmesi; eşleştirilmiş Wilcoxon testleri; 97 birim testi.

## 15. Makale neler raporluyor?

Bunlar makalede raporlanan sayılar (Tablo 1–9); her yerde böyle etiketli.

## 16. Makaleyi yeniden üretebildik mi?

FCM uyumu görüntüleri ve gürültüyü doğruluyor. Üç bölgeli görüntülerdeki yüksek gürültü farkı sonraki slaytta açıklanıyor (σ ayarı).

## 17. Hangi parçalar önemli?

Sorulursa: yalnız yerel-olmayan terim 97.5–99.6, yalnız yerel 97.5–99.9 (makale: %82.26); %5 gürültüde σ, w ve δ ACC'yi 0.4 puandan az değiştiriyor, k = 1 bozuyor, δ esas olarak iterasyon sayısını belirliyor.

## 18. İterasyon 1: güven ağırlıkları için bulanık kurallar

Şekli anlatın: hangi kurallar ateşleniyor, çıkış kümesi nasıl oluşuyor, sonuç. Sorulursa: girdiler Dev = |y − (ξ+ϑ)/2| ve Dis = |ξ − ϑ|; çıktılar α, β, γ; sonradan eklenen 'split' varyantı makalenin α'sını koruyup yalnız β : γ'yı paylaştırıyor.

## 19. Sonuç: ilk kurallar doğruluğu artırmadı

Olumsuz sonuç dürüstçe raporlandı — yönerge iyileşmeyi zorunlu tutmuyor ama analiz edilmesini istiyor. Sorulursa: H1 hipotezi reddedildi; '*' = eşleştirilmiş Wilcoxon p < 0.05.

## 20. Neden başarısız oldu?

Bu teşhis ikinci iterasyona köprü. Sorulursa: H3 ve H4 tuttu; kurallar temiz / %1 gürültüde en iyi, çünkü orada tutarlı piksellere güvenmek doğru.

## 21. İterasyon 2: σ'yı bulanık bir kural seçsin

Protokolü anlatın: ayar 100–104 tohumlarında, test 0–9'da; izin verilen 12 konfigürasyonun 9'u denendi; H5/H6 hipotezleri testten önce commit'lendi. Sorulursa: gürültü tahmini = Haar dönüşümünün median(|HH|)/0.6745 değeri; σ çıktıları 0.3 / 0.6 / 0.95; iki aday daha denendi (sınırlı α, dürtü girdisi). Fikir, σ üzerindeki önceki testten geldi — test parametrelere kör, fikre değil.

## 22. Sonuç: yüksek gürültüde belirgin kazanç

Kuralın değeri σ'yı otomatik seçmesi; karışık gürültüde sabit σ = 0.9 da aynı derecede iyi (farklar -0.02 … +0.19). 'Bulanık σ + sınırlı güven' (FIS-σ+A) ayrıca gürültülü piksele duyulan güveni sınırlıyor; ilk kural tabanını zararsız hâle getiriyor (en kötü fark +0.00). Sorulursa: %10 ve %15'te p < 0.001; %15'te sy2/sy3 97.00/95.08'e ulaşıyor.

## 23. Test görüntülerinin dışında da çalışıyor mu?

Sorulursa: %0–20 aralığında dört gürültü türünde bulanık σ ile sabit σ = 0.9 arasındaki fark -0.31 … +0.24 puan; tuz-biber %20: tahmin 0, sabit 0.9 biraz daha iyi.

## 24. Makalenin kendi sayılarına göre: daha yakın, ama daha iyi değil

İki karşılaştırmayı ayırın. Aynı kod, aynı gürültü: bulanık σ %10–15'te makale ayarını geçiyor, hiçbir yerde anlamlı kaybı yok. Makalede basılı sayılara göre (başka uygulama, başka gürültü; yalnızca yol gösterici): düşük gürültüde eşit, %15'te sy2/sy3'te hâlâ 1.53/2.28 puan aşağıda (önce 6.15/8.23). 'Makaleyi geçtik' demeyin.

## 25. Gerçek fotoğraflar (BSDS500)

Makaledeki fotoğraflar renkli, bu yüzden yöntemin renkli bir sürümünü de çalıştırdık (D-043). Sorulursa: split varyantı 78.70, H2 hipotezi reddedildi.

## 26. Ne öğrendik — ve sınırlar

Neyin yapılıp neyin yapılmadığını açıkça söyleyin; yönerge yalnız doğruluğu değil analizi de değerlendiriyor. Sorulursa: makaledeki 8 karşılaştırma yöntemi yeniden yazılmadı; iterasyon 2 aynı görüntülerin başka gürültü tohumlarıyla ayarlandı.

## 27. Sonuç

Tek cümleyle özetleyin, teşekkür edin ve soruları davet edin.