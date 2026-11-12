# References

**Verification rule.** An entry is listed as `[V]` only after its DOI was resolved on Crossref and title, authors, year and venue matched. The raw Crossref responses are stored in `verification/crossref_2026-11-10.jsonl` and can be regenerated with:

```bash
python -X utf8 references/verification/verify_doi.py references/verification/dois.txt
```

`[V-abs]` = metadata verified **and** the abstract was read (summary below is based on the abstract).
`[V-meta]` = metadata verified, abstract **not** accessible to us (publisher page blocked) → may be cited only as a pointer, not for claims about its method, until the student reads it via university access.

Re-check (2026-11-12): all 38 DOIs in `verification/dois.txt` resolve on Crossref (`verification/crossref_recheck_2026-11-12.jsonl`); titles match the entries below except for HTML markup in two Crossref titles ([17], [19]: `<i>C</i>`); two DOIs in `dois.txt` (10.1016/j.sigpro.2024.109515, 10.1016/j.patcog.2022.108686) were candidates screened in Faz 1 and are not listed or cited.

Format: IEEE. Local PDFs live in `references/papers/` and are **not** committed (publisher copyright).

---

## A. Reference paper

[1] [V] J. Wu, X. Wang, Y. Liu, and C. Fang, "Adaptive sparse regularized fuzzy clustering noise image segmentation algorithm based on complementary spatial information," *Expert Syst. Appl.*, vol. 256, Art. no. 124943, 2024, doi: 10.1016/j.eswa.2024.124943.

## B. Foundations

[2] [V] J. C. Bezdek, R. Ehrlich, and W. Full, "FCM: The fuzzy c-means clustering algorithm," *Comput. Geosci.*, vol. 10, no. 2–3, pp. 191–203, 1984, doi: 10.1016/0098-3004(84)90020-7. *(not in [1]'s bibliography; standard FCM citation)*

[3] [V] M. P. Windham, "Cluster validity for the fuzzy c-means clustering algorithm," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. PAMI-4, no. 4, pp. 357–363, 1982, doi: 10.1109/TPAMI.1982.4767266. *(cited by [1] for FCM)*

[4] [V] N. Kingsbury, "Complex wavelets for shift invariant analysis and filtering of signals," *Appl. Comput. Harmon. Anal.*, vol. 10, no. 3, pp. 234–253, 2001, doi: 10.1006/acha.2000.0343. *(DTCWT)*

[5] [V] A. Buades, B. Coll, and J.-M. Morel, "Nonlocal image and movie denoising," *Int. J. Comput. Vis.*, vol. 76, no. 2, pp. 123–139, 2008, doi: 10.1007/s11263-007-0052-1. *(non-local means)*

[6] [V] L. Vincent, "Morphological grayscale reconstruction in image analysis: Applications and efficient algorithms," *IEEE Trans. Image Process.*, vol. 2, no. 2, pp. 176–201, 1993, doi: 10.1109/83.217222. *(used by FRFCM/SRFCM)*

[7] [V] P. Arbeláez, M. Maire, C. Fowlkes, and J. Malik, "Contour detection and hierarchical image segmentation," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 33, no. 5, pp. 898–916, 2011, doi: 10.1109/TPAMI.2010.161. *(BSDS500 dataset)*

## C. FCM variants for noisy image segmentation (from [1]'s bibliography)

Method descriptions below follow how [1] describes them (§1 and §4 of [1]); complexity is from [1], Table 11.

[8] [V] M. N. Ahmed, S. M. Yamany, N. Mohamed, A. A. Farag, and T. Moriarty, "A modified fuzzy c-means algorithm for bias field estimation and segmentation of MRI data," *IEEE Trans. Med. Imag.*, vol. 21, no. 3, pp. 193–199, 2002, doi: 10.1109/42.996338. **(BCFCM / FCM_S)**

[9] [V] S. Chen and D. Zhang, "Robust image segmentation using FCM with spatial constraints based on new kernel-induced distance measure," *IEEE Trans. Syst., Man, Cybern. B, Cybern.*, vol. 34, no. 4, pp. 1907–1916, 2004, doi: 10.1109/TSMCB.2004.831165. **(FCM_S1/S2)**

[10] [V] W. Cai, S. Chen, and D. Zhang, "Fast and robust fuzzy c-means clustering algorithms incorporating local information for image segmentation," *Pattern Recognit.*, vol. 40, no. 3, pp. 825–838, 2007, doi: 10.1016/j.patcog.2006.07.011. **(FGFCM)**

[11] [V] S. Krinidis and V. Chatzis, "A robust fuzzy local information C-means clustering algorithm," *IEEE Trans. Image Process.*, vol. 19, no. 5, pp. 1328–1337, 2010, doi: 10.1109/TIP.2010.2040763. **(FLICM)**

[12] [V] F. Zhao, "Fuzzy clustering algorithms with self-tuning non-local spatial information for image segmentation," *Neurocomputing*, vol. 106, pp. 115–125, 2013, doi: 10.1016/j.neucom.2012.10.022. **(FCM_SNLS)**

[13] [V] M. Gong, Y. Liang, J. Shi, W. Ma, and J. Ma, "Fuzzy C-means clustering with local information and kernel metric for image segmentation," *IEEE Trans. Image Process.*, vol. 22, no. 2, pp. 573–584, 2013, doi: 10.1109/TIP.2012.2219547. **(KWFLICM)**

[14] [V] H. Zhang, Q. Wang, W. Shi, and M. Hao, "A novel adaptive fuzzy local information C-means clustering algorithm for remotely sensed imagery classification," *IEEE Trans. Geosci. Remote Sens.*, vol. 55, no. 9, pp. 5057–5068, 2017, doi: 10.1109/TGRS.2017.2702061. **(ADFLICM)**

[15] [V] T. Lei, X. Jia, Y. Zhang, L. He, H. Meng, and A. K. Nandi, "Significantly fast and robust fuzzy C-means clustering algorithm based on morphological reconstruction and membership filtering," *IEEE Trans. Fuzzy Syst.*, vol. 26, no. 5, pp. 3027–3041, 2018, doi: 10.1109/TFUZZ.2018.2796074. **(FRFCM)**

[16] [V] Y. Zhang, X. Bai, R. Fan, and Z. Wang, "Deviation-sparse fuzzy C-means with neighbor information constraint," *IEEE Trans. Fuzzy Syst.*, vol. 27, no. 1, pp. 185–199, 2019, doi: 10.1109/TFUZZ.2018.2883033. **(DSFCM_N)**

[17] [V] C. Wang, W. Pedrycz, J. Yang, M. Zhou, and Z. Li, "Wavelet frame-based fuzzy C-means clustering for segmenting images on graphs," *IEEE Trans. Cybern.*, vol. 50, no. 9, pp. 3938–3949, 2020, doi: 10.1109/TCYB.2019.2921779. **(WFCM)**

[18] [V] Q. Wang, X. Wang, C. Fang, and W. Yang, "Robust fuzzy c-means clustering algorithm with adaptive spatial & intensity constraint and membership linking for noise image segmentation," *Appl. Soft Comput.*, vol. 92, Art. no. 106318, 2020, doi: 10.1016/j.asoc.2020.106318. **(FCM_SICM)**

[19] [V] C. Wang, W. Pedrycz, M. Zhou, and Z. Li, "Sparse regularization-based fuzzy C-means clustering incorporating morphological grayscale reconstruction and wavelet frames," *IEEE Trans. Fuzzy Syst.*, vol. 29, no. 7, pp. 1826–1840, 2021, doi: 10.1109/TFUZZ.2020.2985930. **(SRFCM)**

[20] [V] Q. Wang, X. Wang, C. Fang, and J. Jiao, "Fuzzy image clustering incorporating local and region-level information with median memberships," *Appl. Soft Comput.*, vol. 105, Art. no. 107245, 2021, doi: 10.1016/j.asoc.2021.107245. **(FALRCM)**

[21] [V] A. Golzari Oskouei, M. Hashemzadeh, B. Asheghi, and M. A. Balafar, "CGFFCM: Cluster-weight and group-local feature-weight learning in fuzzy C-means clustering algorithm for color image segmentation," *Appl. Soft Comput.*, vol. 113, Art. no. 108005, 2021, doi: 10.1016/j.asoc.2021.108005. **(CGFFCM)**

[22] [V] T. Wei, X. Wang, X. Li, and S. Zhu, "Fuzzy subspace clustering noisy image segmentation algorithm with adaptive local variance & non-local information and mean membership linking," *Eng. Appl. Artif. Intell.*, vol. 110, Art. no. 104672, 2022, doi: 10.1016/j.engappai.2022.104672. **(FSC_LNML)**

[23] [V] C. Wu and Z. Wang, "A modified fuzzy dual-local information c-mean clustering algorithm using quadratic surface as prototype for image segmentation," *Expert Syst. Appl.*, vol. 201, Art. no. 117019, 2022, doi: 10.1016/j.eswa.2022.117019.

## D. Recent works (2022–2026) found in Faz 1 (not in [1]'s bibliography)

Found via Crossref keyword search and OpenAlex "works citing [1]" (search date: 2026-11-10).

| # | Status | Work | What it does (from the abstract) | Relation to [1] |
|---|---|---|---|---|
| [24] | V-abs | J. Jiao, X. Wang, T. Wei, and J. Zhang, "An adaptive fuzzy C-means noise image segmentation algorithm combining local and regional information," *IEEE Trans. Fuzzy Syst.*, vol. 31, no. 8, pp. 2645–2657, 2023, doi: 10.1109/TFUZZ.2023.3235392. | Builds a weighted image from regional and local filtering; the constraint ratio between the original and weighted image is adapted per pixel from their difference; adds the cluster sample count to the objective to speed up convergence. Argues local info fails at high noise and non-local info over-preserves noise (false edges). | Same research group; the per-pixel adaptive weighting from image–filtered differences is the same idea as α, β, γ in [1]. |
| [25] | V-abs | Y. Chen, Z. Wang, and X. Bai, "Fuzzy sparse subspace clustering for infrared image segmentation," *IEEE Trans. Image Process.*, vol. 32, pp. 2132–2146, 2023, doi: 10.1109/TIP.2023.3263102. | Combines sparse subspace clustering (self-representation, global correlation) with fuzzy memberships for infrared images with complex backgrounds and intensity inhomogeneity. | A different use of "sparsity": sparse self-representation for global information, vs. ℓ0 sparsity of the membership matrix in [1]. |
| [26] | V-abs | L. Lei, C. Wu, and X. Tian, "Robust deep kernel-based fuzzy clustering with spatial information for image segmentation," *Appl. Intell.*, vol. 53, no. 1, pp. 23–48, 2023, doi: 10.1007/s10489-022-03255-3. | Extends a deep fuzzy K-means (autoencoder + clustering) with neighborhood median/mean information, membership neighborhood information and a kernel distance (KDFKMS); reports stronger noise robustness than DFKM. | Shows the deep-learning direction for fuzzy clustering; [1] stays shallow/interpretable. |
| [27] | V-abs | C. Wu and S. Zhou, "Robust harmonic fuzzy partition local information C-means clustering for image segmentation," *Symmetry*, vol. 16, no. 10, Art. no. 1370, 2024, doi: 10.3390/sym16101370. | Introduces generalized harmonic fuzzy sets/partitions as an alternative to Ruspini (sum-to-one) partitions; proposes HLICM (with a local-convergence proof via Zangwill's theorem) and two robust kernel/FLICM-style variants. | Changes the *fuzzy partition* itself (membership constraint), whereas [1] keeps the FCM partition and changes the data term and adds sparsity. |
| [28] | V-abs | S. Das, Kamarujjaman, and S. Dhar, "Enhancing interdisciplinary image segmentation through a Gaussian-based modified local consensus spatial fuzzy approach," *Comput. Biol. Med.*, vol. 190, Art. no. 110053, 2025, doi: 10.1016/j.compbiomed.2025.110053. | GMLCSF: histogram-peak rule determines the **number of clusters** and initial centers; a consensus-inspired local spatial membership is combined with the global membership; targets satellite and medical images. | Cites [1]. Addresses [1]'s stated limitation that K must be given in advance. |
| [29] | V-meta | J. Wu, X. Wang, T. Wei, and C. Fang, "Full-parameter adaptive fuzzy clustering for noise image segmentation based on non-local and local spatial information," *Comput. Vis. Image Underst.*, vol. 235, Art. no. 103765, 2023, doi: 10.1016/j.cviu.2023.103765. | *(abstract not accessible)* | Same first author as [1], one year earlier. **Read first** — likely the direct predecessor. |
| [30] | V-meta | C. Huang *et al.*, "Interval type-2 enhanced possibilistic fuzzy C-means noisy image segmentation algorithm amalgamating weighted local information," *Eng. Appl. Artif. Intell.*, vol. 137, Art. no. 109135, 2024, doi: 10.1016/j.engappai.2024.109135. | *(abstract not accessible)* | Type-2 fuzzy direction (title). |
| [31] | V-meta | H. Cui *et al.*, "Intuitionistic fuzzy local information C-means algorithm for image segmentation," *Inf. Sci.*, vol. 681, Art. no. 121205, 2024, doi: 10.1016/j.ins.2024.121205. | *(abstract not accessible)* | Intuitionistic fuzzy sets + FLICM (title). |
| [32] | V-meta | H. Yu, Y. Wu, H. Zheng, Q. Luo, and L. Zhang, "Possibilistic c-means clustering approach based on a novel weighted-kernel distance for imbalanced images with minority targets in sparsely distribution," *Eng. Appl. Artif. Intell.*, vol. 154, Art. no. 110902, 2025, doi: 10.1016/j.engappai.2025.110902. | *(abstract not accessible)* | Cites [1]. |
| [33] | V-meta | C. Huang, H. Lei, J. Peng, X. Qin, Y. Chen, and L. Zhou, "Adaptive interval type-2 fuzzy clustering noisy image segmentation algorithm with weighted local spatial information embedding non-local spatial information," *Int. J. Fuzzy Syst.*, vol. 28, no. 6, pp. 2108–2127, 2026, doi: 10.1007/s40815-025-02068-z. | *(abstract not accessible)* | Type-2 + local/non-local (title). |

## F. Fuzzy inference foundations (added in Faz 4 for the proposed extension; Crossref responses in `verification/crossref_2026-11-12.jsonl`)

[34] [V] L. A. Zadeh, "Fuzzy sets," *Inf. Control*, vol. 8, no. 3, pp. 338–353, 1965, doi: 10.1016/S0019-9958(65)90241-X.

[35] [V] E. H. Mamdani and S. Assilian, "An experiment in linguistic synthesis with a fuzzy logic controller," *Int. J. Man-Mach. Stud.*, vol. 7, no. 1, pp. 1–13, 1975, doi: 10.1016/S0020-7373(75)80002-2.

[36] [V] T. Takagi and M. Sugeno, "Fuzzy identification of systems and its applications to modeling and control," *IEEE Trans. Syst., Man, Cybern.*, vol. SMC-15, no. 1, pp. 116–132, 1985, doi: 10.1109/TSMC.1985.6313399.

## E. Comparison table

Legend: ✓ = uses it (as described in [1] or in the work's abstract), — = not described. "Complexity" is copied from [1], Table 11 (paper-reported, symbolic and coarse).

| Method | Year | Local spatial | Non-local | Wavelet domain | Sparsity | Adaptive weights | Pre-processing / other | Complexity ([1] Tab. 11) | In [1]'s experiments |
|---|---|---|---|---|---|---|---|---|---|
| FCM [2],[3] | 1984 | — | — | — | — | — | — | O(n³) | ✓ |
| BCFCM / FCM_S [8] | 2002 | ✓ | — | — | — | — | bias-field correction | — | — |
| FCM_S1/S2 [9] | 2004 | ✓ (mean/median filtered image) | — | — | — | — | kernel distance | — | — |
| FGFCM [10] | 2007 | ✓ (spatial + gray) | — | — | — | — | gray-level histogram (fast) | O(n³) | ✓ |
| FLICM [11] | 2010 | ✓ (fuzzy factor) | — | — | — | ✓ parameter-free factor | — | — | — |
| FCM_SNLS [12] | 2013 | — | ✓ | — | — | ✓ self-tuning | — | — | — |
| KWFLICM [13] | 2013 | ✓ | — | — | — | — | kernel metric | — | — |
| ADFLICM [14] | 2017 | ✓ (pixel space attraction) | — | — | — | ✓ | — | O(n⁵) | ✓ |
| FRFCM [15] | 2018 | ✓ | — | — | — | — | morphological reconstruction + membership filtering | O(n³) | ✓ |
| DSFCM_N [16] | 2019 | ✓ | — | — | ✓ (sparse deviation) | — | — | O(n⁵) | ✓ |
| WFCM [17] | 2020 | — | — | ✓ (wavelet frame) | — | — | graph images | — | — |
| FCM_SICM [18] | 2020 | ✓ (bilateral) | — | — | — | ✓ | membership linking | O(n⁴) | ✓ |
| SRFCM [19] | 2021 | ✓ | — | ✓ (wavelet frame) | ✓ (membership) | — | morphological reconstruction | O(n³) | ✓ |
| FALRCM [20] | 2021 | ✓ | ✓ (region-level) | — | — | — | median memberships | — | — |
| CGFFCM [21] | 2021 | — | — | — | — | ✓ (feature/cluster weights) | color features | O(n³) | ✓ |
| FSC_LNML [22] | 2022 | ✓ (local variance) | ✓ | — | — | ✓ | fuzzy subspace, mean membership linking | O(n⁵) | ✓ |
| Jiao et al. [24] | 2023 | ✓ | ✓ (regional) | — | — | ✓ per pixel | weighted image | — | — |
| **ASRFCM-CSI [1]** | 2024 | ✓ (reward/penalty sets) | ✓ | ✓ (DTCWT) | ✓ (ℓ0 on U) | ✓ per pixel (α, β, γ) | — | O(n⁵) | — |

Observation used in the report: [1] is the first entry in this table that combines **local + non-local + wavelet domain + sparsity + per-pixel adaptive weights**; its closest predecessors are SRFCM [19] (wavelet + sparsity, no non-local, no adaptive weights) and FSC_LNML [22] / Jiao et al. [24] (local + non-local + adaptive, no sparsity, spatial domain).
