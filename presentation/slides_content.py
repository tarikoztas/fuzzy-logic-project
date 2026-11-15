"""Slide specification (15-20 min talk) in English and Turkish. Numbers come from
report/report_values.py (CSV-based), so both languages show identical values.

Guideline Sec. 4 coverage: problem & motivation (2), literature (3), fuzzy-logic background (4),
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
         "title": L("Reproducing an Adaptive Sparse-Regularized Fuzzy Clustering Method for Noisy Image Segmentation — and Extending It with Mamdani Rule Bases",
                    "Gürültülü Görüntü Bölütleme için Uyarlamalı Seyrek Düzenlileştirilmiş Bulanık Kümeleme Yönteminin Yeniden Gerçekleştirilmesi ve Mamdani Kural Tabanlarıyla Geliştirilmesi"),
         "subtitle": L("Tarık Öztaş (1306230040) · İstanbul University-Cerrahpaşa, Computer Engineering · Reference paper: Wu et al., Expert Systems with Applications 256 (2024) 124943",
                       "Tarık Öztaş (1306230040) · İstanbul Üniversitesi-Cerrahpaşa, Bilgisayar Mühendisliği · Referans makale: Wu vd., Expert Systems with Applications 256 (2024) 124943"),
         "notes": L("Introduce yourself and the paper. Say what you will show: re-implementation, reproduction, two iterations of a fuzzy-rule extension, and an honest evaluation.",
                    "Kendinizi ve makaleyi tanıtın. Neleri göstereceğinizi söyleyin: yeniden gerçekleştirme, yeniden üretim, bulanık kural tabanlı geliştirmenin iki iterasyonu ve dürüst bir değerlendirme.")},
        {"section": L("Problem", "Problem"), "title": L("Why noisy image segmentation is hard for FCM", "Gürültülü görüntü bölütleme FCM için neden zor?"),
         "lead": L('Real images often contain several kinds of noise at once. FCM decides each pixel only from its own gray value, so a single noisy pixel can switch to the wrong class.', 'Gerçek görüntülerde çoğu zaman birkaç gürültü türü bir arada bulunur. FCM her pikseli yalnızca kendi gri değerine göre sınıflandırdığı için tek bir gürültülü piksel yanlış sınıfa geçebilir.'),
         "bullets": [L("Segmentation = split an image into homogeneous regions", "Bölütleme = görüntüyü homojen bölgelere ayırmak"),
                     L("**Fuzzy C-means**: every pixel belongs to every cluster with a degree u ∈ [0, 1]", "**Bulanık C-ortalamalar (FCM)**: her piksel her kümeye u ∈ [0, 1] derecesiyle üye"),
                     L("FCM looks only at the gray value of each pixel → noise flips memberships", "FCM yalnızca pikselin gri değerine bakar → gürültü üyelikleri bozar"),
                     [L("e.g. our FCM on sy3 with 15 % mixed noise: ACC ≈ 56 %", "ör. bizim FCM, sy3, %15 karışık gürültü: ACC ≈ %56")],
                     L("Goal of the paper: robust segmentation under **mixed** Gaussian + salt-and-pepper + multiplicative noise, with few iterations",
                       "Makalenin amacı: **karışık** Gauss + tuz-biber + çarpımsal gürültü altında, az iterasyonla dayanıklı bölütleme")],
         "image": "results/figures/panel_synthetic.png", "caption": L("sy1–sy3, 10 % mixed noise: FCM vs. the method (ours)", "sy1–sy3, %10 karışık gürültü: FCM ve yöntem (bizim)"),
         "notes": L("Show the noisy images and how FCM fails. Motivation: real images (medical, remote sensing) contain several noise types at once.",
                    "Gürültülü görüntüleri ve FCM'nin nasıl başarısız olduğunu gösterin. Motivasyon: gerçek görüntülerde (tıbbi, uzaktan algılama) aynı anda birkaç gürültü türü bulunur.")},
        {"section": L("Literature", "Literatür"), "title": L("How earlier work adds spatial information to FCM", "Önceki çalışmalar FCM'ye uzamsal bilgiyi nasıl ekliyor?"),
         "lead": L('Most improvements add information from the neighbourhood of a pixel. The reference paper combines local, non-local and wavelet-domain information with adaptive weights and sparsity.', 'İyileştirmelerin çoğu pikselin çevresinden bilgi ekler. Referans makale yerel, yerel-olmayan ve dalgacık alanı bilgisini uyarlamalı ağırlıklar ve seyreklikle birleştiriyor.'),
         "table": {"columns": [L("Family", "Aile"), L("Examples", "Örnekler"), L("Idea", "Fikir"), L("Weakness (per [1])", "Zayıflık ([1]'e göre)")],
                   "rows": [[L("Local", "Yerel"), "BCFCM, FCM_S, FGFCM, FLICM, FRFCM", L("average / filter neighbours", "komşuları ortala / filtrele"), L("biased if many neighbours are noisy", "komşuların çoğu gürültülüyse yanlı")],
                            [L("Non-local", "Yerel-olmayan"), "FCM_SNLS, FALRCM, FSC_LNML", L("similar patches anywhere", "her yerdeki benzer yamalar"), L("keeps noise, blurs in spatial domain", "gürültüyü taşır, uzamsal alanda bulanıklaştırır")],
                            [L("Transform + sparse", "Dönüşüm + seyrek"), "WFCM, SRFCM, DSFCM_N", L("wavelet domain, sparse U", "dalgacık alanı, seyrek U"), L("no non-local / adaptive weights", "yerel-olmayan / uyarlamalı ağırlık yok")],
                            [L("Recent (2023–25)", "Güncel (2023–25)"), "Jiao'23, Chen'23, Das'25", L("adaptive weights, auto-K", "uyarlamalı ağırlık, otomatik K"), "—"],
                            ["Wu et al. 2024 [1]", L("this paper", "bu makale"), L("local + non-local (DTCWT) + adaptive + ℓ0", "yerel + yerel-olmayan (DTCWT) + uyarlamalı + ℓ0"), L("cost O(n⁵)", "maliyet O(n⁵)")]],
                   "caption": L("33 references verified on Crossref (references/README.md)", "33 kaynak Crossref üzerinden doğrulandı (references/README.md)")},
         "notes": L("Explain the four strands; the paper is the only one combining all five ingredients. Closest relatives: SRFCM (sparsity framework) and FSC_LNML (same lab).",
                    "Dört akımı anlatın; makale beş bileşeni birleştiren tek çalışma. En yakın akrabaları: SRFCM (seyreklik çerçevesi) ve FSC_LNML (aynı laboratuvar).")},
        {"section": L("Fuzzy-logic background", "Bulanık mantık altyapısı"), "title": L("Fuzzy sets, fuzzy clustering and fuzzy inference", "Bulanık kümeler, bulanık kümeleme ve bulanık çıkarım"),
         "lead": L('Two fuzzy ideas meet in this project: fuzzy clustering, where every pixel belongs partly to every class, and Mamdani inference, which turns IF–THEN rules into numbers.', 'Bu projede iki bulanık fikir buluşuyor: her pikselin her sınıfa kısmen ait olduğu bulanık kümeleme ve EĞER–İSE kurallarını sayıya çeviren Mamdani çıkarımı.'),
         "bullets": [L("Fuzzy set: membership function μ(x) ∈ [0, 1] (Zadeh 1965)", "Bulanık küme: üyelik fonksiyonu μ(x) ∈ [0, 1] (Zadeh 1965)"),
                     L("FCM: each cluster is a fuzzy set over the pixels; minimise Σ u^m (y − c)², Σ_i u = 1", "FCM: her küme pikseller üzerinde bir bulanık küme; Σ u^m (y − c)² en küçüklenir, Σ_i u = 1"),
                     L("Mamdani inference: fuzzify → rule firing (AND = min) → clip consequents → aggregate (max) → defuzzify",
                       "Mamdani çıkarımı: bulanıklaştır → kural ateşleme (VE = min) → sonuçları kırp → birleştir (max) → durulaştır"),
                     L("Defuzzification: centroid, bisector, mean of maxima; Sugeno: constants + weighted average",
                       "Durulaştırma: ağırlık merkezi, açıortay, maksimumların ortalaması; Sugeno: sabitler + ağırlıklı ortalama")],
         "image": f"results/figures/fis_membership{sfx}.png", "caption": L("membership functions of the first rule base", "ilk kural tabanının üyelik fonksiyonları"),
         "notes": L("Connect to the lectures. FCM is fuzzy because of the membership matrix; the paper has no explicit rule base — this motivates our extension.",
                    "Derslerle bağ kurun. FCM üyelik matrisi nedeniyle bulanıktır; makalede açık bir kural tabanı yok — geliştirmemizin çıkış noktası bu.")},
        {"section": L("Reference method", "Referans yöntem"), "title": L("Architecture of the method (and where our extension plugs in)", "Yöntemin mimarisi (ve geliştirmemizin yeri)"),
         "lead": L('Each pixel is described three times: by its own value, by a local estimate and by a non-local estimate. The clustering weighs these three views pixel by pixel.', 'Her piksel üç kez tanımlanır: kendi değeriyle, yerel bir kestirimle ve yerel-olmayan bir kestirimle. Kümeleme bu üç görüşü piksel piksel ağırlıklandırır.'),
         "bullets": [L("Input: noisy gray image y ∈ [0, 1], number of clusters K", "Girdi: gürültülü gri görüntü y ∈ [0, 1], küme sayısı K"),
                     L("ξ: local estimate (reward/penalty sets)", "ξ: yerel kestirim (ödül/ceza kümeleri)"), L("ϑ: non-local estimate in the DTCWT domain", "ϑ: DTCWT alanında yerel-olmayan kestirim"),
                     L("α, β, γ: per-pixel trust in y, ξ, ϑ", "α, β, γ: y, ξ, ϑ'ya piksel başına güven"), L("Sparse FCM: d = α(y−c)² + β(ξ−c)² + γ(ϑ−c)²", "Seyrek FCM: d = α(y−c)² + β(ξ−c)² + γ(ϑ−c)²"),
                     L("Output: U (K×N), centres, label = argmax U", "Çıktı: U (K×N), merkezler, etiket = argmax U")],
         "image": f"results/figures/architecture{sfx}.png", "narrow_text": True,
         "notes": L("Walk through the pipeline left to right. Orange box = first iteration of our contribution; the second iteration acts on σ inside the ξ box.",
                    "Akışı soldan sağa anlatın. Turuncu kutu = katkımızın ilk iterasyonu; ikinci iterasyon ξ kutusunun içindeki σ'ya etki ediyor.")},
        {"section": L("Reference method", "Referans yöntem"), "title": L("Local information ξ: golden-ratio reward and penalty sets", "Yerel bilgi ξ: altın oranlı ödül ve ceza kümeleri"),
         "lead": L('The local estimate is a robust weighted mean: neighbours close to the typical value are rewarded, extreme ones are penalised but not removed.', 'Yerel kestirim dayanıklı bir ağırlıklı ortalamadır: tipik değere yakın komşular ödüllendirilir, uç değerler cezalandırılır ama atılmaz.'),
         "bullets": [L("Sort the neighbours in the w×w window by gray value", "w×w penceredeki komşuları gri değere göre sırala"),
                     L("Middle ⌊0.618·(N_R−1)⌋ → **reward set** (weight 1+σ), ends → **penalty set** (1−σ)", "Ortadaki ⌊0.618·(N_R−1)⌋ → **ödül kümesi** (ağırlık 1+σ), uçlar → **ceza kümesi** (1−σ)"),
                     [L("Fig. 1 of the paper: reward {169, 172, 174, 176}, penalty {103, 137, 194, 212} — reproduced exactly", "Makalenin Şekil 1'i: ödül {169, 172, 174, 176}, ceza {103, 137, 194, 212} — birebir yeniden üretildi")],
                     L("Weight = (1±σ) · exp(−Δgray²/τ²) · exp(−distance); ξ = weighted mean", "Ağırlık = (1±σ) · exp(−Δgri²/τ²) · exp(−uzaklık); ξ = ağırlıklı ortalama"),
                     L("**σ** = how strongly the extremes are down-weighted → key parameter of our second iteration", "**σ** = uçların ne kadar bastırılacağı → ikinci iterasyonumuzun anahtar parametresi")],
         "callouts": [("σ = 0.3", L("paper's value", "makalenin değeri")), ("σ = 0.9", L("better at high noise in our ablation", "ablasyonumuzda yüksek gürültüde daha iyi"), "warn")],
         "notes": L("Analogy: a jury that down-weights, but does not delete, the most extreme scores. We round the set size down, as in Fig. 1 of the paper (D-014).",
                    "Benzetme: en uç puanları silmeyen ama ağırlığını düşüren bir jüri. Küme boyutunu makalenin Şekil 1'indeki gibi aşağı yuvarlıyoruz (D-014).")},
        {"section": L("Reference method", "Referans yöntem"), "title": L("Non-local information ϑ in the wavelet domain", "Dalgacık alanında yerel-olmayan bilgi ϑ"),
         "lead": L('The non-local estimate smooths the image in the wavelet domain, where noise and structure are easier to separate than among the pixels themselves.', 'Yerel-olmayan kestirim görüntüyü dalgacık alanında yumuşatır; orada gürültü ile yapı, piksellerin kendisine göre daha kolay ayrılır.'),
         "bullets": [L("DTCWT: 1 low-pass + 6 complex direction sub-bands (±15°, ±45°, ±75°), near shift-invariant", "DTCWT: 1 alçak geçiren + 6 karmaşık yön alt bandı (±15°, ±45°, ±75°), kaymaya neredeyse duyarsız"),
                     L("Non-local means on all 7 sub-bands: 15×15 search window, 5×5 patches, h² = g·w² = 250", "7 alt bandın hepsinde yerel-olmayan ortalama: 15×15 arama penceresi, 5×5 yama, h² = g·w² = 250"),
                     L("Inverse DTCWT → ϑ", "Ters DTCWT → ϑ"),
                     L("Effect: strong smoothing in flat regions, while the direction sub-bands keep the edges", "Etkisi: düz bölgelerde güçlü yumuşatma, yön alt bantları ise kenarları koruyor")],
         "notes": L("Explain DTCWT with the analogy of splitting a song into bass/mid/treble channels.",
                    "DTCWT'yi bir şarkıyı bas/orta/tiz kanallarına ayırma benzetmesiyle anlatın.")},
        {"section": L("Reference method", "Referans yöntem"), "title": L("Adaptive coefficients and sparse-regularised FCM", "Uyarlamalı katsayılar ve seyrek düzenlileştirilmiş FCM"),
         "lead": L('Three coefficients decide how much each pixel trusts its own value and the two estimates; a sparsity term then keeps only clear memberships.', 'Üç katsayı, her pikselin kendi değerine ve iki kestirime ne kadar güveneceğini belirler; seyreklik terimi ise yalnızca belirgin üyelikleri bırakır.'),
         "bullets": [L("ΔG1 = k·exp(y − ξ), ΔG2 = k·exp(y − ϑ);  α = 1/(ΔG1+ΔG2), β = ΔG1, γ = ΔG2", "ΔG1 = k·exp(y − ξ), ΔG2 = k·exp(y − ϑ);  α = 1/(ΔG1+ΔG2), β = ΔG1, γ = ΔG2"),
                     [L("k = 15 → α ≈ 0.01–0.1, β ≈ γ ≈ 5–40: the original pixel gets ~0.1 % of the trust", "k = 15 → α ≈ 0.01–0.1, β ≈ γ ≈ 5–40: özgün piksel güvenin ~%0.1'ini alıyor")],
                     L("Objective J = Σ u^m d + δ‖U‖₀; per iteration: centres → η → hard threshold √δ → normalise", "Amaç J = Σ u^m d + δ‖U‖₀; her iterasyonda: merkezler → η → sert eşik √δ → normalize"),
                     L("√0.4 = 0.63 > 0.5 → at most one membership per pixel survives (D-011r)", "√0.4 = 0.63 > 0.5 → piksel başına en fazla bir üyelik kalıyor (D-011r)"),
                     L("Parameters: w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4, m=2", "Parametreler: w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4, m=2")],
         "notes": L("Emphasise the scale of the coefficients — it becomes important for our extension.", "Katsayıların ölçeğini vurgulayın — geliştirmemiz için önemli hâle geliyor.")},
        {"section": L("Fuzzy system", "Bulanık sistem"), "title": L("The fuzzy systems of the project at a glance", "Projedeki bulanık sistemler bir bakışta"),
         "lead": L("The paper's method is fuzzy through its membership matrix but has no explicit rules. Our two iterations add explicit Mamdani rule bases at two different points.", 'Makalenin yöntemi üyelik matrisi sayesinde bulanıktır ama açık kuralı yoktur. İki iterasyonumuz iki farklı noktaya açık Mamdani kural tabanları ekliyor.'),
         "table": {"columns": [L("Element", "Öğe"), L("Paper (fuzzy clustering)", "Makale (bulanık kümeleme)"), L("Iteration 1: α, β, γ", "İterasyon 1: α, β, γ"), L("Iteration 2: σ", "İterasyon 2: σ")],
                   "rows": [[L("Inputs", "Girdiler"), "y, ξ, ϑ, K", "Dev = |y − (ξ+ϑ)/2|, Dis = |ξ − ϑ|", L("image noise estimate", "görüntü gürültü tahmini")],
                            [L("Membership functions", "Üyelik fonksiyonları"), "u_ij", L("Small/Medium/Large (tri / Gauss)", "Küçük/Orta/Büyük (üçgen / Gauss)"), L("Low/Medium/High", "Düşük/Orta/Yüksek")],
                            [L("Rule base", "Kural tabanı"), L("implicit (objective)", "örtük (amaç fonksiyonu)"), L("9 IF–THEN rules", "9 EĞER–İSE kuralı"), L("3 rules", "3 kural")],
                            [L("Inference", "Çıkarım"), L("alternating optimisation", "dönüşümlü eniyileme"), "min / min / max", "min / min / max"],
                            [L("Defuzzification", "Durulaştırma"), "argmax u_ij", L("centroid / bisector / MOM; Sugeno", "ağırlık merkezi / açıortay / MOM; Sugeno"), L("centroid", "ağırlık merkezi")],
                            [L("Outputs", "Çıktılar"), L("U, centres, labels", "U, merkezler, etiketler"), L("α, β, γ per pixel", "piksel başına α, β, γ"), L("σ per image", "görüntü başına σ")]]},
         "notes": L("This slide answers the guideline items: inputs/outputs, membership functions, rule base, inference, defuzzification — for the paper and for both iterations.",
                    "Bu slayt yönergenin istediği öğeleri karşılıyor: girdi/çıktı, üyelik fonksiyonları, kural tabanı, çıkarım, durulaştırma — makale ve iki iterasyon için.")},
        {"section": L("Experiments", "Deneyler"), "title": L("Data, noise and protocol", "Veri, gürültü ve protokol"),
         "lead": L('All methods see exactly the same noisy images and start from the same initial memberships, so the differences come only from the methods.', 'Tüm yöntemler birebir aynı gürültülü görüntüleri görür ve aynı başlangıç üyelikleriyle başlar; böylece farklar yalnızca yöntemlerden gelir.'),
         "bullets": [L("sy1–sy3 (256×256, K = 2/3/3) extracted from the paper's Fig. 9; BSDS500: 8 images with the 2–4 class ground truths of Fig. 22",
                       "sy1–sy3 (256×256, K = 2/3/3) makalenin Şekil 9'undan çıkarıldı; BSDS500: Şekil 22'deki 2–4 sınıflı referanslarla 8 görüntü"),
                     L("Mixed noise p % = Gaussian(var p) → speckle(var p) → salt-and-pepper(p) — our reading, validated by the FCM agreement",
                       "Karışık gürültü %p = Gauss(varyans p) → benek(varyans p) → tuz-biber(p) — bizim yorumumuz, FCM uyumuyla doğrulandı"),
                     L("10 seeds per setting; same noise and initial U for all methods; paired Wilcoxon tests",
                       "Her ayar için 10 tohum; tüm yöntemlerde aynı gürültü ve başlangıç U; eşleştirilmiş Wilcoxon testleri"),
                     L(f"Metrics: V_PC, V_PE, ACC, F, NMI, Kappa, iterations, time; Hungarian matching; {V['n_tests']} unit tests",
                       f"Ölçütler: V_PC, V_PE, ACC, F, NMI, Kappa, iterasyon, süre; Macar eşlemesi; {V['n_tests']} birim testi")],
         "notes": L("Stress fairness: identical noise realisations and initialisations; only one factor changes at a time.",
                    "Adilliği vurgulayın: aynı gürültü örnekleri ve başlangıçlar; her seferinde tek bir etken değişiyor.")},
        {"section": L("Paper's results", "Makalenin sonuçları"), "title": L("What the paper reports", "Makale neler raporluyor?"),
         "lead": L("These are the paper's own numbers; they are the target of our reproduction.", 'Bunlar makalenin kendi sayıları; yeniden üretimimizin hedefi bunlar.'),
         "callouts": [("79.58 → 99.23", L("mean ACC (%) on the synthetic images, FCM → method (Tables 2–8)", "sentetik görüntülerde ortalama ACC (%), FCM → yöntem (Tablo 2–8)")),
                      (f"{V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']}", L("mean ACC (%) on BSDS500 (Table 9)", "BSDS500'de ortalama ACC (%) (Tablo 9)"))],
         "bullets": [L("Ablation (Table 1): non-local term most effective; all three components best", "Ablasyon (Tablo 1): en etkili bileşen yerel-olmayan terim; üçü birlikte en iyi"),
                     L("Fewer iterations thanks to sparsity; best or near-best against 8 methods", "Seyreklik sayesinde daha az iterasyon; 8 yönteme karşı en iyi ya da en iyiye yakın")],
         "notes": L("These are paper-reported numbers (labelled as such everywhere).", "Bunlar makalede raporlanan sayılar (her yerde böyle etiketli).")},
        {"section": L("Reproduction", "Yeniden üretim"), "title": L("Our reproduction vs. the paper (synthetic images)", "Yeniden üretimimiz ve makale (sentetik görüntüler)"),
         "lead": L('FCM agrees closely with the paper, which confirms our images and noise. The method agrees at low noise but falls behind at high noise.', 'FCM makaleyle yakından uyuşuyor; bu, görüntülerimizi ve gürültüyü doğruluyor. Yöntem düşük gürültüde uyuşuyor, yüksek gürültüde geride kalıyor.'),
         "table": {"columns": [L("Setting", "Ayar"), L("FCM ours / paper", "FCM bizim / makale"), L("Method ours / paper", "Yöntem bizim / makale")], "rows": _e2_rows(),
                   "caption": L("ACC (%), mean of 10 seeds vs paper-reported", "ACC (%), 10 tohumun ortalaması ve makalede raporlanan")},
         "image": "results/figures/e2_asrfcm_vs_paper_compact.png",
         "bullets": [L(f"FCM: mean |Δ| = {V['E1_acc_mad']} ACC points", f"FCM: ortalama |Δ| = {V['E1_acc_mad']} ACC puanı"),
                     L(f"Method: {V['E2_acc_mad_low']} points up to 5 %, {V['E2_acc_mad_high']} at 10–15 %", f"Yöntem: %5'e kadar {V['E2_acc_mad_low']} puan, %10–15'te {V['E2_acc_mad_high']} puan")],
         "notes": L("FCM agreement validates images and noise. The method matches at low noise; at high noise on 3-class images it is lower — explained on the next slides.",
                    "FCM uyumu görüntüleri ve gürültüyü doğruluyor. Yöntem düşük gürültüde tutuyor; üç sınıflı görüntülerde yüksek gürültüde daha düşük — sonraki slaytlarda açıklanıyor.")},
        {"section": L("Reproduction", "Yeniden üretim"), "title": L("Ablation and sensitivity", "Ablasyon ve duyarlılık"),
         "lead": L('Removing one component at a time shows what each part contributes; changing one parameter at a time shows which choices matter.', 'Bileşenleri tek tek çıkarmak her parçanın katkısını, parametreleri tek tek değiştirmek hangi seçimlerin önemli olduğunu gösteriyor.'),
         "bullets": [L(f"All three components: ACC {V['E3_full_acc']} % (sy1/sy2/sy3); non-local alone {V['E3_nl_only']} %", f"Üç bileşen birlikte: ACC {V['E3_full_acc']} (sy1/sy2/sy3); yalnız yerel-olmayan {V['E3_nl_only']}"),
                     L(f"Local alone is strong in our runs ({V['E3_local_only']} %), paper: 82.26 %", f"Yalnız yerel terim bizde güçlü ({V['E3_local_only']}), makale: %82.26"),
                     L("Sensitivity at 5 %: σ, w, δ change ACC by < 0.4 points; k = 1 degrades; δ mainly controls the iterations", "%5'te duyarlılık: σ, w, δ ACC'yi < 0.4 puan değiştiriyor; k = 1 bozuyor; δ esas olarak iterasyonu belirliyor"),
                     L(f"**σ = 0.9** closes most of the high-noise gap (sy2/sy3 at 15 %: gap {V['C2_sigma_gap']} points)", f"**σ = 0.9** yüksek gürültü farkının çoğunu kapatıyor (sy2/sy3, %15: fark {V['C2_sigma_gap']} puana)")],
         "image": "results/figures/e3_ablation.png",
         "notes": L("The reward factor σ is the most influential parameter at high noise. Remember this — it drives the second iteration.",
                    "Ödül katsayısı σ yüksek gürültüde en etkili parametre. Bunu akılda tutun — ikinci iterasyonu yönlendiren bu.")},
        {"section": L("Contribution · iteration 1", "Katkı · iterasyon 1"), "title": L("A Mamdani rule base for α, β, γ", "α, β, γ için Mamdani kural tabanı"),
         "lead": L("First idea: replace the paper's fixed formula for the three trust coefficients by readable IF–THEN rules that try to tell noise from edges.", 'İlk fikir: makalenin üç güven katsayısı için kullandığı sabit formülü, gürültüyü kenardan ayırmaya çalışan okunabilir EĞER–İSE kurallarıyla değiştirmek.'),
         "bullets": [L("Inputs Dev (pixel vs. consensus) and Dis (disagreement ≈ edge); 9 rules, e.g.", "Girdiler Dev (piksel ile uzlaşı farkı) ve Dis (anlaşmazlık ≈ kenar); 9 kural, ör."),
                     [L("IF Dev is Large AND Dis is Small THEN α Low, β High, γ High (noise in a flat region)", "EĞER Dev Büyük VE Dis Küçük İSE α Düşük, β Yüksek, γ Yüksek (düz bölgede gürültü)"),
                      L("IF Dev is Large AND Dis is Large THEN α Low, β High, γ Low (noise at an edge)", "EĞER Dev Büyük VE Dis Büyük İSE α Düşük, β Yüksek, γ Düşük (kenarda gürültü)")],
                     L("Hypotheses H1–H4 committed **before** the experiments (CP4)", "H1–H4 hipotezleri deneylerden **önce** kayda geçti (CP4)"),
                     L("Post-hoc variant 'split' (labelled exploratory): keep the paper's α, FIS only splits β : γ", "Sonradan eklenen 'split' varyantı (keşifsel etiketli): makalenin α'sı korunur, FIS yalnız β : γ'yı paylaştırır")],
         "image": f"results/figures/fis_inference_example{sfx}.png",
         "notes": L("Walk through the inference example: which rules fire, how the output set is built, three defuzzification results.",
                    "Çıkarım örneğini adım adım anlatın: hangi kurallar ateşleniyor, çıkış kümesi nasıl oluşuyor, üç durulaştırma sonucu.")},
        {"section": L("Contribution · iteration 1", "Katkı · iterasyon 1"), "title": L("Result: the first rule base did not improve accuracy (H1 rejected)", "Sonuç: ilk kural tabanı doğruluğu artırmadı (H1 reddedildi)"),
         "lead": L('The rules made the weighting interpretable but lowered the accuracy, strongly at high noise. We report this as it is and analyse the cause.', 'Kurallar ağırlıklandırmayı yorumlanabilir kıldı ama doğruluğu düşürdü, yüksek gürültüde belirgin biçimde. Bunu olduğu gibi raporluyor ve nedenini inceliyoruz.'),
         "table": {"columns": [L("Setting", "Ayar"), "FCM", L("paper coeff.", "makale kats."), "+FIS full (Δ)", "+FIS split (Δ)"], "rows": _e5_rows(),
                   "caption": L("ACC (%), mean of 10 seeds; Δ vs paper coefficients; * Wilcoxon p < 0.05", "ACC (%), 10 tohumun ortalaması; Δ makale katsayılarına göre; * Wilcoxon p < 0.05")},
         "callouts": [("~30 %", L("trust that FIS-full gives the noisy pixel", "FIS-full'ün gürültülü piksele verdiği güven"), "warn"),
                      ("~0.1 %", L("trust that the paper's formula gives it", "makalenin formülünün verdiği güven"))],
         "notes": L("Negative result reported honestly — the guideline says improvement is not required, but it must be analysed. The next slide shows the analysis.",
                    "Olumsuz sonuç dürüstçe raporlandı — yönerge iyileşmeyi zorunlu tutmuyor ama analiz edilmesini istiyor. Sonraki slayt analizi gösteriyor.")},
        {"section": L("Contribution · analysis", "Katkı · analiz"), "title": L("Why it failed — and what the variants show", "Neden başarısız oldu — varyantlar ne gösteriyor?"),
         "lead": L('The analysis points to two causes. Both shaped the second iteration.', 'Analiz iki nedene işaret ediyor. İkinci iterasyonu ikisi de belirledi.'),
         "bullets": [L("**Trust leak**: moderately deviating pixels fire 'Small/Medium deviation' rules; at 15 % almost half of the pixels are noisy", "**Güven sızıntısı**: orta sapmalı pikseller 'Küçük/Orta sapma' kurallarını ateşliyor; %15'te piksellerin neredeyse yarısı gürültülü"),
                     L("**Inputs confounded**: when ξ itself is noisy, Dis = |ξ − ϑ| is large although there is no edge", "**Girdiler karışıyor**: ξ'nin kendisi gürültülüyse kenar olmasa da Dis = |ξ − ϑ| büyük çıkıyor"),
                     L(f"Membership shape, bisector vs centroid, Mamdani vs Sugeno: ≤ {V['FV_full_maxdiff_nomom']} points (**H3, H4 hold**)", f"Üyelik şekli, açıortay–ağırlık merkezi, Mamdani–Sugeno: ≤ {V['FV_full_maxdiff_nomom']} puan (**H3, H4 tuttu**)"),
                     L("FIS-full is best on clean / 1 % noise, where trusting consistent pixels is right", "FIS-full temiz / %1 gürültüde en iyi: tutarlı piksellere güvenmek orada doğru"),
                     L("**What matters**: the trust left to the noisy pixel and σ — not the inference details", "**Önemli olan**: gürültülü piksele bırakılan güven ve σ — çıkarımın ayrıntıları değil")],
         "image": "results/figures/e5_robustness_acc.png",
         "notes": L("This diagnosis is the bridge to the second iteration: each candidate targets one of these causes.", "Bu teşhis ikinci iterasyona köprü: her aday bu nedenlerden birini hedefliyor.")},
        {"section": L("Contribution · iteration 2", "Katkı · iterasyon 2"), "title": L("Second iteration: a fuzzy reward factor (pre-registered)", "İkinci iterasyon: bulanık ödül katsayısı (önceden kayıtlı)"),
         "lead": L('Second attempt: instead of per-pixel coefficients, a small rule system sets the reward factor σ from the noise level of the whole image.', "İkinci deneme: piksel başına katsayılar yerine, küçük bir kural sistemi ödül katsayısı σ'yı tüm görüntünün gürültü düzeyine göre belirliyor."),
         "bullets": [L("Candidates: **A** bounded α (×0.002) · **B** impulse input Imp · **C** 3-rule Mamdani system: image noise → σ", "Adaylar: **A** sınırlı α (×0.002) · **B** dürtü girdisi Imp · **C** 3 kurallı Mamdani: görüntü gürültüsü → σ"),
                     [L("IF noise is Low THEN σ Small (0.3) · Medium → Medium (0.6) · High → Large (0.95)", "EĞER gürültü Düşük İSE σ Küçük (0.3) · Orta → Orta (0.6) · Yüksek → Büyük (0.95)")],
                     L(f"Tuned only on seeds 100–104; {V['E8_n_configs']} of 12 allowed configurations, all logged", f"Yalnız 100–104 tohumlarında ayarlandı; izin verilen 12 konfigürasyonun {V['E8_n_configs']}'u kullanıldı, hepsi kayıtlı"),
                     L("Selection rule, chosen variant and hypotheses H5/H6 **committed before** the single test run (CP6, git log)", "Seçim kuralı, seçilen varyant ve H5/H6 hipotezleri tek test koşusundan **önce commit'lendi** (CP6, git log)"),
                     L("Control: a fixed σ = 0.9 — does the rule add anything beyond a larger σ?", "Kontrol: sabit σ = 0.9 — kural, daha büyük bir σ'nın ötesinde bir şey katıyor mu?")],
         "image": f"results/figures/e8_sigma_fis{'_tr' if lang == 'tr' else ''}.png",
         "notes": L("Explain the protocol: tuning set separate from the test set, budget, pre-registration. Be open that the idea came from the C2 ablation on the test seeds — the test is blind to the parameters, not to the idea.",
                    "Protokolü anlatın: ayar kümesi test kümesinden ayrı, deneme bütçesi, ön kayıt. Fikrin test tohumlarındaki C2 ablasyonundan geldiğini açıkça söyleyin — test parametrelere kör, fikre değil.")},
        {"section": L("Contribution · iteration 2", "Katkı · iterasyon 2"), "title": L(f"Result: H5 {V['E8_H5']}, H6 {V['E8_H6']}", f"Sonuç: H5 {V['E8_H5']}, H6 {V['E8_H6']}"),
         "lead": L('Under identical conditions the fuzzy σ clearly improves the method at high noise and does not hurt it at low noise.', 'Aynı koşullarda bulanık σ yöntemi yüksek gürültüde belirgin biçimde iyileştiriyor, düşük gürültüde zarar vermiyor.'),
         "callouts": [(f"{V['E8_fs_gain10']} / {V['E8_fs_gain15']}", L("ACC points of FIS-σ over the paper at 10 / 15 % (p < 0.001)", "FIS-σ'nın makaleye göre %10 / %15'teki ACC kazancı (p < 0.001)")),
                      (V["E8_fs_worst_low"], L("largest loss at 1–5 % noise", "%1–5 gürültüde en büyük kayıp")),
                      (V["E8_fsa_worst"], L("worst difference of FIS-σ+A to the paper", "FIS-σ+A'nın makaleye göre en kötü farkı"))],
         "table": {"columns": [L("Setting", "Ayar"), "σ = 0.3", L("σ = 0.9 fixed", "σ = 0.9 sabit"), "FIS-σ (Δ)", "FIS-σ+A (Δ)"], "rows": _e8_rows(),
                   "caption": L("ACC (%), mean of seeds 0–9; Δ vs σ = 0.3; * Wilcoxon p < 0.05", "ACC (%), 0–9 tohumlarının ortalaması; Δ σ = 0.3'e göre; * Wilcoxon p < 0.05")},
         "notes": L(f"FIS-σ reaches {V['E8_fs_15_sy2']}/{V['E8_fs_15_sy3']} % at 15 % on sy2/sy3 (paper-reported {V['E8_reported_15_sy2']}/{V['E8_reported_15_sy3']} %: closer, still below; next slides). Honest part: a fixed σ = 0.9 is as good on mixed noise (differences {V['E8_fs_fixed_range']}); the rule's value is choosing σ automatically. FIS-σ+A is the first rule base made harmless and better at low noise.",
                    f"FIS-σ, %15'te sy2/sy3'te {V['E8_fs_15_sy2']}/{V['E8_fs_15_sy3']}'e ulaşıyor (makalede raporlanan {V['E8_reported_15_sy2']}/{V['E8_reported_15_sy3']}: daha yakın ama hâlâ altında; sonraki slayt). Dürüst kısım: karışık gürültüde sabit σ = 0.9 de aynı derecede iyi (farklar {V['E8_fs_fixed_range']}); kuralın değeri σ'yı otomatik seçmesi. FIS-σ+A, ilk kural tabanını zararsız ve düşük gürültüde daha iyi hâle getiriyor.")},
        {"section": L("Contribution · iteration 2", "Katkı · iterasyon 2"), "title": L("Beyond the test grid: noise types and real images", "Test ızgarasının ötesi: gürültü türleri ve gerçek görüntüler"),
         "lead": L('The gain carries over to real photographs and to other noise types, with two limitations of the noise estimate.', 'Kazanç gerçek fotoğraflara ve diğer gürültü türlerine de taşınıyor; gürültü tahmininin iki sınırlılığı var.'),
         "bullets": [L(f"BSDS500 gray: σ = 0.3 {V['E8_bsds_gray_paper']} → FIS-σ {V['E8_bsds_gray_fs']} % (fixed 0.9: {V['E8_bsds_gray_fixed']} %)",
                       f"BSDS500 gri: σ = 0.3 {V['E8_bsds_gray_paper']} → FIS-σ {V['E8_bsds_gray_fs']} (sabit 0.9: {V['E8_bsds_gray_fixed']})"),
                     L(f"BSDS500 colour: {V.get('E8_bsds_rgb_paper', '–')} → FIS-σ {V.get('E8_bsds_rgb_fs', '–')} % (paper-reported {V['E6_paper_ours_mean']} %)",
                       f"BSDS500 renkli: {V.get('E8_bsds_rgb_paper', '–')} → FIS-σ {V.get('E8_bsds_rgb_fs', '–')} (makalede {V['E6_paper_ours_mean']})"),
                     L(f"Noise types 0–20 %: FIS-σ vs fixed 0.9 within {V.get('E8_rob_fs_fixed_min', '–')} … {V.get('E8_rob_fs_fixed_max', '–')} points",
                       f"Gürültü türleri %0–20: FIS-σ ile sabit 0.9 farkı {V.get('E8_rob_fs_fixed_min', '–')} … {V.get('E8_rob_fs_fixed_max', '–')} puan"),
                     L("Limitation: the image noise estimate counts texture as noise (a textured photo at 5 % looks like sy2 at 10 %)", "Sınırlılık: görüntü gürültü tahmini dokuyu gürültü sayıyor (dokulu bir fotoğraf %5'te sy2'nin %10'u gibi görünüyor)"),
                     L("…and it does not see sparse impulses: salt-and-pepper 20 % → estimate 0, σ stays 0.3 (fixed 0.9 slightly better)", "…ve seyrek dürtüleri görmüyor: tuz-biber %20 → tahmin 0, σ 0.3'te kalıyor (sabit 0.9 biraz daha iyi)")],
         "image": f"results/figures/e8_robustness_acc{'_tr' if lang == 'tr' else ''}.png",
         "notes": L("Show that the gain carries over to the real images and to all noise types, and say clearly where the fixed σ = 0.9 is equally good.",
                    "Kazancın gerçek görüntülere ve tüm gürültü türlerine taşındığını gösterin; sabit σ = 0.9'un nerede aynı derecede iyi olduğunu açıkça söyleyin.")},
        {"section": L("Contribution · iteration 2", "Katkı · iterasyon 2"),
         "title": L("Against the paper's own numbers: closer, not better", "Makalenin kendi sayılarına göre: daha yakın, ama daha iyi değil"),
         "lead": L('Compared with the numbers printed in the paper, we are equal at low noise and closer, but still below, at high noise.', 'Makalede basılı sayılarla karşılaştırıldığında düşük gürültüde eşitiz, yüksek gürültüde daha yakınız ama hâlâ altındayız.'),
         "callouts": [(f"{V['E8_gap15_closed']} %", L("of the gap to [1] at 15 % closed (sy2/sy3)", "%15'te [1]'e olan farkın kapanan kısmı (sy2/sy3)")),
                      (V["E8_gap15_after"], L(f"points still below [1] at 15 % (was {V['E8_gap15_before']})", f"%15'te [1]'in hâlâ altında kalınan puan (önce {V['E8_gap15_before']})")),
                      (f"{V['E8_bsds_rgb_fs']} / {V['E6_paper_ours_mean']}", L("BSDS500 colour: FIS-σ / reported in [1]", "BSDS500 renkli: FIS-σ / [1]'de raporlanan"))],
         "table": {"columns": [L("Setting", "Ayar"), L("Reported [1]", "Makalede [1]"), L("σ = 0.3, ours (Δ)", "σ = 0.3, bizim (Δ)"), "FIS-σ (Δ)"],
                   "rows": _e8_reported_rows(),
                   "caption": L(f"ACC (%), mean of seeds 0–9; Δ = difference to the value reported in [1]. At 1–5 % FIS-σ is within {V['E8_rep_low_min']} … {V['E8_rep_low_max']} of [1] (agreement)",
                                f"ACC (%), 0–9 tohumlarının ortalaması; Δ = [1]'de raporlanan değere göre fark. %1–5'te FIS-σ [1]'den {V['E8_rep_low_min']} … {V['E8_rep_low_max']} farklı (uyum)")},
         "notes": L("Separate the two comparisons. Controlled (same code, same noise): FIS-σ beats the paper's settings at 10–15 % and never loses meaningfully. "
                    "Against the numbers printed in the paper (other implementation, other noise realizations, so indicative only): equal at low noise, "
                    f"still {V['E8_gap15_after']} points below at 15 % on sy2/sy3, down from {V['E8_gap15_before']}. Do not claim that we beat the paper.",
                    "İki karşılaştırmayı ayırın. Denetimli (aynı kod, aynı gürültü): FIS-σ %10–15'te makale ayarlarını geçiyor, hiçbir yerde anlamlı kaybı yok. "
                    "Makalede basılı sayılara göre (başka uygulama, başka gürültü örnekleri; yalnızca yol gösterici): düşük gürültüde eşit, %15'te sy2/sy3'te "
                    f"hâlâ {V['E8_gap15_after']} puan aşağıda (önce {V['E8_gap15_before']}). 'Makaleyi geçtik' demeyin.")},
        {"section": L("Real images", "Gerçek görüntüler"), "title": L("Real images: BSDS500 in gray and colour (5 % mixed noise)", "Gerçek görüntüler: gri ve renkli BSDS500 (%5 karışık gürültü)"),
         "lead": L("On natural photographs the method also clearly improves FCM. Running it on the colour images brings our numbers closer to the paper's.", "Doğal fotoğraflarda da yöntem FCM'yi belirgin biçimde iyileştiriyor. Renkli görüntülerde çalıştırmak sayılarımızı makaledekilere yaklaştırıyor."),
         "bullets": [L(f"Gray protocol: mean ACC FCM {V['E6_fcm_mean']} → method {V['E6_asr_mean']} % (paper: {V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']} %, colour)",
                       f"Gri protokol: ortalama ACC FCM {V['E6_fcm_mean']} → yöntem {V['E6_asr_mean']} (makale: {V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']}, renkli)"),
                     L(f"Iteration 1 rule bases: full {V['E6_full_mean']} %, split {V['E6_split_mean']} % → H2 rejected", f"İterasyon 1 kural tabanları: full {V['E6_full_mean']}, split {V['E6_split_mean']} → H2 reddedildi"),
                     L(f"Colour re-run: FCM {V['E6c_fcm_mean']} % (paper {V['E6_paper_fcm_mean']} %), method {V['E6c_asr_mean']} % (paper {V['E6_paper_ours_mean']} %)",
                       f"Renkli tekrar: FCM {V['E6c_fcm_mean']} (makale {V['E6_paper_fcm_mean']}), yöntem {V['E6c_asr_mean']} (makale {V['E6_paper_ours_mean']})")],
         "image": "results/figures/panel_bsds.png",
         "notes": L("Explain why we also ran the colour images: the paper's BSDS500 images are colour photographs; we use a multichannel version of the method (D-043).",
                    "Renkli görüntüleri neden ayrıca çalıştırdığımızı anlatın: makaledeki BSDS500 görüntüleri renkli fotoğraflar; yöntemin çok kanallı bir sürümünü kullanıyoruz (D-043).")},
        {"section": L("Discussion", "Tartışma"), "title": L("What the contribution adds — and its limits", "Katkının getirdikleri — ve sınırları"),
         "lead": L('The project followed a full cycle: reproduce, extend, fail, analyse and try again under a stricter protocol.', 'Proje tam bir döngü izledi: yeniden üret, geliştir, başarısız ol, analiz et ve daha sıkı bir protokolle yeniden dene.'),
         "bullets": [L("Process: iteration 1 failed (H1/H2 rejected) → failure analysed → diagnosis tested in a pre-registered iteration 2 → H5/H6 hold",
                       "Süreç: iterasyon 1 başarısız (H1/H2 reddedildi) → başarısızlık analiz edildi → teşhis önceden kayıtlı iterasyon 2'de sınandı → H5/H6 tuttu"),
                     L(f"Better than the paper's method under identical conditions; below the values reported in [1] at 10–15 % ({V['E8_gap15_after']} points at 15 %)",
                       f"Aynı koşullarda makalenin yönteminden iyi; %10–15'te [1]'de raporlanan değerlerin altında (%15'te {V['E8_gap15_after']} puan)"),
                     L("Limits: test images re-created from figures; 8 comparison methods not re-implemented; K must be known", "Sınırlar: test görüntüleri şekillerden yeniden üretildi; 8 karşılaştırma yöntemi yeniden yazılmadı; K bilinmeli"),
                     L("Iteration 2 tuned on the same images (other seeds); fixed σ = 0.9 equally good on mixed noise", "İterasyon 2 aynı görüntülerde (başka tohumlarla) ayarlandı; karışık gürültüde sabit σ = 0.9 de aynı derecede iyi"),
                     L("Next: a texture-robust noise estimate, per-pixel rules learned from data, automatic K", "Sonraki adımlar: dokuya dayanıklı gürültü tahmini, veriden öğrenilen piksel düzeyi kurallar, otomatik K")],
         "notes": L("Be clear about what was and was not done; the guideline values the analysis, not only the accuracy.", "Neyin yapılıp neyin yapılmadığını açıkça söyleyin; yönerge yalnız doğruluğu değil analizi de değerlendiriyor.")},
        {"section": L("Conclusion", "Sonuç"), "title": L("Conclusion", "Sonuç"),
         "lead": L('A fuzzy rule base helps most where the method leaves a parameter open: choosing σ from the image recovers most of the accuracy lost at high noise.', "Bulanık bir kural tabanı en çok, yöntemin açık bıraktığı bir parametrede işe yarıyor: σ'yı görüntüden seçmek yüksek gürültüde kaybedilen doğruluğun çoğunu geri kazandırıyor."),
         "bullets": [L("Faithful reproduction of FCM and of the method at low and medium noise", "FCM ve yöntem düşük ve orta gürültüde sadık biçimde yeniden üretildi"),
                     L("Iteration 1 (rules for α, β, γ): interpretable, but no accuracy gain — the cause was analysed",
                       "İterasyon 1 (α, β, γ için kurallar): yorumlanabilir ama doğruluk kazancı yok — nedeni analiz edildi"),
                     L(f"Iteration 2 (fuzzy σ): {V['E8_fs_gain10']} / {V['E8_fs_gain15']} ACC points at 10 / 15 % under identical conditions; as good as a well-chosen fixed σ",
                       f"İterasyon 2 (bulanık σ): aynı koşullarda %10 / %15'te {V['E8_fs_gain10']} / {V['E8_fs_gain15']} ACC puanı; iyi seçilmiş sabit bir σ kadar iyi"),
                     L(f"Still below the values reported in [1] at high noise ({V['E8_gap15_after']} points at 15 % on sy2/sy3)",
                       f"Yüksek gürültüde [1]'de raporlanan değerlerin hâlâ altında (%15'te sy2/sy3: {V['E8_gap15_after']} puan)"),
                     L("Code, data steps, results, decisions: github.com/tarikoztas/fuzzy-logic-project", "Kod, veri adımları, sonuçlar, kararlar: github.com/tarikoztas/fuzzy-logic-project")],
         "notes": L("Summarise in one sentence: a small rule system that sets σ from the image recovers most of the accuracy lost at high noise. Thank the audience and invite questions.",
                    "Tek cümleyle özetleyin: σ'yı görüntüden seçen küçük bir kural sistemi yüksek gürültüde kaybedilen doğruluğun çoğunu geri kazandırıyor. Teşekkür edin ve soruları davet edin.")},
    ]
