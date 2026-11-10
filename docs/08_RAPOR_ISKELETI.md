# 08 — Teknik Rapor İskeleti

Kural: **8–12 sayfa (kaynakça hariç)**, IEEE kaynakça formatı, aşağıdaki bölüm sırası (yönerge §8) + **Generative AI Usage Disclosure**. Dil: D-007 (öneri İngilizce). Şablon: IEEE konferans (2 sütun) veya tek sütun — hocadan teyit (D-019).

**Sayfa bütçesi (öneri, toplam ≈ 11 sf):**

| # | Bölüm | Sayfa | İçerik | Puan bağı |
|---|---|---|---|---|
| — | Başlık + Abstract + Anahtar kelimeler | 0.5 | 150–200 kelime; problem, yöntem, katkı, ana sonuç (bizim sayılar) | Akademik yapı |
| 1 | Introduction | 1 | Problem (gürültülü görüntü segmentasyonu), motivasyon, FCM'nin sınırı, amaç, kapsam, katkılarımız | Akademik yapı |
| 2 | Related Work | 1.25 | Karşılaştırmalı: BCFCM→FGFCM→FLICM→FRFCM→SRFCM→FCM_SICM→FSC_LNML vb.; güncel (2022+) çalışmalar; tablo (yöntem × bilgi türü × adaptif × sparse × süre) | Literatür (3) |
| 3 | Theoretical Background | 1 | Fuzzy sets, membership, FCM (Eq.1–3), Lagrange türetimi, ℓ0/hard threshold, DTCWT, (kısa) Mamdani/Sugeno ile FCM'nin konumu, defuzzification (argmax) | Yöntem açıklaması (3) |
| 4 | Original Method | 1.25 | Makale yöntemi: Alg.2, non-local DTCWT, adaptif α,β,γ, sparse FCM (Eq.5–29), akış şeması (kendi çizimimiz) | Yöntem açıklaması |
| 5 | Reproduction Methodology | 1 | Nasıl uyguladık: modüller, varsayımlar, **makaleden sapmalar (D-011…D-014)**, test stratejisi, sy görüntüleri/gürültü tanımı | Tekrar üretilebilirlik |
| 6 | Proposed Extension | 1 | Katkı (C1+C2…): gerekçe, hipotez, tasarım, başarı ölçütü | Katkı (4+8) |
| 7 | Experimental Setup | 0.75 | Veri, ortam, kütüphaneler+sürümler, donanım, parametreler, seed, metrikler | Deney tasarımı |
| 8 | Results | 1.5 | Reproduction vs makale tabloları; baseline vs katkı tablosu (§6.2 biçimi); ablasyon; duyarlılık; gerçek görüntü; süre; figürler | Raporlama (3), Analiz (5) |
| 9 | Discussion | 0.75 | Neden bu sonuçlar? Makale ile farkın nedenleri; başarısızlık örnekleri | Tartışma (3) |
| 10 | Limitations | 0.4 | K önceden verilir, maliyet, sentetik/gerçek açık, tek makale protokolü, kendi sınırlarımız | Tartışma |
| 11 | Conclusion | 0.4 | Özet + gelecek çalışma | Akademik yapı |
| — | **Generative AI Usage Disclosure** | 0.2 | `docs/genai_usage_log.md`'den | Etik/şeffaflık |
| — | References (IEEE) | (ek) | Doğrulanmış kaynaklar | Literatür (3) |

## Şekil/tablo planı (hepsi betikle üretilir)

- Fig.1 Sistem mimarisi / akış şeması (kendi çizimimiz)
- Fig.2 Ödül/ceza kümesi örneği (kendi 3×3 örneğimiz)
- Fig.3 Sentetik görüntüler + gürültülü hâlleri
- Fig.4 Segmentasyon karşılaştırma paneli (sy, BSDS)
- Fig.5 Yakınsama eğrileri (FCM vs ASRFCM)
- Fig.6 Duyarlılık eğrileri (σ, k, δ, w)
- Fig.7 Robustness (gürültü türü × yoğunluk → ACC/Kappa)
- Tab.1 Literatür karşılaştırması · Tab.2 Reproduction vs makale · Tab.3 Ablasyon · Tab.4 Baseline vs geliştirilen (Metrik|Baseline|Geliştirilen|Değişim) · Tab.5 Gerçek görüntüler · Tab.6 Süre

## Yazım kontrol listesi

- [ ] Her denklem numaralı ve metinde açıklanmış; notasyon tutarlı (makale sembolleri)
- [ ] Her figür/tablo metinde atıflı; başlık + birim + "makale/bizim" etiketi
- [ ] Her atıf DOI ile doğrulanmış; IEEE biçimi
- [ ] Makale sonuçları "reported in [1]" ile; bizim sonuçlar kendi çalıştırmamız
- [ ] Başarısız/negatif sonuçlar saklanmadan raporlandı
- [ ] GenAI Disclosure gerçeği yansıtıyor (log ile uyumlu)
- [ ] Sayfa sayısı 8–12 (kaynakça hariç)
- [ ] PDF açılıyor, fontlar/figürler sağlam

## GenAI Disclosure şablonu (log'a göre doldur)

> *Generative AI Usage Disclosure.* During this project, Claude (Anthropic) was used as an assistant for: [code development and debugging / explaining fuzzy-logic and signal-processing concepts / literature search assistance / language editing / drafting project documentation — keep only what is true]. All generated code, algorithms, experiments, figures, tables and explanations were reviewed, tested and verified by the author. All references were manually verified (DOI checked) and no unverified or non-existent sources were used. All reported results were produced by running the code in the accompanying repository.
