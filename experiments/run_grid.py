"""Generic experiment runner: images x noise kinds x levels x seeds x methods.

Every row of the output CSV is one clustering run with all metrics, the number
of iterations and the times. Runs are distributed over processes; results are
appended as each (image, noise, seed) task finishes, so an interrupted run can
be resumed (tasks already in the CSV are skipped).

Config keys:
    name, images (sy1/sy2/sy3, "bsds" = the 8 paper images, or "bsds:<id>"),
    noise: {kinds: [...], levels_pct: [...]}, seeds: [...],
    methods: [{label, base, params?, record_sigma?}]   base = "FCM" | "paper" | a name in src/fcm/variants.py
        params may hold `fis: {...}` (FuzzyCoefficients options) and `fis_sigma: {...}`
        (FuzzySigma options, second iteration); record_sigma: true adds a sigma_used column
    output: results/tables/<file>.csv,  workers (optional)

Usage:
    python experiments/run_grid.py --config experiments/contribution/main.yaml
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

KEY = ["image", "noise_kind", "noise_pct", "seed"]


def expand_images(images: list[str]) -> list[str]:
    """"bsds" / "bsdsrgb" expand to the 8 paper images (gray / colour, D-043)."""
    from src.data import bsds500

    out = []
    for name in images:
        if name in ("bsds", "bsdsrgb"):
            out.extend(f"{name}:{pid}" for pid in bsds500.PAPER_IDS)
        else:
            out.append(name)
    return out


def load_image(name: str):
    """(clean or original gray image in [0, 1], ground-truth labels, K)."""
    if name.startswith(("bsds:", "bsdsrgb:")):
        from src.data import bsds500

        kind, pid = name.split(":", 1)
        gt, K = bsds500.paper_ground_truth(pid)
        im = bsds500.load(pid)
        return (im.gray if kind == "bsds" else im.rgb / 255.0), gt, K
    from src.data import synthetic

    s = synthetic.load(name)
    return s.image, s.labels, s.K


def run_method(y, K, seed, method: dict):
    from src.fcm.baseline_fcm import fcm
    from src.fcm.pipeline import run_asrfcm
    from src.fcm.variants import kwargs_for

    base, params = method["base"], dict(method.get("params", {}))
    if base == "FCM":
        r = fcm(y, K, seed=seed)
        return r, {"xi_s": 0.0, "theta_s": 0.0, "coeff_s": 0.0, "cluster_s": r.time_s}, float("nan")
    kw = kwargs_for(base)
    params.pop("record_sigma", None)
    sigma_params = params.pop("fis_sigma", None)
    if sigma_params is not None:  # second iteration, candidate C: fuzzy rule for the reward factor
        from src.fcm.fis_sigma import FuzzySigma

        kw = {**kw, "sigma_rule": FuzzySigma(**sigma_params)}
    fis_params = params.pop("fis", None)
    if fis_params is not None:  # FIS options given directly in the config
        from src.fcm.fis_coefficients import FuzzyCoefficients

        kw = {**kw, "coeff_method": "fis", "fis": FuzzyCoefficients(**fis_params)}
    pr = run_asrfcm(y, K, seed=seed, **kw, **params)
    return pr.result, pr.times, pr.sigma_used


def cfg_has_sigma(methods: list[dict]) -> bool:
    """Record the reward factor actually used only for second-iteration grids (keeps old CSV columns)."""
    return any(m.get("record_sigma") for m in methods)


def run_task(task: tuple, methods: list[dict]) -> list[dict]:
    from src.data import noise
    from src.eval.metrics import evaluate

    image, kind, pct, seed = task
    clean, gt, K = load_image(image)
    y = noise.add_noise(clean, kind, pct / 100, seed)
    rows = []
    for m in methods:
        res, times, sigma_used = run_method(y, K, seed, m)
        met = evaluate(gt, U=res.U)
        rows.append({"image": image, "noise_kind": kind, "noise_pct": pct, "seed": seed, "method": m["label"],
                     "K": K, **met, "Iterations": res.n_iter, **{f"time_{k}": v for k, v in times.items()},
                     **({"sigma_used": sigma_used} if cfg_has_sigma(methods) else {})})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()
    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    out = ROOT / cfg["output"]
    out.parent.mkdir(parents=True, exist_ok=True)
    methods = cfg["methods"]
    tasks = [(img, kind, pct, seed) for img in expand_images(cfg["images"]) for kind in cfg["noise"]["kinds"]
             for pct in cfg["noise"]["levels_pct"] for seed in cfg["seeds"]]
    done = set()
    if out.exists():
        prev = pd.read_csv(out)
        labels = {m["label"] for m in methods}
        for key, g in prev.groupby(KEY):
            if labels <= set(g["method"]):
                done.add((key[0], key[1], int(key[2]), int(key[3])))
    todo = [t for t in tasks if (t[0], t[1], int(t[2]), int(t[3])) not in done]
    print(f"{cfg['name']}: {len(tasks)} tasks x {len(methods)} methods, {len(todo)} to run", flush=True)
    workers = args.workers or cfg.get("workers") or max(1, (os.cpu_count() or 2) - 1)
    t0 = time.time()
    header = not out.exists()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(run_task, t, methods): t for t in todo}
        for i, f in enumerate(as_completed(futures), 1):
            pd.DataFrame(f.result()).to_csv(out, mode="a", header=header, index=False)
            header = False
            if i % max(1, len(todo) // 20) == 0 or i == len(todo):
                print(f"  {i}/{len(todo)} tasks, {time.time() - t0:.0f} s", flush=True)
    df = pd.read_csv(out).drop_duplicates(subset=KEY + ["method"], keep="last")
    df.sort_values(KEY + ["method"]).to_csv(out, index=False)
    print(f"saved {out.relative_to(ROOT)} ({len(df)} rows)")


if __name__ == "__main__":
    main()
