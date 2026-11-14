"""End-to-end ASRFCM-CSI pipeline (Algorithm 3, steps 1-9) with caching and ablation switches.

    noisy image y --(Alg. 2)--> xi            (local information)
                  --(DTCWT+NLM)--> theta      (non-local information)
    (y, xi, theta) --> alpha, beta, gamma     (paper Eqs. 13-19, or the fuzzy-rule system, D-033)
    --> sparse_fcm (Eqs. 20-29) --> U, centres, labels = argmax U

xi and theta depend only on the image and their own parameters, not on the
clustering seed or K, so they are computed once and cached on disk
(cache/, ignored by git). Pre-processing and clustering times are kept apart.
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .adaptive_params import EPS, paper_coefficients
from .baseline_fcm import FCMResult
from .local_info import local_spatial_info
from .nonlocal_wavelet import nonlocal_wavelet_info
from .sparse_fcm import sparse_fcm

CACHE_DIR = Path(__file__).resolve().parents[2] / "cache"

# Paper parameters (Sec. 4.1/4.4): w=5, S=15, upsilon=4, g=10, sigma=0.3, k=15, delta=0.4, m=2, eps=1e-6, T=100
DEFAULTS = dict(w=5, S=15, upsilon=4.0, g=10.0, nlm_scale=1.0, sigma=0.3, ratio=0.618, rounding="floor",
                k=15.0, delta=0.4, m=2.0, eps=1e-6, T=100)


@dataclass
class PipelineResult:
    result: FCMResult
    xi: np.ndarray | None
    theta: np.ndarray | None
    alpha: np.ndarray
    beta: np.ndarray | None
    gamma: np.ndarray | None
    times: dict = field(default_factory=dict)   # xi_s, theta_s, coeff_s, cluster_s
    sigma_used: float = float("nan")            # reward factor of the local term (mean if per pixel)


def _key(img: np.ndarray, tag: str, **params) -> str:
    h = hashlib.sha1(np.ascontiguousarray(img, dtype=np.float64).tobytes())
    h.update((tag + repr(sorted(params.items()))).encode())
    return h.hexdigest()[:20]


def _cached(fn, img: np.ndarray, tag: str, use_cache: bool, **params) -> tuple[np.ndarray, float]:
    """Return (array, seconds). Seconds = compute time (stored with the cache entry)."""
    path = CACHE_DIR / f"{tag}_{_key(img, tag, **params)}.npz"
    if use_cache and path.exists():
        with np.load(path) as z:
            return z["arr"], float(z["seconds"])
    t0 = time.perf_counter()
    arr = fn(img, **params)
    sec = time.perf_counter() - t0
    if use_cache:
        CACHE_DIR.mkdir(exist_ok=True)
        np.savez_compressed(path, arr=arr, seconds=sec)
    return arr, sec


def _per_channel(fn, img, *args):
    """Gray: fn(img). Colour (H, W, C): fn on every channel separately, stacked (D-043)."""
    if np.ndim(img) == 2:
        return fn(img, *args)
    outs = [fn(np.ascontiguousarray(img[..., c]), *args) for c in range(img.shape[-1])]
    return np.stack([o[0] for o in outs], axis=-1), sum(o[1] for o in outs)


def compute_xi(img, w, sigma, ratio, rounding, use_cache=True):
    return _per_channel(lambda im: _cached(local_spatial_info, im, "xi", use_cache, w=w, sigma=sigma, ratio=ratio,
                                           rounding=rounding), img)


def compute_theta(img, S, w, upsilon, g, scale=1.0, use_cache=True):
    return _per_channel(lambda im: _cached(nonlocal_wavelet_info, im, "theta", use_cache, S=S, w=w, upsilon=upsilon,
                                           g=g, scale=scale), img)


def coefficients(y, xi, theta, method: str, k: float, variant: str, fis=None):
    """alpha, beta, gamma for the active terms (D-037). xi/theta may be None (term off)."""
    if method == "fis":
        if fis is None:
            raise ValueError("method='fis' needs a fuzzy coefficient system (src/fcm/fis_coefficients.py)")
        return fis(y, xi, theta)
    if method != "paper":
        raise ValueError("method must be 'paper' or 'fis'")
    if xi is None and theta is None:
        return np.ones(np.shape(y)[:2]), None, None
    ref1 = xi if xi is not None else theta
    ref2 = theta if theta is not None else xi
    alpha, dG1, dG2 = paper_coefficients(y, ref1, ref2, k=k, variant=variant)
    if xi is not None and theta is not None:
        return alpha, dG1, dG2
    single = dG1  # only one corrected image active: alpha = 1 / dG
    a = 1.0 / single
    return (a, single, None) if xi is not None else (a, None, single)


def run_asrfcm(img: np.ndarray, K: int, seed: int = 0, use_local: bool = True, use_nonlocal: bool = True,
               use_sparse: bool = True, coeff_method: str = "paper", coeff_variant: str = "signed",
               empty_col_policy: str = "keep", fis=None, sigma_rule=None, use_cache: bool = True,
               **params) -> PipelineResult:
    """Run the proposed method on a noisy image in [0, 1]. `params` override DEFAULTS.

    sigma_rule: optional callable y -> reward factor sigma (a number, or an (H, W) array
    for one value per pixel). It replaces the fixed sigma of the local term; used by the
    fuzzy-sigma variants of the second iteration (src/fcm/fis_sigma.py, D-045)."""
    p = {**DEFAULTS, **params}
    unknown = set(params) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"unknown parameters {unknown}")
    y = np.asarray(img, dtype=np.float64)
    times = {"xi_s": 0.0, "theta_s": 0.0}
    sigma_used = float("nan")
    xi = theta = None
    if use_local:
        sigma = p["sigma"]
        if sigma_rule is not None:
            sigma = sigma_rule(y)
            if np.ndim(sigma) == 0:
                sigma = round(float(sigma), 4)  # a number: rounded so the xi cache is reused
        if np.ndim(sigma) == 0:
            sigma_used = float(sigma)
            xi, times["xi_s"] = compute_xi(y, p["w"], sigma, p["ratio"], p["rounding"], use_cache)
        else:  # one sigma per pixel: computed directly (an array cannot be a cache key)
            sigma_used = float(np.mean(sigma))
            t0 = time.perf_counter()
            if np.ndim(y) == 2:
                xi = local_spatial_info(y, p["w"], sigma, p["ratio"], p["rounding"])
            else:
                xi = np.stack([local_spatial_info(np.ascontiguousarray(y[..., c]), p["w"], sigma, p["ratio"],
                                                  p["rounding"]) for c in range(y.shape[-1])], axis=-1)
            times["xi_s"] = time.perf_counter() - t0
    if use_nonlocal:
        theta, times["theta_s"] = compute_theta(y, p["S"], p["w"], p["upsilon"], p["g"], p["nlm_scale"], use_cache)
    t0 = time.perf_counter()
    alpha, beta, gamma = coefficients(y, xi, theta, coeff_method, p["k"], coeff_variant, fis)
    times["coeff_s"] = time.perf_counter() - t0
    res = sparse_fcm(y, xi, theta, alpha, beta, gamma, K, m=p["m"], delta=p["delta"] if use_sparse else 0.0,
                     T=p["T"], eps=p["eps"], seed=seed, empty_col_policy=empty_col_policy)
    times["cluster_s"] = res.time_s
    return PipelineResult(res, xi, theta, alpha, beta, gamma, times, sigma_used)


__all__ = ["DEFAULTS", "EPS", "PipelineResult", "run_asrfcm", "compute_xi", "compute_theta", "coefficients"]
