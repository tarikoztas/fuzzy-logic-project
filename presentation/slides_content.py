"""Slide specification (15-20 min talk) in English and Turkish. Numbers come from
report/report_values.py (CSV-based), so both languages show identical values.

Guideline Sec. 4 coverage: introduction, paper and project overview, outline (2-5), problem & motivation (6), literature (7), fuzzy-logic background (8),
method & architecture incl. inputs/outputs, membership functions, rules, inference, defuzzification
(5-9), experiments & data (10), paper's results (11), discussion (22), our implementation
and contribution with comparative results (12-13, 14-21), conclusion (23).
"""
from __future__ import annotations

import pandas as pd

from report.report_values import compute

T = "results/tables/"


def _e5_rows():
    d = pd.read_csv(T + "e5_main_runs.csv")
    w = pd.read_csv(T + "e5_main_wilcoxon.csv")
    rows = []
    for img in ("sy2", "sy3"):
        for p in (5, 15):
            g = d[(d.image == img) & (d.noise_pct == p)].groupby("method").ACC.mean()
            ws = {m: w[(w.image == img) & (w.noise_pct == p) & (w.method == m)].iloc[0] for m in ("FIS-full", "FIS-split")}
            rows.append([f"{img} {p}%", f"{g['FCM']:.1f}", f"{g['ASRFCM-paper']:.2f}",
                         f"{g['FIS-full']:.2f} ({ws['FIS-full'].mean_diff:+.1f}{'*' if ws['FIS-full']['significant_0.05'] else ''})",
                         f"{g['FIS-split']:.2f} ({ws['FIS-split'].mean_diff:+.1f}{'*' if ws['FIS-split']['significant_0.05'] else ''})"])
    return rows


def _e2_rows():
    e1 = pd.read_csv(T + "e1_fcm_vs_paper.csv").query("metric == 'ACC'").set_index(["image", "noise_pct"])
    e2 = pd.read_csv(T + "e2_asrfcm_vs_paper.csv").query("metric == 'ACC'").set_index(["image", "noise_pct"])
    rows = []
    for img in ("sy1", "sy2", "sy3"):
        for p in (5, 15):
            rows.append([f"{img} {p}%", f"{e1.loc[(img, p), 'ours_mean']:.1f} / {e1.loc[(img, p), 'paper_reported']:.1f}",
                         f"{e2.loc[(img, p), 'ours_mean']:.2f} / {e2.loc[(img, p), 'paper_reported']:.2f}"])
    return rows


def _e8_rows():
    d = pd.read_csv(T + "e8_second_iteration_runs.csv")
    w = pd.read_csv(T + "e8_second_iteration_wilcoxon.csv")
    rows = []
    for img in ("sy2", "sy3"):
        for p in (5, 10, 15):
            g = d[(d.image == img) & (d.noise_pct == p)].groupby("method").ACC.mean()
            cell = []
            for m in ("FIS-sigma", "FIS-sigma+A"):
                ww = w[(w.image == img) & (w.noise_pct == p) & (w.method == m)].iloc[0]
                cell.append(f"{g[m]:.2f} ({ww.mean_diff:+.1f}{'*' if ww['significant_0.05'] else ''})")
            rows.append([f"{img} {p}%", f"{g['ASRFCM-paper']:.2f}", f"{g['sigma=0.9 (fixed)']:.2f}", *cell])
    return rows


def _e8_reported_rows():
    """FIS-σ against the values printed in [1] (indicative: other implementation and noise realizations)."""
    d = pd.read_csv(T + "e8_second_iteration_runs.csv")
    pr = pd.read_csv(T + "e2_asrfcm_vs_paper.csv").query("metric == 'ACC'").set_index(["image", "noise_pct"]).paper_reported
    rows = []
    for img in ("sy2", "sy3"):
        for p in (5, 10, 15):
            g = d[(d.image == img) & (d.noise_pct == p)].groupby("method").ACC.mean()
            r = pr[(img, p)]
            rows.append([f"{img} {p}%", f"{r:.2f}", f"{g['ASRFCM-paper']:.2f} ({g['ASRFCM-paper'] - r:+.2f})",
                         f"{g['FIS-sigma']:.2f} ({g['FIS-sigma'] - r:+.2f})"])
    return rows


def slides(lang: str = "en") -> list[dict]:
    V, _ = compute(lang)
    L = (lambda en, tr: tr) if lang == "tr" else (lambda en, tr: en)
    sfx = "_tr" if lang == "tr" else ""   # figures with a Turkish variant
    return [
        {"kind": "title",
         "kicker": L("Fuzzy Logic · Term Project", "Bulanık Mantık · Dönem Projesi"),
         "title": L("Adaptive Sparse-Regularized Fuzzy Clustering for Noisy Image Segmentation",
                    "Gürültülü Görüntü Bölütleme için Uyarlamalı Seyrek Düzenlileştirilmiş Bulanık Kümeleme"),
         "subtitle": L("Tarık Öztaş\nStudent ID: 1306230040\nİstanbul University-Cerrahpaşa, Computer Engineering\nReference paper: Wu et al., Expert Systems with Applications 256 (2024) 124943",
                       "Tarık Öztaş\nÖğrenci No: 1306230040\nİstanbul Üniversitesi-Cerrahpaşa, Bilgisayar Mühendisliği\nReferans makale: Wu vd., Expert Systems with Applications 256 (2024) 124943"),
         "notes": L("Introduce yourself and the paper. Say what you will show: re-implementation, reproduction, two iterations of a fuzzy-rule extension, and an honest evaluation.",
                    "Kendinizi ve makaleyi tanıtın. Neleri göstereceğinizi söyleyin: yeniden gerçekleştirme, yeniden üretim, bulanık kural tabanlı geliştirmenin iki iterasyonu ve dürüst bir değerlendirme.")},
        {"section": L("Introduction", "Giriş"), "title": L("Image segmentation: what it is and why it matters", "Görüntü bölütleme: nedir, neden önemlidir?"),
         "lead": L("Segmentation divides an image into regions that belong together, such as tissue types in an MRI scan or land-cover classes in a satellite image. It is often the first step before anything is measured or recognised.",
                   "Bölütleme, bir görüntüyü birbirine ait bölgelere ayırır: bir MR görüntüsündeki doku türleri ya da bir uydu görüntüsündeki arazi sınıfları gibi. Çoğu zaman bir şey ölçülmeden ya da tanınmadan önceki ilk adımdır."),
         "bullets": [L("Every pixel gets a class label → regions, boundaries and areas can be measured", "Her piksel bir sınıf etiketi alır → bölgeler, sınırlar ve alanlar ölçülebilir"),
                     L("Uses: medical imaging, remote sensing, industrial inspection", "Kullanım alanları: tıbbi görüntüleme, uzaktan algılama, endüstriyel denetim"),
                     L("Real images are noisy: sensor noise, faulty pixels (salt-and-pepper), speckle in ultrasound and radar", "Gerçek görüntüler gürültülüdür: algılayıcı gürültüsü, hatalı pikseller (tuz-biber), ultrason ve radarda benek gürültüsü"),
                     L("A good method keeps the regions intact even when many single pixels are wrong", "İyi bir yöntem, tek tek birçok piksel hatalı olsa bile bölgeleri bütün tutar")],
         "image": f"results/figures/intro_segmentation{sfx}.png",
         "caption": L("Our runs, seed 0: the noisy image, plain FCM, the reference method and the correct segmentation", "Bizim koşularımız, tohum 0: gürültülü görüntü, düz FCM, referans yöntem ve doğru bölütleme"),
         "notes": L("Start from the everyday meaning: colouring an image by regions. Point at the figure: plain FCM is confused by the noise, the reference method recovers the regions. This is the problem the whole talk is about.",
                    "Gündelik anlamdan başlayın: görüntüyü bölgelere göre boyamak. Şekli gösterin: düz FCM gürültüden şaşırıyor, referans yöntem bölgeleri geri kazanıyor. Sunumun tamamı bu problemle ilgili.")},
        {"section": L("Introduction", "Giriş"), "title": L("The reference paper at a glance", "Referans makaleye genel bakış"),
         "lead": L("Wu, Wang, Liu and Fang (Expert Systems with Applications, 2024) propose a fuzzy clustering method that stays accurate when an image contains several kinds of noise at the same time.",
                   "Wu, Wang, Liu ve Fang (Expert Systems with Applications, 2024), bir görüntüde aynı anda birkaç gürültü türü olduğunda da doğru kalan bir bulanık kümeleme yöntemi öneriyor."),
         "bullets": [L("Problem: FCM and its spatial variants degrade under mixed Gaussian, salt-and-pepper and speckle noise", "Problem: FCM ve uzamsal türevleri karışık Gauss, tuz-biber ve benek gürültüsü altında bozuluyor"),
                     L("Idea: describe every pixel by its own value and two denoised estimates — one from its neighbours, one from similar patches in the wavelet domain", "Fikir: her pikseli kendi değeri ve iki gürültüsüz kestirimle tanımlamak — biri komşularından, biri dalgacık alanındaki benzer yamalardan"),
                     L("Adaptive weights decide, pixel by pixel, how much each of the three views is trusted", "Uyarlamalı ağırlıklar, üç görüşün her birine ne kadar güvenileceğine piksel piksel karar veriyor"),
                     L("A sparsity term keeps only clear memberships and reduces the number of iterations", "Seyreklik terimi yalnızca belirgin üyelikleri bırakıyor ve iterasyon sayısını azaltıyor"),
                     L("Evaluated on synthetic images and on natural BSDS500 photographs against eight other methods", "Sentetik görüntülerde ve doğal BSDS500 fotoğraflarında sekiz başka yöntemle karşılaştırılıyor")],
         "callouts": [("ESWA 256 (2024)", L("article 124943, doi 10.1016/j.eswa.2024.124943", "makale 124943, doi 10.1016/j.eswa.2024.124943")),
                      (L("Why this paper?", "Neden bu makale?"), L("recent, fuzzy at its core, and evaluated on public data", "güncel, özünde bulanık ve açık veriyle değerlendirilmiş"))],
         "notes": L("Name the authors and the journal. Explain the idea in one sentence: do not trust a single noisy pixel, combine it with two cleaner estimates and decide per pixel how much to trust each. Details follow in the method section.",
                    "Yazarları ve dergiyi söyleyin. Fikri tek cümleyle anlatın: tek bir gürültülü piksele güvenme; onu iki daha temiz kestirimle birleştir ve her piksel için hangisine ne kadar güvenileceğine karar ver. Ayrıntılar yöntem bölümünde.")},
        {"section": L("Introduction", "Giriş"), "title": L("This project: what we did and why it is useful", "Bu proje: ne yaptık, ne işe yarıyor?"),
         "lead": L("The project has two parts: rebuilding the paper's method from its description and checking its results, and then extending it with explicit fuzzy rule bases.",
                   "Proje iki bölümden oluşuyor: makalenin yöntemini açıklamasından yola çıkarak yeniden kurmak ve sonuçlarını sınamak, ardından açık bulanık kural tabanlarıyla geliştirmek."),
         "bullets": [L(f"Re-implementation in Python from the paper alone — no author code — with {V['n_tests']} unit tests", f"Yalnızca makaleden, Python ile yeniden gerçekleştirme — yazarların kodu kullanılmadı — {V['n_tests']} birim testi"),
                     L("Reproduction: the paper's images, noise levels and metrics; 10 seeds per setting", "Yeniden üretim: makalenin görüntüleri, gürültü düzeyleri ve ölçütleri; her ayar için 10 tohum"),
                     L("Extension: Mamdani rule bases — iteration 1 for the per-pixel trust α, β, γ; iteration 2 for the reward factor σ", "Geliştirme: Mamdani kural tabanları — iterasyon 1 piksel başına güven α, β, γ için; iterasyon 2 ödül katsayısı σ için"),
                     L("Honest evaluation: hypotheses fixed in advance, paired statistical tests, negative results and limits reported", "Dürüst değerlendirme: önceden belirlenen hipotezler, eşleştirilmiş istatistik testleri, olumsuz sonuçlar ve sınırlar raporlandı")],
         "callouts": [(L("Open code", "Açık kod"), L("a public implementation others can check and reuse", "başkalarının kontrol edip kullanabileceği açık bir uygulama")),
                      (L("Readable rules", "Okunur kurallar"), L("the weighting is explained by IF–THEN rules instead of a formula", "ağırlıklandırma bir formül yerine EĞER–İSE kurallarıyla açıklanıyor")),
                      (L("Automatic σ", "Otomatik σ"), L("the noise level of the image sets σ — no manual tuning", "σ'yı görüntünün gürültü düzeyi belirliyor — elle ayar yok"))],
         "notes": L("Say what the listener gains: a checked implementation, interpretable rules and an automatic parameter choice. Mention that the guideline does not require an improvement, but our second iteration did improve the method under identical conditions.",
                    "Dinleyicinin ne kazandığını söyleyin: sınanmış bir uygulama, yorumlanabilir kurallar ve otomatik parametre seçimi. Yönergenin iyileşmeyi zorunlu tutmadığını, ama ikinci iterasyonumuzun yöntemi aynı koşullarda iyileştirdiğini belirtin.")},
        {"section": L("Introduction", "Giriş"), "title": L("Outline of the talk", "Sunumun akışı"),
         "lead": L("The talk follows the order of the work: first the problem and the method, then whether we could reproduce it, and finally what our fuzzy extension adds.",
                   "Sunum, çalışmanın sırasını izliyor: önce problem ve yöntem, sonra yöntemi yeniden üretip üretemediğimiz, en son da bulanık geliştirmemizin ne kattığı."),
         "bullets": [L("**Background** — why noise is hard for FCM, related work, fuzzy sets and inference", "**Altyapı** — gürültü FCM için neden zor, ilgili çalışmalar, bulanık kümeler ve çıkarım"),
                     L("**The method** — architecture, local and non-local information, adaptive weights, sparsity", "**Yöntem** — mimari, yerel ve yerel-olmayan bilgi, uyarlamalı ağırlıklar, seyreklik"),
                     L("**Reproduction** — data and protocol, the paper's results and ours", "**Yeniden üretim** — veri ve protokol, makalenin ve bizim sonuçlarımız"),
                     L("**Our extension** — iteration 1 (α, β, γ), why it failed, iteration 2 (σ) and its results", "**Geliştirmemiz** — iterasyon 1 (α, β, γ), neden başarısız oldu, iterasyon 2 (σ) ve sonuçları"),
                     L("**Discussion and conclusion**", "**Tartışma ve sonuç**")],
         "notes": L("Keep this short (20 seconds).", "Kısa tutun (20 saniye).")},
        {"section": L("Problem", "Problem"), "title": L("Why noisy images are hard for plain fuzzy clustering", "Gürültülü görüntüler düz bulanık kümeleme için neden zor?"),
         "lead": L("Fuzzy C-means (FCM) groups pixels by brightness. It looks at each pixel on its own, so when noise changes a pixel's brightness, the pixel lands in the wrong group.",
                   "Bulanık C-ortalamalar (FCM) pikselleri parlaklıklarına göre gruplar. Her piksele tek başına baktığı için gürültü bir pikselin parlaklığını değiştirince piksel yanlış gruba düşer."),
         "bullets": [L("“Fuzzy”: a pixel can belong partly to several groups, e.g. 70 % dark and 30 % bright", "“Bulanık”: bir piksel birkaç gruba kısmen ait olabilir, ör. %70 koyu, %30 açık"),
                     L("FCM ignores the neighbours of a pixel → noise produces scattered wrong dots", "FCM pikselin komşularına bakmaz → gürültü dağınık yanlış noktalar üretir"),
                     L("Example from our runs: FCM labels only about 56 % of the pixels correctly at 15 % noise", "Bizim koşulardan örnek: %15 gürültüde FCM piksellerin yalnızca yaklaşık %56'sını doğru etiketliyor"),
                     L("Goal of the paper: stay accurate when several kinds of noise are mixed", "Makalenin amacı: birkaç gürültü türü karıştığında da doğru kalmak")],
         "image": "results/figures/panel_synthetic.png", "caption": L("Three test images with 10 % mixed noise: FCM and the method (our runs)", "%10 karışık gürültülü üç test görüntüsü: FCM ve yöntem (bizim koşular)"),
         "notes": L("Show the noisy images and how FCM fails. If asked: FCM minimises Σ u^m (y − c)² with Σ_i u = 1; the mixed noise is Gaussian + speckle + salt-and-pepper (sy3, 15 %: ACC ≈ 56 %).",
                    "Gürültülü görüntüleri ve FCM'nin nasıl başarısız olduğunu gösterin. Sorulursa: FCM, Σ_i u = 1 koşuluyla Σ u^m (y − c)² değerini en küçükler; karışık gürültü Gauss + benek + tuz-biberdir (sy3, %15: ACC ≈ %56).")},
        {"section": L("Literature", "Literatür"), "title": L("How earlier work helps FCM against noise", "Önceki çalışmalar FCM'ye gürültüye karşı nasıl yardım ediyor?"),
         "lead": L("The common idea: a pixel's neighbours tell us what the pixel probably should be. The methods differ in which neighbours they use and how.",
                   "Ortak fikir: bir pikselin komşuları, o pikselin aslında ne olması gerektiğini söyler. Yöntemler hangi komşuları nasıl kullandıklarına göre ayrılır."),
         "table": {"columns": [L("Approach", "Yaklaşım"), L("What it does", "Ne yapar"), L("Weak point", "Zayıf noktası")],
                   "rows": [[L("Local", "Yerel"), L("averages the nearby pixels", "yakındaki pikselleri ortalar"), L("fails when many neighbours are noisy", "komşuların çoğu gürültülüyse başarısız")],
                            [L("Non-local", "Yerel-olmayan"), L("uses similar patches anywhere in the image", "görüntünün her yerindeki benzer yamaları kullanır"), L("can carry the noise along", "gürültüyü de taşıyabilir")],
                            [L("Wavelet + sparse", "Dalgacık + seyrek"), L("cleans the image in a transformed form", "görüntüyü dönüştürülmüş hâlinde temizler"), L("no adaptive weighting", "uyarlamalı ağırlık yok")],
                            [L("This paper [1]", "Bu makale [1]"), L("combines all of them with adaptive weights", "hepsini uyarlamalı ağırlıklarla birleştirir"), L("slower to compute", "hesaplaması daha yavaş")]],
                   "caption": L("33 references, all checked on Crossref", "33 kaynak, hepsi Crossref üzerinden kontrol edildi")},
         "notes": L("If asked for names: local — BCFCM, FCM_S, FGFCM, FLICM, FRFCM; non-local — FCM_SNLS, FALRCM, FSC_LNML; wavelet/sparse — WFCM, SRFCM, DSFCM_N.",
                    "İsim sorulursa: yerel — BCFCM, FCM_S, FGFCM, FLICM, FRFCM; yerel-olmayan — FCM_SNLS, FALRCM, FSC_LNML; dalgacık/seyrek — WFCM, SRFCM, DSFCM_N.")},
        {"section": L("Fuzzy-logic background", "Bulanık mantık altyapısı"), "title": L("Fuzzy logic in three ideas", "Üç fikirde bulanık mantık"),
         "lead": L("Fuzzy logic lets a statement be partly true. That is useful when the boundary between categories is not sharp, like “noisy” and “clean”.",
                   "Bulanık mantık bir ifadenin kısmen doğru olmasına izin verir. Kategoriler arasındaki sınır keskin olmadığında, ör. “gürültülü” ve “temiz” gibi, bu çok işe yarar."),
         "bullets": [L("**Fuzzy set**: “noise is high” is true to a degree between 0 and 1", "**Bulanık küme**: “gürültü yüksek” ifadesi 0 ile 1 arasında bir dereceyle doğrudur"),
                     L("**Fuzzy clustering**: every pixel belongs to every group with a degree", "**Bulanık kümeleme**: her piksel her gruba bir dereceyle aittir"),
                     L("**Fuzzy rules (Mamdani)**: “IF noise is high THEN smooth strongly” — rules fire partly, their answers are combined", "**Bulanık kurallar (Mamdani)**: “EĞER gürültü yüksekse O HÂLDE güçlü yumuşat” — kurallar kısmen ateşlenir, cevapları birleştirilir"),
                     L("The combined answer is turned into one number (defuzzification)", "Birleşik cevap tek bir sayıya çevrilir (durulaştırma)")],
         "image": f"results/figures/fis_membership{sfx}.png", "caption": L("membership functions of our first rule base", "ilk kural tabanımızın üyelik fonksiyonları"),
         "notes": L("Connect to the lectures. If asked: AND = min, implication = min (clipping), aggregation = max; defuzzification by centroid, bisector or mean of maxima; Sugeno uses constant outputs and a weighted average.",
                    "Derslerle bağ kurun. Sorulursa: VE = min, çıkarım = min (kırpma), birleştirme = max; durulaştırma ağırlık merkezi, açıortay ya da maksimumların ortalamasıyla; Sugeno sabit çıktılar ve ağırlıklı ortalama kullanır.")},
        {"section": L("Reference method", "Referans yöntem"), "title": L("How the method works", "Yöntem nasıl çalışıyor?"),
         "lead": L("Instead of trusting a single noisy pixel, the method asks two “second opinions” and decides for each pixel how much to trust each of the three.",
                   "Yöntem tek bir gürültülü piksele güvenmek yerine iki “ikinci görüş” alır ve her piksel için üçünden hangisine ne kadar güveneceğine karar verir."),
         "bullets": [L("Input: the noisy image and the number of regions", "Girdi: gürültülü görüntü ve bölge sayısı"),
                     L("Opinion 1: a cleaned value from the pixel's neighbours", "1. görüş: pikselin komşularından elde edilen temizlenmiş değer"),
                     L("Opinion 2: a cleaned value from similar patches, computed after a wavelet transform", "2. görüş: dalgacık dönüşümünden sonra benzer yamalardan elde edilen temizlenmiş değer"),
                     L("Weights per pixel → fuzzy clustering → one region label per pixel", "Piksel başına ağırlıklar → bulanık kümeleme → her piksele bir bölge etiketi")],
         "image": f"results/figures/architecture_simple{sfx}.png", "narrow_text": True,
         "notes": L("Walk through the figure left to right. Orange box = our first iteration (the weights); the second iteration changes σ inside the first opinion. "
                    "If asked: distance d = α(y−c)² + β(ξ−c)² + γ(ϑ−c)², ξ = local, ϑ = non-local estimate.",
                    "Şekli soldan sağa anlatın. Turuncu kutu = ilk iterasyonumuz (ağırlıklar); ikinci iterasyon 1. görüşün içindeki σ'yı değiştiriyor. "
                    "Sorulursa: uzaklık d = α(y−c)² + β(ξ−c)² + γ(ϑ−c)², ξ = yerel, ϑ = yerel-olmayan kestirim.")},
        {"section": L("Reference method", "Referans yöntem"), "title": L("Opinion 1: a fair vote of the neighbours", "1. görüş: komşuların adil oylaması"),
         "lead": L("Like a jury that gives less weight to the most extreme scores, the method trusts neighbours with typical values more and extreme values less.",
                   "En uç puanlara daha az ağırlık veren bir jüri gibi, yöntem tipik değerli komşulara daha çok, uç değerli komşulara daha az güvenir."),
         "bullets": [L("Look at the 5×5 neighbourhood and sort the values", "5×5 komşuluğa bak ve değerleri sırala"),
                     L("The middle part (golden ratio, about 62 %) is **rewarded**, the extremes are **penalised**", "Ortadaki kısım (altın oran, yaklaşık %62) **ödüllendirilir**, uçlar **cezalandırılır**"),
                     L("Closer and more similar neighbours count more; the result is a weighted average", "Daha yakın ve daha benzer komşular daha çok sayılır; sonuç ağırlıklı bir ortalamadır"),
                     L("**σ** sets how strongly the extremes are pushed down — the key knob of our second iteration", "**σ**, uçların ne kadar bastırılacağını belirler — ikinci iterasyonumuzun anahtar ayarı")],
         "callouts": [("σ = 0.3", L("paper's value", "makalenin değeri")), ("σ = 0.9", L("better at high noise in our tests", "testlerimizde yüksek gürültüde daha iyi"), "warn")],
         "notes": L("If asked: reward weight 1+σ, penalty weight 1−σ, times exp(−Δgray²/τ²)·exp(−distance); reward-set size ⌊0.618·(N_R−1)⌋; Fig. 1 of the paper is reproduced exactly (D-014).",
                    "Sorulursa: ödül ağırlığı 1+σ, ceza ağırlığı 1−σ, bunlar exp(−Δgri²/τ²)·exp(−uzaklık) ile çarpılır; ödül kümesi boyutu ⌊0.618·(N_R−1)⌋; makalenin Şekil 1'i birebir yeniden üretildi (D-014).")},
        {"section": L("Reference method", "Referans yöntem"), "title": L("Opinion 2: cleaning in the wavelet domain", "2. görüş: dalgacık alanında temizleme"),
         "lead": L("A wavelet transform splits the image into a coarse picture and fine details in six directions — like splitting a song into bass, middle and treble.",
                   "Dalgacık dönüşümü görüntüyü kaba bir resme ve altı yöndeki ince ayrıntılara ayırır — bir şarkıyı bas, orta ve tiz seslere ayırmak gibi."),
         "bullets": [L("In each part, every value is replaced by an average over similar patches", "Her parçada her değer, benzer yamalar üzerinden alınan bir ortalamayla değiştirilir"),
                     L("The parts are put back together into a cleaned image", "Parçalar yeniden birleştirilerek temizlenmiş bir görüntü elde edilir"),
                     L("Effect: flat regions become smooth, edges are kept by the direction parts", "Etkisi: düz bölgeler yumuşar, kenarları yön parçaları korur")],
         "notes": L("If asked: dual-tree complex wavelet transform (DTCWT), 1 low-pass + 6 sub-bands at ±15°, ±45°, ±75°; non-local means with a 15×15 search window and 5×5 patches, h² = 250.",
                    "Sorulursa: çift ağaçlı karmaşık dalgacık dönüşümü (DTCWT), 1 alçak geçiren + ±15°, ±45°, ±75°'de 6 alt bant; 15×15 arama penceresi ve 5×5 yamalarla yerel-olmayan ortalama, h² = 250.")},
        {"section": L("Reference method", "Referans yöntem"), "title": L("Weighing the three opinions", "Üç görüşü tartmak"),
         "lead": L("For every pixel the method computes three trust weights: for the pixel itself and for the two cleaned opinions. Then it clusters.",
                   "Yöntem her piksel için üç güven ağırlığı hesaplar: pikselin kendisi ve iki temizlenmiş görüş için. Ardından kümeleme yapar."),
         "bullets": [L("The paper's formula gives the noisy pixel itself almost no trust (about 0.1 %)", "Makalenin formülü gürültülü pikselin kendisine neredeyse hiç güvenmiyor (yaklaşık %0.1)"),
                     L("A sparsity step keeps only clear memberships, so each pixel ends up in one region", "Seyreklik adımı yalnızca belirgin üyelikleri bırakıyor; böylece her piksel tek bir bölgeye düşüyor"),
                     L("This also reduces the number of iterations", "Bu, iterasyon sayısını da azaltıyor"),
                     L("All parameters are taken from the paper (e.g. 5×5 window, σ = 0.3)", "Tüm parametreler makaleden alındı (ör. 5×5 pencere, σ = 0.3)")],
         "notes": L("If asked: ΔG1 = k·exp(y − ξ), ΔG2 = k·exp(y − ϑ); α = 1/(ΔG1+ΔG2), β = ΔG1, γ = ΔG2 with k = 15; objective Σ u^m d + δ‖U‖₀, hard threshold √δ = 0.63 then normalise; w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4, m=2.",
                    "Sorulursa: ΔG1 = k·exp(y − ξ), ΔG2 = k·exp(y − ϑ); α = 1/(ΔG1+ΔG2), β = ΔG1, γ = ΔG2, k = 15; amaç Σ u^m d + δ‖U‖₀, sert eşik √δ = 0.63, ardından normalize; w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4, m=2.")},
        {"section": L("Fuzzy system", "Bulanık sistem"), "title": L("The fuzzy systems of the project at a glance", "Projedeki bulanık sistemler bir bakışta"),
         "lead": L("The paper is fuzzy through its clustering, but it has no rules. Our two iterations add small rule systems at two different places.",
                   "Makale kümelemesi sayesinde bulanıktır ama kuralı yoktur. İki iterasyonumuz iki farklı yere küçük kural sistemleri ekliyor."),
         "table": {"columns": [L("Element", "Öğe"), L("Paper", "Makale"), L("Our iteration 1", "İterasyon 1 (bizim)"), L("Our iteration 2", "İterasyon 2 (bizim)")],
                   "rows": [[L("Inputs", "Girdiler"), L("pixel + two opinions", "piksel + iki görüş"), L("pixel vs. opinions; disagreement", "piksel–görüş farkı; anlaşmazlık"), L("noise level of the image", "görüntünün gürültü düzeyi")],
                            [L("Fuzzy sets", "Bulanık kümeler"), L("membership to regions", "bölgelere üyelik"), L("Small / Medium / Large", "Küçük / Orta / Büyük"), L("Low / Medium / High", "Düşük / Orta / Yüksek")],
                            [L("Rules", "Kurallar"), L("none (a formula)", "yok (formül)"), L("9 IF–THEN rules", "9 EĞER–İSE kuralı"), L("3 IF–THEN rules", "3 EĞER–İSE kuralı")],
                            [L("Inference", "Çıkarım"), L("repeated updates", "tekrarlanan güncellemeler"), "Mamdani (min / max)", "Mamdani (min / max)"],
                            [L("Defuzzification", "Durulaştırma"), L("strongest membership", "en güçlü üyelik"), L("centre of gravity (+ variants)", "ağırlık merkezi (+ türevleri)"), L("centre of gravity", "ağırlık merkezi")],
                            [L("Output", "Çıktı"), L("region label per pixel", "piksel başına bölge etiketi"), L("3 trust weights per pixel", "piksel başına 3 güven ağırlığı"), L("σ for the whole image", "tüm görüntü için σ")]]},
         "notes": L("This slide answers the guideline items: inputs/outputs, membership functions, rule base, inference, defuzzification — for the paper and for both iterations.",
                    "Bu slayt yönergenin istediği öğeleri karşılıyor: girdi/çıktı, üyelik fonksiyonları, kural tabanı, çıkarım, durulaştırma — makale ve iki iterasyon için.")},
        {"section": L("Experiments", "Deneyler"), "title": L("How we tested", "Nasıl test ettik?"),
         "lead": L("All methods see exactly the same noisy images and start from the same point, so any difference comes from the methods themselves.",
                   "Tüm yöntemler birebir aynı gürültülü görüntüleri görür ve aynı noktadan başlar; böylece her fark yöntemlerin kendisinden gelir."),
         "bullets": [L("Images: 3 synthetic test images from the paper and 8 natural photographs (BSDS500)", "Görüntüler: makaleden 3 sentetik test görüntüsü ve 8 doğal fotoğraf (BSDS500)"),
                     L("Noise: three kinds mixed, at 1, 5, 10 and 15 %", "Gürültü: üç tür karışık, %1, 5, 10 ve 15 düzeyinde"),
                     L("Every setting repeated 10 times with different random noise", "Her ayar farklı rastgele gürültüyle 10 kez tekrarlandı"),
                     L("Main measure: accuracy = share of correctly labelled pixels; a statistical test checks that differences are not luck", "Ana ölçüt: doğruluk = doğru etiketlenen piksellerin oranı; istatistik testi farkların şans olmadığını kontrol ediyor")],
         "notes": L(f"If asked: mixed noise p % = Gaussian(var p) → speckle(var p) → salt-and-pepper(p); metrics V_PC, V_PE, ACC, F, NMI, Kappa; Hungarian matching of labels; paired Wilcoxon tests; {V['n_tests']} unit tests.",
                    f"Sorulursa: karışık gürültü %p = Gauss(varyans p) → benek(varyans p) → tuz-biber(p); ölçütler V_PC, V_PE, ACC, F, NMI, Kappa; etiketlerin Macar yöntemiyle eşlenmesi; eşleştirilmiş Wilcoxon testleri; {V['n_tests']} birim testi.")},
        {"section": L("Paper's results", "Makalenin sonuçları"), "title": L("What the paper reports", "Makale neler raporluyor?"),
         "lead": L("These are the paper's own numbers; they are the target of our reproduction.", "Bunlar makalenin kendi sayıları; yeniden üretimimizin hedefi bunlar."),
         "callouts": [("79.58 → 99.23", L("average accuracy (%) on the synthetic images: FCM → method", "sentetik görüntülerde ortalama doğruluk (%): FCM → yöntem")),
                      (f"{V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']}", L("average accuracy (%) on the natural photographs", "doğal fotoğraflarda ortalama doğruluk (%)"))],
         "bullets": [L("Each part of the method helps; all of them together work best", "Yöntemin her parçası katkı sağlıyor; hepsi birlikte en iyi sonucu veriyor"),
                     L("Fewer iterations than the other methods; best or close to best against 8 methods", "Diğer yöntemlerden daha az iterasyon; 8 yönteme karşı en iyi ya da en iyiye yakın")],
         "notes": L("These are paper-reported numbers (Tables 1–9), labelled as such everywhere.", "Bunlar makalede raporlanan sayılar (Tablo 1–9); her yerde böyle etiketli.")},
        {"section": L("Reproduction", "Yeniden üretim"), "title": L("Could we reproduce the paper?", "Makaleyi yeniden üretebildik mi?"),
         "lead": L("Mostly yes: plain FCM matches the paper, which confirms our images and noise. The method matches at low noise but is weaker at high noise.",
                   "Büyük ölçüde evet: düz FCM makaleyle uyuşuyor; bu, görüntülerimizi ve gürültüyü doğruluyor. Yöntem düşük gürültüde uyuşuyor, yüksek gürültüde daha zayıf."),
         "table": {"columns": [L("Setting", "Ayar"), L("FCM ours / paper", "FCM bizim / makale"), L("Method ours / paper", "Yöntem bizim / makale")], "rows": _e2_rows(),
                   "caption": L("accuracy (%), average of 10 runs vs the paper's number", "doğruluk (%), 10 koşunun ortalaması ve makaledeki sayı")},
         "image": "results/figures/e2_asrfcm_vs_paper_compact.png",
         "bullets": [L(f"FCM: on average {V['E1_acc_mad']} points from the paper", f"FCM: makaleden ortalama {V['E1_acc_mad']} puan uzakta"),
                     L(f"Method: {V['E2_acc_mad_low']} points up to 5 % noise, {V['E2_acc_mad_high']} points at 10–15 %", f"Yöntem: %5'e kadar {V['E2_acc_mad_low']} puan, %10–15'te {V['E2_acc_mad_high']} puan fark")],
         "notes": L("FCM agreement validates images and noise. The gap at high noise on the three-region images is explained on the next slide (the σ setting).",
                    "FCM uyumu görüntüleri ve gürültüyü doğruluyor. Üç bölgeli görüntülerdeki yüksek gürültü farkı sonraki slaytta açıklanıyor (σ ayarı).")},
        {"section": L("Reproduction", "Yeniden üretim"), "title": L("Which parts matter?", "Hangi parçalar önemli?"),
         "lead": L("We switched parts of the method off one at a time and changed one setting at a time to see what really drives the result.",
                   "Sonucu gerçekte neyin belirlediğini görmek için yöntemin parçalarını tek tek kapattık ve ayarları tek tek değiştirdik."),
         "bullets": [L(f"All parts together work best ({V['E3_full_acc']} % on the three test images)", f"Tüm parçalar birlikte en iyi sonucu veriyor (üç test görüntüsünde {V['E3_full_acc']})"),
                     L("Most settings change the accuracy only a little at low noise", "Çoğu ayar düşük gürültüde doğruluğu yalnızca biraz değiştiriyor"),
                     L(f"One setting stands out: with **σ = 0.9** most of the high-noise gap disappears (remaining gap {V['C2_sigma_gap']} points)", f"Bir ayar öne çıkıyor: **σ = 0.9** ile yüksek gürültüdeki farkın çoğu kayboluyor (kalan fark {V['C2_sigma_gap']} puan)"),
                     L("→ σ became the starting point of our second iteration", "→ σ, ikinci iterasyonumuzun çıkış noktası oldu")],
         "image": "results/figures/e3_ablation.png",
         "notes": L(f"If asked: non-local term alone {V['E3_nl_only']} %, local alone {V['E3_local_only']} % (paper: 82.26 %); at 5 % noise σ, w and δ change ACC by < 0.4 points, k = 1 degrades, δ mainly controls the iterations.",
                    f"Sorulursa: yalnız yerel-olmayan terim {V['E3_nl_only']}, yalnız yerel {V['E3_local_only']} (makale: %82.26); %5 gürültüde σ, w ve δ ACC'yi 0.4 puandan az değiştiriyor, k = 1 bozuyor, δ esas olarak iterasyon sayısını belirliyor.")},
        {"section": L("Contribution · iteration 1", "Katkı · iterasyon 1"), "title": L("Iteration 1: fuzzy rules for the trust weights", "İterasyon 1: güven ağırlıkları için bulanık kurallar"),
         "lead": L("First idea: replace the paper's formula for the three trust weights by readable IF–THEN rules that try to tell noise from edges.",
                   "İlk fikir: makalenin üç güven ağırlığı için kullandığı formülü, gürültüyü kenardan ayırmaya çalışan okunabilir EĞER–İSE kurallarıyla değiştirmek."),
         "bullets": [L("Two inputs: how far the pixel is from the opinions, and how much the two opinions disagree", "İki girdi: pikselin görüşlerden ne kadar uzak olduğu ve iki görüşün ne kadar anlaştığı"),
                     L("9 rules, for example:", "9 kural, örneğin:"),
                     [L("IF the pixel is far off AND the opinions agree THEN it is noise → trust the opinions", "EĞER piksel çok farklıysa VE görüşler anlaşıyorsa O HÂLDE gürültüdür → görüşlere güven"),
                      L("IF the pixel is far off AND the opinions disagree THEN it is near an edge → trust the local opinion", "EĞER piksel çok farklıysa VE görüşler anlaşmıyorsa O HÂLDE kenara yakındır → yerel görüşe güven")],
                     L("Expectations (hypotheses) written down **before** the experiments", "Beklentiler (hipotezler) deneylerden **önce** yazıldı")],
         "image": f"results/figures/fis_inference_example{sfx}.png",
         "notes": L("Walk through the figure: which rules fire, how the output set is built, the result. If asked: inputs Dev = |y − (ξ+ϑ)/2| and Dis = |ξ − ϑ|; outputs α, β, γ; a post-hoc variant 'split' keeps the paper's α and only splits β : γ.",
                    "Şekli anlatın: hangi kurallar ateşleniyor, çıkış kümesi nasıl oluşuyor, sonuç. Sorulursa: girdiler Dev = |y − (ξ+ϑ)/2| ve Dis = |ξ − ϑ|; çıktılar α, β, γ; sonradan eklenen 'split' varyantı makalenin α'sını koruyup yalnız β : γ'yı paylaştırıyor.")},
        {"section": L("Contribution · iteration 1", "Katkı · iterasyon 1"), "title": L("Result: the first rules did not improve accuracy", "Sonuç: ilk kurallar doğruluğu artırmadı"),
         "lead": L("The rules made the weighting readable but lowered the accuracy, strongly at high noise. We report this as it is and analyse the cause.",
                   "Kurallar ağırlıklandırmayı okunabilir kıldı ama doğruluğu düşürdü, yüksek gürültüde belirgin biçimde. Bunu olduğu gibi raporluyor ve nedenini inceliyoruz."),
         "table": {"columns": [L("Setting", "Ayar"), "FCM", L("Paper's formula", "Makalenin formülü"), L("Our rules (Δ)", "Kurallarımız (Δ)"), L("Rules, variant (Δ)", "Kurallar, varyant (Δ)")], "rows": _e5_rows(),
                   "caption": L("accuracy (%), average of 10 runs; Δ = difference to the paper's formula; * = not due to chance", "doğruluk (%), 10 koşunun ortalaması; Δ = makalenin formülüne göre fark; * = şans değil")},
         "callouts": [("~30 %", L("trust our rules leave to a noisy pixel", "kurallarımızın gürültülü piksele bıraktığı güven"), "warn"),
                      ("~0.1 %", L("trust the paper's formula leaves to it", "makalenin formülünün ona bıraktığı güven"))],
         "notes": L("Negative result reported honestly — the guideline does not require an improvement, but it must be analysed. If asked: hypothesis H1 rejected; '*' = paired Wilcoxon p < 0.05.",
                    "Olumsuz sonuç dürüstçe raporlandı — yönerge iyileşmeyi zorunlu tutmuyor ama analiz edilmesini istiyor. Sorulursa: H1 hipotezi reddedildi; '*' = eşleştirilmiş Wilcoxon p < 0.05.")},
        {"section": L("Contribution · analysis", "Katkı · analiz"), "title": L("Why it failed", "Neden başarısız oldu?"),
         "lead": L("The analysis points to two causes. Both shaped the second iteration.", "Analiz iki nedene işaret ediyor. İkinci iterasyonu ikisi de belirledi."),
         "bullets": [L("**Too much trust in noisy pixels**: at 15 % noise almost half of the pixels are noisy, and many of them still get trust", "**Gürültülü piksellere fazla güven**: %15 gürültüde piksellerin neredeyse yarısı gürültülü ve çoğu hâlâ güven alıyor"),
                     L("**Inputs get confused**: when the opinions themselves are noisy, the rules see an “edge” where there is none", "**Girdiler karışıyor**: görüşlerin kendisi gürültülü olunca kurallar olmayan bir yerde “kenar” görüyor"),
                     L(f"The details of the fuzzy system (set shapes, defuzzification, Mamdani or Sugeno) change little (≤ {V['FV_full_maxdiff_nomom']} points)", f"Bulanık sistemin ayrıntıları (küme şekli, durulaştırma, Mamdani ya da Sugeno) az şey değiştiriyor (≤ {V['FV_full_maxdiff_nomom']} puan)"),
                     L("**What matters**: how much the noisy pixel is trusted, and σ", "**Önemli olan**: gürültülü pikselin ne kadar güven aldığı ve σ")],
         "image": "results/figures/e5_robustness_acc.png",
         "notes": L("This diagnosis is the bridge to the second iteration. If asked: H3 and H4 hold; the rules are best on clean / 1 % noise, where trusting consistent pixels is right.",
                    "Bu teşhis ikinci iterasyona köprü. Sorulursa: H3 ve H4 tuttu; kurallar temiz / %1 gürültüde en iyi, çünkü orada tutarlı piksellere güvenmek doğru.")},
        {"section": L("Contribution · iteration 2", "Katkı · iterasyon 2"), "title": L("Iteration 2: let a fuzzy rule choose σ", "İterasyon 2: σ'yı bulanık bir kural seçsin"),
         "lead": L("Second attempt: instead of per-pixel weights, a small rule system sets σ from the noise level of the whole image.",
                   "İkinci deneme: piksel başına ağırlıklar yerine, küçük bir kural sistemi σ'yı tüm görüntünün gürültü düzeyine göre belirliyor."),
         "bullets": [L("Measure how noisy the image is (one number)", "Görüntünün ne kadar gürültülü olduğunu ölç (tek sayı)"),
                     L("3 rules: noise Low → σ small · Medium → medium · High → large", "3 kural: gürültü Düşük → σ küçük · Orta → orta · Yüksek → büyük"),
                     L("Tuned only on separate practice runs; the choice was saved in git **before** the final test", "Yalnızca ayrı deneme koşularında ayarlandı; seçim son testten **önce** git'e kaydedildi"),
                     L("Fair check: we also compare with a fixed σ = 0.9", "Adil kontrol: sabit σ = 0.9 ile de karşılaştırıyoruz")],
         "image": f"results/figures/e8_sigma_fis{'_tr' if lang == 'tr' else ''}.png",
         "notes": L(f"Explain the protocol: tuning on seeds 100–104, testing on 0–9; {V['E8_n_configs']} of 12 allowed configurations tried; hypotheses H5/H6 committed before the test. "
                    "If asked: noise estimate = median(|HH|)/0.6745 of a Haar transform; σ outputs 0.3 / 0.6 / 0.95; two other candidates (bounded α, impulse input) were also tried. The idea came from the earlier test on σ — the test is blind to the parameters, not to the idea.",
                    f"Protokolü anlatın: ayar 100–104 tohumlarında, test 0–9'da; izin verilen 12 konfigürasyonun {V['E8_n_configs']}'u denendi; H5/H6 hipotezleri testten önce commit'lendi. "
                    "Sorulursa: gürültü tahmini = Haar dönüşümünün median(|HH|)/0.6745 değeri; σ çıktıları 0.3 / 0.6 / 0.95; iki aday daha denendi (sınırlı α, dürtü girdisi). Fikir, σ üzerindeki önceki testten geldi — test parametrelere kör, fikre değil.")},
        {"section": L("Contribution · iteration 2", "Katkı · iterasyon 2"), "title": L("Result: a clear gain at high noise", "Sonuç: yüksek gürültüde belirgin kazanç"),
         "lead": L("Under identical conditions the fuzzy σ clearly improves the method at high noise and does not hurt it at low noise. Both expectations (H5, H6) hold.",
                   "Aynı koşullarda bulanık σ yöntemi yüksek gürültüde belirgin biçimde iyileştiriyor, düşük gürültüde zarar vermiyor. İki beklenti de (H5, H6) tuttu."),
         "callouts": [(f"{V['E8_fs_gain10']} / {V['E8_fs_gain15']}", L("accuracy points gained at 10 / 15 % noise", "%10 / %15 gürültüde kazanılan doğruluk puanı")),
                      (V["E8_fs_worst_low"], L("largest loss at 1–5 % noise", "%1–5 gürültüde en büyük kayıp")),
                      ("σ = 0.9", L("a fixed value is just as good — the rule finds it automatically", "sabit değer de aynı derecede iyi — kural onu kendisi buluyor"))],
         "table": {"columns": [L("Setting", "Ayar"), L("Paper (σ = 0.3)", "Makale (σ = 0.3)"), L("Fixed σ = 0.9", "Sabit σ = 0.9"), L("Fuzzy σ (Δ)", "Bulanık σ (Δ)"), L("Fuzzy σ + bounded trust (Δ)", "Bulanık σ + sınırlı güven (Δ)")], "rows": _e8_rows(),
                   "caption": L("accuracy (%), average of 10 test runs; Δ = gain over the paper's setting; * = not due to chance", "doğruluk (%), 10 test koşusunun ortalaması; Δ = makale ayarına göre kazanç; * = şans değil")},
         "notes": L(f"The rule's value is that it picks σ automatically; a fixed σ = 0.9 is as good on mixed noise (differences {V['E8_fs_fixed_range']}). 'Fuzzy σ + bounded trust' (FIS-σ+A) also bounds the trust in the noisy pixel; it makes the first rule base harmless (worst difference {V['E8_fsa_worst']}). "
                    f"If asked: p < 0.001 at 10 and 15 %; at 15 % sy2/sy3 reach {V['E8_fs_15_sy2']}/{V['E8_fs_15_sy3']} %.",
                    f"Kuralın değeri σ'yı otomatik seçmesi; karışık gürültüde sabit σ = 0.9 da aynı derecede iyi (farklar {V['E8_fs_fixed_range']}). 'Bulanık σ + sınırlı güven' (FIS-σ+A) ayrıca gürültülü piksele duyulan güveni sınırlıyor; ilk kural tabanını zararsız hâle getiriyor (en kötü fark {V['E8_fsa_worst']}). "
                    f"Sorulursa: %10 ve %15'te p < 0.001; %15'te sy2/sy3 {V['E8_fs_15_sy2']}/{V['E8_fs_15_sy3']}'e ulaşıyor.")},
        {"section": L("Contribution · iteration 2", "Katkı · iterasyon 2"), "title": L("Does it work beyond the test images?", "Test görüntülerinin dışında da çalışıyor mu?"),
         "lead": L("The gain carries over to real photographs and to other noise types. The noise measurement has two blind spots.",
                   "Kazanç gerçek fotoğraflara ve diğer gürültü türlerine de taşınıyor. Gürültü ölçümünün iki kör noktası var."),
         "bullets": [L(f"Natural photographs (gray): {V['E8_bsds_gray_paper']} → {V['E8_bsds_gray_fs']} % accuracy", f"Doğal fotoğraflar (gri): doğruluk {V['E8_bsds_gray_paper']} → {V['E8_bsds_gray_fs']}"),
                     L(f"Natural photographs (colour): {V.get('E8_bsds_rgb_paper', '–')} → {V.get('E8_bsds_rgb_fs', '–')} %", f"Doğal fotoğraflar (renkli): {V.get('E8_bsds_rgb_paper', '–')} → {V.get('E8_bsds_rgb_fs', '–')}"),
                     L("Blind spot 1: texture looks like noise to the measurement", "1. kör nokta: doku, ölçüme gürültü gibi görünüyor"),
                     L("Blind spot 2: scattered black-and-white dots (salt-and-pepper) are not seen → σ stays small", "2. kör nokta: dağınık siyah-beyaz noktalar (tuz-biber) görülmüyor → σ küçük kalıyor")],
         "image": f"results/figures/e8_robustness_acc{'_tr' if lang == 'tr' else ''}.png",
         "notes": L(f"If asked: over four noise types at 0–20 % the fuzzy σ differs from a fixed σ = 0.9 by {V.get('E8_rob_fs_fixed_min', '–')} … {V.get('E8_rob_fs_fixed_max', '–')} points; salt-and-pepper 20 %: estimate 0, fixed 0.9 slightly better.",
                    f"Sorulursa: %0–20 aralığında dört gürültü türünde bulanık σ ile sabit σ = 0.9 arasındaki fark {V.get('E8_rob_fs_fixed_min', '–')} … {V.get('E8_rob_fs_fixed_max', '–')} puan; tuz-biber %20: tahmin 0, sabit 0.9 biraz daha iyi.")},
        {"section": L("Contribution · iteration 2", "Katkı · iterasyon 2"),
         "title": L("Against the paper's own numbers: closer, not better", "Makalenin kendi sayılarına göre: daha yakın, ama daha iyi değil"),
         "lead": L("Compared with the numbers printed in the paper, we are equal at low noise and closer, but still below, at high noise.",
                   "Makalede basılı sayılarla karşılaştırıldığında düşük gürültüde eşitiz, yüksek gürültüde daha yakınız ama hâlâ altındayız."),
         "callouts": [(f"{V['E8_gap15_closed']} %", L("of the gap to the paper at 15 % noise closed", "%15 gürültüde makaleye olan farkın kapanan kısmı")),
                      (V["E8_gap15_after"], L(f"points still below the paper at 15 % (was {V['E8_gap15_before']})", f"%15'te makalenin hâlâ altında kalınan puan (önce {V['E8_gap15_before']})")),
                      (f"{V['E8_bsds_rgb_fs']} / {V['E6_paper_ours_mean']}", L("colour photographs: ours / paper", "renkli fotoğraflar: bizim / makale"))],
         "table": {"columns": [L("Setting", "Ayar"), L("Paper's number", "Makaledeki sayı"), L("Ours, paper's σ (Δ)", "Bizim, makale σ'sı (Δ)"), L("Ours, fuzzy σ (Δ)", "Bizim, bulanık σ (Δ)")],
                   "rows": _e8_reported_rows(),
                   "caption": L(f"accuracy (%), average of 10 test runs; Δ = difference to the paper's number. At 1–5 % noise: {V['E8_rep_low_min']} … {V['E8_rep_low_max']} (agreement)",
                                f"doğruluk (%), 10 test koşusunun ortalaması; Δ = makaledeki sayıya göre fark. %1–5 gürültüde: {V['E8_rep_low_min']} … {V['E8_rep_low_max']} (uyum)")},
         "notes": L("Separate the two comparisons. Same code, same noise: the fuzzy σ beats the paper's setting at 10–15 % and never loses meaningfully. "
                    "Against the numbers printed in the paper (other implementation, other noise, so only indicative): equal at low noise, "
                    f"still {V['E8_gap15_after']} points below at 15 % on sy2/sy3, down from {V['E8_gap15_before']}. Do not claim that we beat the paper.",
                    "İki karşılaştırmayı ayırın. Aynı kod, aynı gürültü: bulanık σ %10–15'te makale ayarını geçiyor, hiçbir yerde anlamlı kaybı yok. "
                    "Makalede basılı sayılara göre (başka uygulama, başka gürültü; yalnızca yol gösterici): düşük gürültüde eşit, %15'te sy2/sy3'te "
                    f"hâlâ {V['E8_gap15_after']} puan aşağıda (önce {V['E8_gap15_before']}). 'Makaleyi geçtik' demeyin.")},
        {"section": L("Real images", "Gerçek görüntüler"), "title": L("Real photographs (BSDS500)", "Gerçek fotoğraflar (BSDS500)"),
         "lead": L("On natural photographs the method also clearly improves plain FCM. Running it on the colour versions brings our numbers closer to the paper's.",
                   "Doğal fotoğraflarda da yöntem düz FCM'yi belirgin biçimde iyileştiriyor. Renkli sürümlerde çalıştırmak sayılarımızı makaledekilere yaklaştırıyor."),
         "bullets": [L(f"Gray photographs: FCM {V['E6_fcm_mean']} → method {V['E6_asr_mean']} % accuracy", f"Gri fotoğraflar: doğruluk FCM {V['E6_fcm_mean']} → yöntem {V['E6_asr_mean']}"),
                     L(f"Colour photographs: FCM {V['E6c_fcm_mean']} → method {V['E6c_asr_mean']} % (paper: {V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']} %)",
                       f"Renkli fotoğraflar: FCM {V['E6c_fcm_mean']} → yöntem {V['E6c_asr_mean']} (makale: {V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']})"),
                     L(f"Our first rules: {V['E6_full_mean']} % — again below the paper's formula", f"İlk kurallarımız: {V['E6_full_mean']} — yine makalenin formülünün altında")],
         "image": "results/figures/panel_bsds.png",
         "notes": L(f"The paper's photographs are in colour, so we also ran a colour version of the method (D-043). If asked: split variant {V['E6_split_mean']} %, hypothesis H2 rejected.",
                    f"Makaledeki fotoğraflar renkli, bu yüzden yöntemin renkli bir sürümünü de çalıştırdık (D-043). Sorulursa: split varyantı {V['E6_split_mean']}, H2 hipotezi reddedildi.")},
        {"section": L("Discussion", "Tartışma"), "title": L("What we learned — and the limits", "Ne öğrendik — ve sınırlar"),
         "lead": L("The project followed a full cycle: reproduce, extend, fail, analyse and try again more carefully.",
                   "Proje tam bir döngü izledi: yeniden üret, geliştir, başarısız ol, analiz et ve daha dikkatli biçimde yeniden dene."),
         "bullets": [L("The first rules failed; the analysis showed why; the second attempt worked", "İlk kurallar başarısız oldu; analiz nedenini gösterdi; ikinci deneme işe yaradı"),
                     L(f"Better than the paper's setting under identical conditions; still below the paper's own numbers at high noise ({V['E8_gap15_after']} points at 15 %)",
                       f"Aynı koşullarda makalenin ayarından iyi; yüksek gürültüde makalenin kendi sayılarının hâlâ altında (%15'te {V['E8_gap15_after']} puan)"),
                     L("A well-chosen fixed σ = 0.9 is just as good — the rule's value is choosing it automatically", "İyi seçilmiş sabit σ = 0.9 de aynı derecede iyi — kuralın değeri bunu otomatik seçmesi"),
                     L("Limits: test images re-drawn from the paper's figures; the number of regions must be known", "Sınırlar: test görüntüleri makalenin şekillerinden yeniden çizildi; bölge sayısı önceden bilinmeli"),
                     L("Next: a noise measurement that is not fooled by texture; rules learned from data", "Sonraki adımlar: dokuya aldanmayan bir gürültü ölçümü; veriden öğrenilen kurallar")],
         "notes": L("Be clear about what was and was not done; the guideline values the analysis, not only the accuracy. If asked: the 8 comparison methods of the paper were not re-implemented; iteration 2 was tuned on other noise seeds of the same images.",
                    "Neyin yapılıp neyin yapılmadığını açıkça söyleyin; yönerge yalnız doğruluğu değil analizi de değerlendiriyor. Sorulursa: makaledeki 8 karşılaştırma yöntemi yeniden yazılmadı; iterasyon 2 aynı görüntülerin başka gürültü tohumlarıyla ayarlandı.")},
        {"section": L("Conclusion", "Sonuç"), "title": L("Conclusion", "Sonuç"),
         "lead": L("A fuzzy rule helps most where the method leaves a setting open: choosing σ from the image recovers most of the accuracy lost at high noise.",
                   "Bulanık bir kural en çok, yöntemin açık bıraktığı bir ayarda işe yarıyor: σ'yı görüntüden seçmek yüksek gürültüde kaybedilen doğruluğun çoğunu geri kazandırıyor."),
         "bullets": [L("The paper's method was rebuilt and reproduced well at low and medium noise", "Makalenin yöntemi yeniden kuruldu ve düşük-orta gürültüde iyi biçimde yeniden üretildi"),
                     L("Iteration 1 (rules for the trust weights): readable, but no accuracy gain — the cause was found",
                       "İterasyon 1 (güven ağırlıkları için kurallar): okunabilir ama doğruluk kazancı yok — nedeni bulundu"),
                     L(f"Iteration 2 (fuzzy σ): {V['E8_fs_gain10']} / {V['E8_fs_gain15']} accuracy points at 10 / 15 % noise",
                       f"İterasyon 2 (bulanık σ): %10 / %15 gürültüde {V['E8_fs_gain10']} / {V['E8_fs_gain15']} doğruluk puanı"),
                     L("Code, data steps, results and decisions: github.com/tarikoztas/fuzzy-logic-project", "Kod, veri adımları, sonuçlar ve kararlar: github.com/tarikoztas/fuzzy-logic-project")],
         "notes": L("Summarise in one sentence, thank the audience and invite questions.", "Tek cümleyle özetleyin, teşekkür edin ve soruları davet edin.")},
    ]
