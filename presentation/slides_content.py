"""Slide specification (15-20 min talk) in English and Turkish. Numbers come from
report/report_values.py (CSV-based), so both languages show identical values.

Guideline Sec. 4 coverage: problem & motivation (2), literature (3), fuzzy-logic background (4),
method & architecture incl. inputs/outputs, membership functions, rules, inference, defuzzification
(5-9), experiments & data (10), paper's results (11), critical evaluation (14, 22), our implementation
and contribution with comparative results (12-13, 15-21), demo (23).
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
         "notes": L("Introduce yourself and the paper. Say what you will show: re-implementation, reproduction, findings about the paper, two iterations of a fuzzy-rule extension, and an honest evaluation.",
                    "Kendinizi ve makaleyi tanıtın. Neleri göstereceğinizi söyleyin: yeniden gerçekleştirme, yeniden üretim, makaleyle ilgili bulgular, bulanık kural tabanlı geliştirmenin iki iterasyonu ve dürüst bir değerlendirme.")},
        {"section": L("Problem", "Problem"), "title": L("Why noisy image segmentation is hard for FCM", "Gürültülü görüntü bölütleme FCM için neden zor?"),
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
         "bullets": [L("Input: noisy gray image y ∈ [0, 1], number of clusters K", "Girdi: gürültülü gri görüntü y ∈ [0, 1], küme sayısı K"),
                     L("ξ: local estimate (reward/penalty sets)", "ξ: yerel kestirim (ödül/ceza kümeleri)"), L("ϑ: non-local estimate in the DTCWT domain", "ϑ: DTCWT alanında yerel-olmayan kestirim"),
                     L("α, β, γ: per-pixel trust in y, ξ, ϑ", "α, β, γ: y, ξ, ϑ'ya piksel başına güven"), L("Sparse FCM: d = α(y−c)² + β(ξ−c)² + γ(ϑ−c)²", "Seyrek FCM: d = α(y−c)² + β(ξ−c)² + γ(ϑ−c)²"),
                     L("Output: U (K×N), centres, label = argmax U", "Çıktı: U (K×N), merkezler, etiket = argmax U")],
         "image": f"results/figures/architecture{sfx}.png", "narrow_text": True,
         "notes": L("Walk through the pipeline left to right. Orange box = first iteration of our contribution; the second iteration acts on σ inside the ξ box.",
                    "Akışı soldan sağa anlatın. Turuncu kutu = katkımızın ilk iterasyonu; ikinci iterasyon ξ kutusunun içindeki σ'ya etki ediyor.")},
        {"section": L("Reference method", "Referans yöntem"), "title": L("Local information ξ: golden-ratio reward and penalty sets", "Yerel bilgi ξ: altın oranlı ödül ve ceza kümeleri"),
         "bullets": [L("Sort the neighbours in the w×w window by gray value", "w×w penceredeki komşuları gri değere göre sırala"),
                     L("Middle ⌊0.618·(N_R−1)⌋ → **reward set** (weight 1+σ), ends → **penalty set** (1−σ)", "Ortadaki ⌊0.618·(N_R−1)⌋ → **ödül kümesi** (ağırlık 1+σ), uçlar → **ceza kümesi** (1−σ)"),
                     [L("Fig. 1 of the paper: reward {169, 172, 174, 176}, penalty {103, 137, 194, 212} — reproduced exactly", "Makalenin Şekil 1'i: ödül {169, 172, 174, 176}, ceza {103, 137, 194, 212} — birebir yeniden üretildi")],
                     L("Weight = (1±σ) · exp(−Δgray²/τ²) · exp(−distance); ξ = weighted mean", "Ağırlık = (1±σ) · exp(−Δgri²/τ²) · exp(−uzaklık); ξ = ağırlıklı ortalama"),
                     L("**σ** = how strongly the extremes are down-weighted → key parameter of our second iteration", "**σ** = uçların ne kadar bastırılacağı → ikinci iterasyonumuzun anahtar parametresi")],
         "callouts": [("σ = 0.3", L("paper's value", "makalenin değeri")), ("σ ≈ 0.9", L("implied by the paper's own worked example", "makalenin kendi örneğinin ima ettiği"), "warn")],
         "notes": L("Analogy: a jury that down-weights, but does not delete, the most extreme scores. Text says ceil, the figure shows floor — we use floor (D-014).",
                    "Benzetme: en uç puanları silmeyen ama ağırlığını düşüren bir jüri. Metin yukarı yuvarlama diyor, şekil aşağı yuvarlama gösteriyor — biz aşağıyı kullanıyoruz (D-014).")},
        {"section": L("Reference method", "Referans yöntem"), "title": L("Non-local information ϑ in the wavelet domain", "Dalgacık alanında yerel-olmayan bilgi ϑ"),
         "bullets": [L("DTCWT: 1 low-pass + 6 complex direction sub-bands (±15°, ±45°, ±75°), near shift-invariant", "DTCWT: 1 alçak geçiren + 6 karmaşık yön alt bandı (±15°, ±45°, ±75°), kaymaya neredeyse duyarsız"),
                     L("Non-local means on all 7 sub-bands: 15×15 search window, 5×5 patches, h² = g·w² = 250", "7 alt bandın hepsinde yerel-olmayan ortalama: 15×15 arama penceresi, 5×5 yama, h² = g·w² = 250"),
                     L("Inverse DTCWT → ϑ", "Ters DTCWT → ϑ"),
                     L("**Finding (D-038)**: in [0, 1] units every NLM weight lies in [0.996, 1] → it acts like a 15×15 mean filter; edge preservation comes from the wavelets",
                       "**Bulgu (D-038)**: [0, 1] biriminde her NLM ağırlığı [0.996, 1] aralığında → 15×15 ortalama filtresi gibi davranıyor; kenar koruma dalgacıklardan geliyor")],
         "notes": L("Explain DTCWT with the analogy of splitting a song into bass/mid/treble channels. Then the finding: the patch-similarity part is practically inactive with the published parameters.",
                    "DTCWT'yi bir şarkıyı bas/orta/tiz kanallarına ayırma benzetmesiyle anlatın. Ardından bulgu: yayımlanan parametrelerle yama benzerliği kısmı pratikte devre dışı.")},
        {"section": L("Reference method", "Referans yöntem"), "title": L("Adaptive coefficients and sparse-regularised FCM", "Uyarlamalı katsayılar ve seyrek düzenlileştirilmiş FCM"),
         "bullets": [L("ΔG1 = k·exp(y − ξ), ΔG2 = k·exp(y − ϑ);  α = 1/(ΔG1+ΔG2), β = ΔG1, γ = ΔG2", "ΔG1 = k·exp(y − ξ), ΔG2 = k·exp(y − ϑ);  α = 1/(ΔG1+ΔG2), β = ΔG1, γ = ΔG2"),
                     [L("k = 15 → α ≈ 0.01–0.1, β ≈ γ ≈ 5–40: the original pixel gets ~0.1 % of the trust", "k = 15 → α ≈ 0.01–0.1, β ≈ γ ≈ 5–40: özgün piksel güvenin ~%0.1'ini alıyor")],
                     L("Objective J = Σ u^m d + δ‖U‖₀; per iteration: centres → η → hard threshold √δ → normalise", "Amaç J = Σ u^m d + δ‖U‖₀; her iterasyonda: merkezler → η → sert eşik √δ → normalize"),
                     L("√0.4 = 0.63 > 0.5 → at most one membership per pixel survives (D-011r)", "√0.4 = 0.63 > 0.5 → piksel başına en fazla bir üyelik kalıyor (D-011r)"),
                     L("Parameters: w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4, m=2", "Parametreler: w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4, m=2")],
         "notes": L("Emphasise the scale of the coefficients — it becomes important for our extension.", "Katsayıların ölçeğini vurgulayın — geliştirmemiz için önemli hâle geliyor.")},
        {"section": L("Fuzzy system", "Bulanık sistem"), "title": L("The fuzzy systems of the project at a glance", "Projedeki bulanık sistemler bir bakışta"),
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
         "callouts": [("79.58 → 99.23", L("mean ACC (%) on the synthetic images, FCM → method (Tables 2–8)", "sentetik görüntülerde ortalama ACC (%), FCM → yöntem (Tablo 2–8)")),
                      (f"{V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']}", L("mean ACC (%) on BSDS500 (Table 9)", "BSDS500'de ortalama ACC (%) (Tablo 9)"))],
         "bullets": [L("Ablation (Table 1): non-local term most effective; all three components best", "Ablasyon (Tablo 1): en etkili bileşen yerel-olmayan terim; üçü birlikte en iyi"),
                     L("Fewer iterations thanks to sparsity; best or near-best against 8 methods", "Seyreklik sayesinde daha az iterasyon; 8 yönteme karşı en iyi ya da en iyiye yakın")],
         "notes": L("These are paper-reported numbers (labelled as such everywhere).", "Bunlar makalede raporlanan sayılar (her yerde böyle etiketli).")},
        {"section": L("Reproduction", "Yeniden üretim"), "title": L("Our reproduction vs. the paper (synthetic images)", "Yeniden üretimimiz ve makale (sentetik görüntüler)"),
         "table": {"columns": [L("Setting", "Ayar"), L("FCM ours / paper", "FCM bizim / makale"), L("Method ours / paper", "Yöntem bizim / makale")], "rows": _e2_rows(),
                   "caption": L("ACC (%), mean of 10 seeds vs paper-reported", "ACC (%), 10 tohumun ortalaması ve makalede raporlanan")},
         "image": "results/figures/e2_asrfcm_vs_paper_compact.png",
         "bullets": [L(f"FCM: mean |Δ| = {V['E1_acc_mad']} ACC points", f"FCM: ortalama |Δ| = {V['E1_acc_mad']} ACC puanı"),
                     L(f"Method: {V['E2_acc_mad_low']} points up to 5 %, {V['E2_acc_mad_high']} at 10–15 %", f"Yöntem: %5'e kadar {V['E2_acc_mad_low']} puan, %10–15'te {V['E2_acc_mad_high']} puan")],
         "notes": L("FCM agreement validates images and noise. The method matches at low noise; at high noise on 3-class images it is lower — explained on the next slides.",
                    "FCM uyumu görüntüleri ve gürültüyü doğruluyor. Yöntem düşük gürültüde tutuyor; üç sınıflı görüntülerde yüksek gürültüde daha düşük — sonraki slaytlarda açıklanıyor.")},
        {"section": L("Reproduction", "Yeniden üretim"), "title": L("Ablation and sensitivity", "Ablasyon ve duyarlılık"),
         "bullets": [L(f"All three components: ACC {V['E3_full_acc']} % (sy1/sy2/sy3); non-local alone {V['E3_nl_only']} %", f"Üç bileşen birlikte: ACC {V['E3_full_acc']} (sy1/sy2/sy3); yalnız yerel-olmayan {V['E3_nl_only']}"),
                     L(f"Local alone is strong in our runs ({V['E3_local_only']} %), paper: 82.26 %", f"Yalnız yerel terim bizde güçlü ({V['E3_local_only']}), makale: %82.26"),
                     L("Sensitivity at 5 %: σ, w, δ change ACC by < 0.4 points; k = 1 degrades; δ mainly controls the iterations", "%5'te duyarlılık: σ, w, δ ACC'yi < 0.4 puan değiştiriyor; k = 1 bozuyor; δ esas olarak iterasyonu belirliyor"),
                     L(f"**σ = 0.9** closes most of the high-noise gap (sy2/sy3 at 15 %: gap {V['C2_sigma_gap']} points)", f"**σ = 0.9** yüksek gürültü farkının çoğunu kapatıyor (sy2/sy3, %15: fark {V['C2_sigma_gap']} puana)")],
         "image": "results/figures/e3_ablation.png",
         "notes": L("The reward factor is the key under-determined quantity; the paper's own worked example corresponds to σ ≈ 0.9. Remember this — it drives the second iteration.",
                    "Ödül katsayısı belirsiz bırakılmış en önemli büyüklük; makalenin kendi örneği σ ≈ 0.9'a karşılık geliyor. Bunu akılda tutun — ikinci iterasyonu yönlendiren bu.")},
        {"section": L("Critical evaluation", "Eleştirel değerlendirme"), "title": L("Six inconsistencies we found in the paper", "Makalede bulduğumuz altı tutarsızlık"),
         "bullets": [L("**Kappa is a rescaled ACC**: p_e = 5/9 in every 3-class cell → Kappa = (ACC − 5/9)/(4/9)", "**Kappa, ölçeklenmiş ACC**: üç sınıflı her hücrede p_e = 5/9 → Kappa = (ACC − 5/9)/(4/9)"),
                     L("**Figs. 2–3** weights ⇒ σ ≈ 0.9, not 0.3; they do not follow Eq. 6", "**Şekil 2–3** ağırlıkları ⇒ σ ≈ 0.9, 0.3 değil; Denk. 6'ya uymuyor"),
                     L("**NLM ≈ mean filter** with the published parameters (weights 0.996–1)", "**NLM ≈ ortalama filtresi** yayımlanan parametrelerle (ağırlıklar 0.996–1)"),
                     L("**δ = 0.4**: at most one membership survives; reported V_PC needs the 'keep' policy", "**δ = 0.4**: en fazla bir üyelik kalıyor; raporlanan V_PC 'keep' politikasını gerektiriyor"),
                     L("**Table 1** 'no component' row ≠ the paper's own FCM results", "**Tablo 1** 'bileşen yok' satırı ≠ makalenin kendi FCM sonuçları"),
                     L("**BSDS500 is colour**: FCM on RGB reproduces the reported FCM within 1 point (7/8 images)", "**BSDS500 renkli**: RGB üzerinde FCM, raporlanan FCM'yi 1 puan içinde veriyor (8 görüntünün 7'si)")],
         "notes": L("Each finding has evidence in report/decisions.md (D-031, D-032, D-038, D-011r, D-040, D-042). This is the critical-evaluation part of the guideline.",
                    "Her bulgunun kanıtı report/decisions.md'de (D-031, D-032, D-038, D-011r, D-040, D-042). Yönergenin eleştirel değerlendirme kısmı budur.")},
        {"section": L("Contribution · iteration 1", "Katkı · iterasyon 1"), "title": L("A Mamdani rule base for α, β, γ", "α, β, γ için Mamdani kural tabanı"),
         "bullets": [L("Why: the closed form gives β ≈ γ everywhere, but ξ and ϑ fail in different places", "Neden: kapalı formül her yerde β ≈ γ veriyor, oysa ξ ve ϑ farklı yerlerde başarısız oluyor"),
                     L("Inputs Dev (pixel vs. consensus) and Dis (disagreement ≈ edge); 9 rules, e.g.", "Girdiler Dev (piksel ile uzlaşı farkı) ve Dis (anlaşmazlık ≈ kenar); 9 kural, ör."),
                     [L("IF Dev is Large AND Dis is Small THEN α Low, β High, γ High (noise in a flat region)", "EĞER Dev Büyük VE Dis Küçük İSE α Düşük, β Yüksek, γ Yüksek (düz bölgede gürültü)"),
                      L("IF Dev is Large AND Dis is Large THEN α Low, β High, γ Low (noise at an edge)", "EĞER Dev Büyük VE Dis Büyük İSE α Düşük, β Yüksek, γ Düşük (kenarda gürültü)")],
                     L("Hypotheses H1–H4 committed **before** the experiments (CP4)", "H1–H4 hipotezleri deneylerden **önce** kayda geçti (CP4)"),
                     L("Post-hoc variant 'split' (labelled exploratory): keep the paper's α, FIS only splits β : γ", "Sonradan eklenen 'split' varyantı (keşifsel etiketli): makalenin α'sı korunur, FIS yalnız β : γ'yı paylaştırır")],
         "image": f"results/figures/fis_inference_example{sfx}.png",
         "notes": L("Walk through the inference example: which rules fire, how the output set is built, three defuzzification results.",
                    "Çıkarım örneğini adım adım anlatın: hangi kurallar ateşleniyor, çıkış kümesi nasıl oluşuyor, üç durulaştırma sonucu.")},
        {"section": L("Contribution · iteration 1", "Katkı · iterasyon 1"), "title": L("Result: the first rule base did not improve accuracy (H1 rejected)", "Sonuç: ilk kural tabanı doğruluğu artırmadı (H1 reddedildi)"),
         "table": {"columns": [L("Setting", "Ayar"), "FCM", L("paper coeff.", "makale kats."), "+FIS full (Δ)", "+FIS split (Δ)"], "rows": _e5_rows(),
                   "caption": L("ACC (%), mean of 10 seeds; Δ vs paper coefficients; * Wilcoxon p < 0.05", "ACC (%), 10 tohumun ortalaması; Δ makale katsayılarına göre; * Wilcoxon p < 0.05")},
         "callouts": [("~30 %", L("trust that FIS-full gives the noisy pixel", "FIS-full'ün gürültülü piksele verdiği güven"), "warn"),
                      ("~0.1 %", L("trust that the paper's formula gives it", "makalenin formülünün verdiği güven"))],
         "notes": L("Negative result reported honestly — the guideline says improvement is not required, but it must be analysed. The next slide shows the analysis.",
                    "Olumsuz sonuç dürüstçe raporlandı — yönerge iyileşmeyi zorunlu tutmuyor ama analiz edilmesini istiyor. Sonraki slayt analizi gösteriyor.")},
        {"section": L("Contribution · analysis", "Katkı · analiz"), "title": L("Why it failed — and what the variants show", "Neden başarısız oldu — varyantlar ne gösteriyor?"),
         "bullets": [L("**Trust leak**: moderately deviating pixels fire 'Small/Medium deviation' rules; at 15 % almost half of the pixels are noisy", "**Güven sızıntısı**: orta sapmalı pikseller 'Küçük/Orta sapma' kurallarını ateşliyor; %15'te piksellerin neredeyse yarısı gürültülü"),
                     L("**Inputs confounded**: when ξ itself is noisy, Dis = |ξ − ϑ| is large although there is no edge", "**Girdiler karışıyor**: ξ'nin kendisi gürültülüyse kenar olmasa da Dis = |ξ − ϑ| büyük çıkıyor"),
                     L(f"Membership shape, bisector vs centroid, Mamdani vs Sugeno: ≤ {V['FV_full_maxdiff_nomom']} points (**H3, H4 hold**)", f"Üyelik şekli, açıortay–ağırlık merkezi, Mamdani–Sugeno: ≤ {V['FV_full_maxdiff_nomom']} puan (**H3, H4 tuttu**)"),
                     L("FIS-full is best on clean / 1 % noise, where trusting consistent pixels is right", "FIS-full temiz / %1 gürültüde en iyi: tutarlı piksellere güvenmek orada doğru"),
                     L("**What matters**: the trust left to the noisy pixel and σ — not the inference details", "**Önemli olan**: gürültülü piksele bırakılan güven ve σ — çıkarımın ayrıntıları değil")],
         "image": "results/figures/e5_robustness_acc.png",
         "notes": L("This diagnosis is the bridge to the second iteration: each candidate targets one of these causes.", "Bu teşhis ikinci iterasyona köprü: her aday bu nedenlerden birini hedefliyor.")},
        {"section": L("Contribution · iteration 2", "Katkı · iterasyon 2"), "title": L("Second iteration: a fuzzy reward factor (pre-registered)", "İkinci iterasyon: bulanık ödül katsayısı (önceden kayıtlı)"),
         "bullets": [L("Candidates: **A** bounded α (×0.002) · **B** impulse input Imp · **C** 3-rule Mamdani system: image noise → σ", "Adaylar: **A** sınırlı α (×0.002) · **B** dürtü girdisi Imp · **C** 3 kurallı Mamdani: görüntü gürültüsü → σ"),
                     [L("IF noise is Low THEN σ Small (0.3) · Medium → Medium (0.6) · High → Large (0.95)", "EĞER gürültü Düşük İSE σ Küçük (0.3) · Orta → Orta (0.6) · Yüksek → Büyük (0.95)")],
                     L(f"Tuned only on seeds 100–104; {V['E8_n_configs']} of 12 allowed configurations, all logged", f"Yalnız 100–104 tohumlarında ayarlandı; izin verilen 12 konfigürasyonun {V['E8_n_configs']}'u kullanıldı, hepsi kayıtlı"),
                     L("Selection rule, chosen variant and hypotheses H5/H6 **committed before** the single test run (CP6, git log)", "Seçim kuralı, seçilen varyant ve H5/H6 hipotezleri tek test koşusundan **önce commit'lendi** (CP6, git log)"),
                     L("Control: a fixed σ = 0.9 — does the rule add anything beyond a larger σ?", "Kontrol: sabit σ = 0.9 — kural, daha büyük bir σ'nın ötesinde bir şey katıyor mu?")],
         "image": f"results/figures/e8_sigma_fis{'_tr' if lang == 'tr' else ''}.png",
         "notes": L("Explain the protocol: tuning set separate from the test set, budget, pre-registration. Be open that the idea came from the C2 ablation on the test seeds — the test is blind to the parameters, not to the idea.",
                    "Protokolü anlatın: ayar kümesi test kümesinden ayrı, deneme bütçesi, ön kayıt. Fikrin test tohumlarındaki C2 ablasyonundan geldiğini açıkça söyleyin — test parametrelere kör, fikre değil.")},
        {"section": L("Contribution · iteration 2", "Katkı · iterasyon 2"), "title": L(f"Result: H5 {V['E8_H5']}, H6 {V['E8_H6']}", f"Sonuç: H5 {V['E8_H5']}, H6 {V['E8_H6']}"),
         "callouts": [(f"{V['E8_fs_gain10']} / {V['E8_fs_gain15']}", L("ACC points of FIS-σ over the paper at 10 / 15 % (p < 0.001)", "FIS-σ'nın makaleye göre %10 / %15'teki ACC kazancı (p < 0.001)")),
                      (V["E8_fs_worst_low"], L("largest loss at 1–5 % noise", "%1–5 gürültüde en büyük kayıp")),
                      (V["E8_fsa_worst"], L("worst difference of FIS-σ+A to the paper", "FIS-σ+A'nın makaleye göre en kötü farkı"))],
         "table": {"columns": [L("Setting", "Ayar"), "σ = 0.3", L("σ = 0.9 fixed", "σ = 0.9 sabit"), "FIS-σ (Δ)", "FIS-σ+A (Δ)"], "rows": _e8_rows(),
                   "caption": L("ACC (%), mean of seeds 0–9; Δ vs σ = 0.3; * Wilcoxon p < 0.05", "ACC (%), 0–9 tohumlarının ortalaması; Δ σ = 0.3'e göre; * Wilcoxon p < 0.05")},
         "notes": L(f"FIS-σ reaches {V['E8_fs_15_sy2']}/{V['E8_fs_15_sy3']} % at 15 % on sy2/sy3, close to the paper-reported {V['E8_reported_15_sy2']}/{V['E8_reported_15_sy3']} %. Honest part: a fixed σ = 0.9 is as good on mixed noise (differences {V['E8_fs_fixed_range']}); the rule's value is choosing σ automatically. FIS-σ+A is the first rule base made harmless and better at low noise.",
                    f"FIS-σ, %15'te sy2/sy3'te {V['E8_fs_15_sy2']}/{V['E8_fs_15_sy3']}'e ulaşıyor; makalede raporlanan {V['E8_reported_15_sy2']}/{V['E8_reported_15_sy3']}'e yakın. Dürüst kısım: karışık gürültüde sabit σ = 0.9 de aynı derecede iyi (farklar {V['E8_fs_fixed_range']}); kuralın değeri σ'yı otomatik seçmesi. FIS-σ+A, ilk kural tabanını zararsız ve düşük gürültüde daha iyi hâle getiriyor.")},
        {"section": L("Contribution · iteration 2", "Katkı · iterasyon 2"), "title": L("Beyond the test grid: noise types and real images", "Test ızgarasının ötesi: gürültü türleri ve gerçek görüntüler"),
         "bullets": [L(f"BSDS500 gray: σ = 0.3 {V['E8_bsds_gray_paper']} → FIS-σ {V['E8_bsds_gray_fs']} % (fixed 0.9: {V['E8_bsds_gray_fixed']} %)",
                       f"BSDS500 gri: σ = 0.3 {V['E8_bsds_gray_paper']} → FIS-σ {V['E8_bsds_gray_fs']} (sabit 0.9: {V['E8_bsds_gray_fixed']})"),
                     L(f"BSDS500 colour: {V.get('E8_bsds_rgb_paper', '–')} → FIS-σ {V.get('E8_bsds_rgb_fs', '–')} % (paper-reported {V['E6_paper_ours_mean']} %)",
                       f"BSDS500 renkli: {V.get('E8_bsds_rgb_paper', '–')} → FIS-σ {V.get('E8_bsds_rgb_fs', '–')} (makalede {V['E6_paper_ours_mean']})"),
                     L(f"Noise types 0–20 %: FIS-σ vs fixed 0.9 within {V.get('E8_rob_fs_fixed_min', '–')} … {V.get('E8_rob_fs_fixed_max', '–')} points",
                       f"Gürültü türleri %0–20: FIS-σ ile sabit 0.9 farkı {V.get('E8_rob_fs_fixed_min', '–')} … {V.get('E8_rob_fs_fixed_max', '–')} puan"),
                     L("Limitation: the image noise estimate counts texture as noise (a textured photo at 5 % looks like sy2 at 10 %)", "Sınırlılık: görüntü gürültü tahmini dokuyu gürültü sayıyor (dokulu bir fotoğraf %5'te sy2'nin %10'u gibi görünüyor)")],
         "image": f"results/figures/e8_robustness_acc{'_tr' if lang == 'tr' else ''}.png",
         "notes": L("Show that the gain carries over to the real images and to all noise types, and say clearly where the fixed σ = 0.9 is equally good.",
                    "Kazancın gerçek görüntülere ve tüm gürültü türlerine taşındığını gösterin; sabit σ = 0.9'un nerede aynı derecede iyi olduğunu açıkça söyleyin.")},
        {"section": L("Real images", "Gerçek görüntüler"), "title": L("BSDS500 (5 % mixed noise) and the colour finding", "BSDS500 (%5 karışık gürültü) ve renk bulgusu"),
         "bullets": [L(f"Gray protocol: mean ACC FCM {V['E6_fcm_mean']} → method {V['E6_asr_mean']} % (paper: {V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']} %, colour)",
                       f"Gri protokol: ortalama ACC FCM {V['E6_fcm_mean']} → yöntem {V['E6_asr_mean']} (makale: {V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']}, renkli)"),
                     L(f"Iteration 1 rule bases: full {V['E6_full_mean']} %, split {V['E6_split_mean']} % → H2 rejected", f"İterasyon 1 kural tabanları: full {V['E6_full_mean']}, split {V['E6_split_mean']} → H2 reddedildi"),
                     L(f"Colour re-run: FCM {V['E6c_fcm_mean']} % (paper {V['E6_paper_fcm_mean']} %), method {V['E6c_asr_mean']} % (paper {V['E6_paper_ours_mean']} %)",
                       f"Renkli tekrar: FCM {V['E6c_fcm_mean']} (makale {V['E6_paper_fcm_mean']}), yöntem {V['E6c_asr_mean']} (makale {V['E6_paper_ours_mean']})")],
         "image": "results/figures/panel_bsds.png",
         "notes": L("Explain the colour finding (D-042) and the multichannel generalisation (D-043).", "Renk bulgusunu (D-042) ve çok kanallı genellemeyi (D-043) açıklayın.")},
        {"section": L("Discussion", "Tartışma"), "title": L("What the contribution adds — and its limits", "Katkının getirdikleri — ve sınırları"),
         "bullets": [L("Covers the guideline's contribution types: new inputs/outputs, MF shapes, defuzzification, Mamdani vs Sugeno, rule-base change, new scenario (colour), robustness, ablation, cost",
                       "Yönergedeki katkı türlerini kapsıyor: yeni girdi/çıktılar, üyelik şekilleri, durulaştırma, Mamdani–Sugeno, kural tabanı değişikliği, yeni senaryo (renkli), dayanıklılık, ablasyon, maliyet"),
                     L("Negative first result analysed → diagnosis tested in a pre-registered second iteration → H5/H6 hold", "Olumsuz ilk sonuç analiz edildi → teşhis önceden kayıtlı ikinci iterasyonda sınandı → H5/H6 tuttu"),
                     L("Limits: test images re-created from figures; 8 comparison methods not re-implemented; K must be known", "Sınırlar: test görüntüleri şekillerden yeniden üretildi; 8 karşılaştırma yöntemi yeniden yazılmadı; K bilinmeli"),
                     L("Iteration 2 tuned on the same images (other seeds); fixed σ = 0.9 equally good on mixed noise", "İterasyon 2 aynı görüntülerde (başka tohumlarla) ayarlandı; karışık gürültüde sabit σ = 0.9 de aynı derecede iyi"),
                     L("Next: a texture-robust noise estimate, per-pixel rules learned from data, automatic K", "Sonraki adımlar: dokuya dayanıklı gürültü tahmini, veriden öğrenilen piksel düzeyi kurallar, otomatik K")],
         "notes": L("Be clear about what was and was not done; the guideline values the analysis, not only the accuracy.", "Neyin yapılıp neyin yapılmadığını açıkça söyleyin; yönerge yalnız doğruluğu değil analizi de değerlendiriyor.")},
        {"section": L("Demo", "Demo"), "title": L("Live demo and conclusion", "Canlı demo ve sonuç"),
         "bullets": [L("python demo/demo.py --image sy3 --noise salt_pepper --level 20 --pixel 120 80", "python demo/demo.py --image sy3 --noise salt_pepper --level 20 --pixel 120 80"),
                     L("FCM, the method, both rule-base iterations side by side; σ rule firing for the image and α, β, γ rules for one pixel (offline, ≈ 20 s)",
                       "FCM, yöntem ve iki kural tabanı iterasyonu yan yana; görüntü için σ kurallarının, bir piksel için α, β, γ kurallarının ateşlenmesi (çevrimdışı, ≈ 20 s)"),
                     L("Conclusion: faithful reproduction at low/medium noise; six documented inconsistencies; a fuzzy reward factor closes most of the high-noise gap",
                       "Sonuç: düşük/orta gürültüde sadık yeniden üretim; belgelenmiş altı tutarsızlık; bulanık ödül katsayısı yüksek gürültü farkının çoğunu kapatıyor"),
                     L("Code, data steps, results, decisions: github.com/tarikoztas/fuzzy-logic-project", "Kod, veri adımları, sonuçlar, kararlar: github.com/tarikoztas/fuzzy-logic-project")],
         "notes": L("Run the demo with a different noise type than in the report; backup: results/figures/demo_panel.png.",
                    "Demoyu rapordakinden farklı bir gürültü türüyle çalıştırın; yedek: results/figures/demo_panel.png.")},
    ]
