"""Live demo: segment a noisy image with FCM, the reproduced method (ASRFCM-CSI)
and the fuzzy-rule extension, side by side, and explain the fuzzy inference for
one pixel. Runs offline on a laptop CPU in well under two minutes.

Examples:
    python demo/demo.py                                   # sy3, 10 % mixed noise
    python demo/demo.py --image sy2 --noise salt_pepper --level 20
    python demo/demo.py --image bsds:42049 --level 5 --sigma 0.9
    python demo/demo.py --image path/to/photo.png --K 3   # any gray/colour image
    python demo/demo.py --pixel 120 80                    # explain the FIS at (row, col)
Output: results/figures/demo_panel.png (and the window if --show).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from src.data import noise  # noqa: E402
from src.eval.metrics import evaluate  # noqa: E402
from src.fcm.baseline_fcm import fcm  # noqa: E402
from src.fcm.fis_coefficients import FuzzyCoefficients, build_fis, fis_inputs  # noqa: E402
from src.fcm.pipeline import run_asrfcm  # noqa: E402


def load(name: str, K: int | None):
    if name in ("sy1", "sy2", "sy3"):
        from src.data import synthetic

        s = synthetic.load(name)
        return s.image, s.labels, s.K
    if name.startswith("bsds:"):
        from src.data import bsds500

        pid = name.split(":", 1)[1]
        gt, k = bsds500.paper_ground_truth(pid)
        return bsds500.load(pid).gray, gt, k
    img = cv2.imread(name, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise SystemExit(f"cannot read image {name}")
    if K is None:
        raise SystemExit("--K is required for your own image")
    return img.astype(np.float64) / 255.0, None, K


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--image", default="sy3")
    ap.add_argument("--K", type=int, default=None, help="number of clusters (own images only)")
    ap.add_argument("--noise", default="mixed", choices=noise.KINDS)
    ap.add_argument("--level", type=float, default=10.0, help="noise level in percent")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--sigma", type=float, default=0.3, help="reward factor (paper 0.3)")
    ap.add_argument("--delta", type=float, default=0.4, help="sparsity factor (paper 0.4)")
    ap.add_argument("--k", type=float, default=15.0, help="noise suppression factor (paper 15)")
    ap.add_argument("--pixel", type=int, nargs=2, default=None, metavar=("ROW", "COL"))
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    clean, gt, K = load(args.image, args.K)
    y = noise.add_noise(clean, args.noise, args.level / 100, args.seed)
    params = dict(sigma=args.sigma, delta=args.delta, k=args.k)
    results = {}
    t0 = time.perf_counter()
    results["FCM"] = fcm(y, K, seed=args.seed)
    pr = run_asrfcm(y, K, seed=args.seed, use_cache=False, **params)
    results["ASRFCM (paper)"] = pr.result
    xi, theta = pr.xi, pr.theta
    for label, mode in (("ASRFCM + FIS (full)", "full"), ("ASRFCM + FIS (split)", "split")):
        results[label] = run_asrfcm(y, K, seed=args.seed, coeff_method="fis",
                                    fis=FuzzyCoefficients(mode=mode, k=args.k), **params).result
    print(f"\n{args.image}, {args.noise} noise {args.level:g} %, K={K}, seed {args.seed} "
          f"(total {time.perf_counter() - t0:.1f} s)\n")
    print(f"{'method':24s} {'ACC':>7s} {'NMI':>7s} {'Kappa':>7s} {'V_PC':>7s} {'iter':>5s}")
    for name, r in results.items():
        if gt is not None:
            m = evaluate(gt, U=r.U)
            print(f"{name:24s} {m['ACC']:7.2f} {m['NMI']:7.2f} {m['Kappa']:7.2f} {m['VPC']:7.2f} {r.n_iter:5d}")
        else:
            print(f"{name:24s} {'-':>7s} {'-':>7s} {'-':>7s} {evaluate(r.labels, U=r.U)['VPC']:7.2f} {r.n_iter:5d}")

    if args.pixel:
        i, j = args.pixel
        dev, dis = fis_inputs(y[i, j], xi[i, j], theta[i, j])
        fis = build_fis()
        w = fis.firing_strengths({"Dev": np.array([dev]), "Dis": np.array([dis])})[:, 0]
        out = fis.evaluate(Dev=np.array([dev]), Dis=np.array([dis]))
        print(f"\npixel ({i},{j}): y={y[i, j]:.3f}  xi={xi[i, j]:.3f}  theta={theta[i, j]:.3f}  "
              f"Dev={dev:.3f}  Dis={dis:.3f}")
        for line, wr in zip(fis.rule_table(), w):
            if wr > 0:
                print(f"  fires {wr:.2f}  {line}")
        print("  crisp (centroid): " + ", ".join(f"{k}={v[0]:.3f}" for k, v in out.items()))

    import matplotlib

    if not args.show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    panels = [("original", clean), (f"noisy ({args.noise} {args.level:g} %)", y)]
    panels += [(name, r.labels) for name, r in results.items()]
    if gt is not None:
        panels.append(("ground truth", gt))
    fig, axes = plt.subplots(1, len(panels), figsize=(2.6 * len(panels), 2.9))
    for ax, (title, im) in zip(axes, panels):
        ax.imshow(im, cmap="gray")
        ax.set_title(title, fontsize=8)
        ax.axis("off")
    fig.tight_layout()
    out = ROOT / "results" / "figures" / "demo_panel.png"
    fig.savefig(out, dpi=150)
    print(f"\nsaved {out.relative_to(ROOT)}")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
