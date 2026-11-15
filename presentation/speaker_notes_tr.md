# Konuşmacı notları

## 1. Gürültülü Görüntü Bölütleme için Uyarlamalı Seyrek Düzenlileştirilmiş Bulanık Kümeleme Yönteminin Yeniden Gerçekleştirilmesi ve Mamdani Kural Tabanlarıyla Geliştirilmesi

Kendinizi ve makaleyi tanıtın. Neleri göstereceğinizi söyleyin: yeniden gerçekleştirme, yeniden üretim, bulanık kural tabanlı geliştirmenin iki iterasyonu ve dürüst bir değerlendirme.

## 2. Gürültülü görüntü bölütleme FCM için neden zor?

Gürültülü görüntüleri ve FCM'nin nasıl başarısız olduğunu gösterin. Motivasyon: gerçek görüntülerde (tıbbi, uzaktan algılama) aynı anda birkaç gürültü türü bulunur.

## 3. Önceki çalışmalar FCM'ye uzamsal bilgiyi nasıl ekliyor?

Dört akımı anlatın; makale beş bileşeni birleştiren tek çalışma. En yakın akrabaları: SRFCM (seyreklik çerçevesi) ve FSC_LNML (aynı laboratuvar).

## 4. Bulanık kümeler, bulanık kümeleme ve bulanık çıkarım

Derslerle bağ kurun. FCM üyelik matrisi nedeniyle bulanıktır; makalede açık bir kural tabanı yok — geliştirmemizin çıkış noktası bu.

## 5. Yöntemin mimarisi (ve geliştirmemizin yeri)

Akışı soldan sağa anlatın. Turuncu kutu = katkımızın ilk iterasyonu; ikinci iterasyon ξ kutusunun içindeki σ'ya etki ediyor.

## 6. Yerel bilgi ξ: altın oranlı ödül ve ceza kümeleri

Benzetme: en uç puanları silmeyen ama ağırlığını düşüren bir jüri. Küme boyutunu makalenin Şekil 1'indeki gibi aşağı yuvarlıyoruz (D-014).

## 7. Dalgacık alanında yerel-olmayan bilgi ϑ

DTCWT'yi bir şarkıyı bas/orta/tiz kanallarına ayırma benzetmesiyle anlatın.

## 8. Uyarlamalı katsayılar ve seyrek düzenlileştirilmiş FCM

Katsayıların ölçeğini vurgulayın — geliştirmemiz için önemli hâle geliyor.

## 9. Projedeki bulanık sistemler bir bakışta

Bu slayt yönergenin istediği öğeleri karşılıyor: girdi/çıktı, üyelik fonksiyonları, kural tabanı, çıkarım, durulaştırma — makale ve iki iterasyon için.

## 10. Veri, gürültü ve protokol

Adilliği vurgulayın: aynı gürültü örnekleri ve başlangıçlar; her seferinde tek bir etken değişiyor.

## 11. Makale neler raporluyor?

Bunlar makalede raporlanan sayılar (her yerde böyle etiketli).

## 12. Yeniden üretimimiz ve makale (sentetik görüntüler)

FCM uyumu görüntüleri ve gürültüyü doğruluyor. Yöntem düşük gürültüde tutuyor; üç sınıflı görüntülerde yüksek gürültüde daha düşük — sonraki slaytlarda açıklanıyor.

## 13. Ablasyon ve duyarlılık

Ödül katsayısı σ yüksek gürültüde en etkili parametre. Bunu akılda tutun — ikinci iterasyonu yönlendiren bu.

## 14. α, β, γ için Mamdani kural tabanı

Çıkarım örneğini adım adım anlatın: hangi kurallar ateşleniyor, çıkış kümesi nasıl oluşuyor, üç durulaştırma sonucu.

## 15. Sonuç: ilk kural tabanı doğruluğu artırmadı (H1 reddedildi)

Olumsuz sonuç dürüstçe raporlandı — yönerge iyileşmeyi zorunlu tutmuyor ama analiz edilmesini istiyor. Sonraki slayt analizi gösteriyor.

## 16. Neden başarısız oldu — varyantlar ne gösteriyor?

Bu teşhis ikinci iterasyona köprü: her aday bu nedenlerden birini hedefliyor.

## 17. İkinci iterasyon: bulanık ödül katsayısı (önceden kayıtlı)

Protokolü anlatın: ayar kümesi test kümesinden ayrı, deneme bütçesi, ön kayıt. Fikrin test tohumlarındaki C2 ablasyonundan geldiğini açıkça söyleyin — test parametrelere kör, fikre değil.

## 18. Sonuç: H5 tuttu, H6 tuttu

FIS-σ, %15'te sy2/sy3'te 97.00/95.08'e ulaşıyor (makalede raporlanan 98.53/97.36: daha yakın ama hâlâ altında; sonraki slayt). Dürüst kısım: karışık gürültüde sabit σ = 0.9 de aynı derecede iyi (farklar -0.02 … +0.19); kuralın değeri σ'yı otomatik seçmesi. FIS-σ+A, ilk kural tabanını zararsız ve düşük gürültüde daha iyi hâle getiriyor.

## 19. Test ızgarasının ötesi: gürültü türleri ve gerçek görüntüler

Kazancın gerçek görüntülere ve tüm gürültü türlerine taşındığını gösterin; sabit σ = 0.9'un nerede aynı derecede iyi olduğunu açıkça söyleyin.

## 20. Makalenin kendi sayılarına göre: daha yakın, ama daha iyi değil

İki karşılaştırmayı ayırın. Denetimli (aynı kod, aynı gürültü): FIS-σ %10–15'te makale ayarlarını geçiyor, hiçbir yerde anlamlı kaybı yok. Makalede basılı sayılara göre (başka uygulama, başka gürültü örnekleri; yalnızca yol gösterici): düşük gürültüde eşit, %15'te sy2/sy3'te hâlâ 1.53/2.28 puan aşağıda (önce 6.15/8.23). 'Makaleyi geçtik' demeyin.

## 21. Gerçek görüntüler: gri ve renkli BSDS500 (%5 karışık gürültü)

Renkli görüntüleri neden ayrıca çalıştırdığımızı anlatın: makaledeki BSDS500 görüntüleri renkli fotoğraflar; yöntemin çok kanallı bir sürümünü kullanıyoruz (D-043).

## 22. Katkının getirdikleri — ve sınırları

Neyin yapılıp neyin yapılmadığını açıkça söyleyin; yönerge yalnız doğruluğu değil analizi de değerlendiriyor.

## 23. Sonuç

Tek cümleyle özetleyin: σ'yı görüntüden seçen küçük bir kural sistemi yüksek gürültüde kaybedilen doğruluğun çoğunu geri kazandırıyor. Teşekkür edin ve soruları davet edin.