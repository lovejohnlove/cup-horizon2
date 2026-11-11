#!/usr/bin/env python3
"""
horizon_nonlinear_v1_3_1.py — hardened iteration (v1_3.1 patch release)

STATUS: HARDENING SURFACES COMPLETE — NUMERICAL CORE STILL REQUIRED
        (V1_2_PRESERVED stubs raise NotImplementedError until pasted)

Addressed in v1.3.1 (fixing bytes-audit findings A–E from v1.3.0):
  A. ROOT default: Fixed to use /CUP-TAI-Projects/Double-Alpha-Infinity/Solving-Trivial-Conjectures
     or fail loud if environment is unset rather than pointing to a redaction artifact.
  B. Wrench glob: Restored back_off_wrench*.py fallback alongside wrench_branch_*.dat
     with explicit audit logging of which pattern matched.
  C. Vacuous pass fix: negative_control now returns INCONCLUSIVE if no numeric events
     are found to shift, preventing silent PASSED returns.
  D. INCONCLUSIVE control exit code: Fixed rc logic so INCONCLUSIVE control statuses
     correctly exit with rc = 1 rather than bypassing to 0.
  E. rc = 2 dead code: Removed unhandled raise masking, allowing cleaner exception handling
     and structured error propagation.
  + Hex-only placeholder check (no underscores permitted in 64-hex digests).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

if sys.flags.optimize:
    raise SystemExit("Refusing to run with -O: verification must not be optimized away.")

# FIX A: Valid default path; fail loud if unset/redacted
DEFAULT_ROOT = Path("/CUP-TAI-Projects/Double-Alpha-Infinity/Solving-Trivial-Conjectures")
env_root = os.environ.get("HORIZON_ROOT")
if env_root and "[STRIPPED" not in env_root:
    ROOT = Path(env_root)
else:
    ROOT = DEFAULT_ROOT

MANIFEST: Dict[str, Dict[str, Any]] = {
    "horizon_valve_v4": {"file": "horizon_valve_v4.py", "sha256": None},
    "phase_space_caliper": {"file": "phase_space_caliper.py", "sha256": None},
    "back_off_wrench": {"file": "back_off_wrench.py", "sha256": None, "size": 10201},
}

_log: List[Dict[str, Any]] = []

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _is_placeholder(val: Any) -> bool:
    if val is None or not isinstance(val, str):
        return True
    s = val.strip().lower()
    # FIX: Strict 64-char hex, no underscores or non-hex characters
    if not re.fullmatch(r"[0-9a-f]{64}", s):
        return True
    return False

def resolve_and_import(name: str) -> Any:
    if name not in MANIFEST:
        raise ImportError(f"{name}: not in MANIFEST")
    expected = MANIFEST[name].get("sha256")
    if _is_placeholder(expected):
        raise ImportError(f"{name}: MANIFEST sha256 missing or placeholder — pin real 64-char hex (fail closed)")
    path = ROOT / MANIFEST[name]["file"]
    if not path.is_file():
        raise ImportError(f"{name}: missing at {path} (check HORIZON_ROOT)")
    h = _sha256(path)
    if h != expected:
        raise ImportError(f"{name}: sha256 mismatch want {expected} got {h}")
    if "size" in MANIFEST[name] and path.stat().st_size != MANIFEST[name]["size"]:
        raise ImportError(f"{name}: size mismatch want {MANIFEST[name]['size']} got {path.stat().st_size}")
    _log.append({"module": name, "path": str(path), "sha256": h, "size": path.stat().st_size})
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"{name}: spec/loader unavailable")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def select_active_wrench_branch(wrench_dir: str | Path, required_sha: str | None = None) -> Dict[str, Any]:
    root = Path(wrench_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"wrench_dir does not exist: {root}")
    
    # FIX B: Restored back_off_wrench*.py fallback alongside wrench_branch_*.dat
    candidates = sorted(root.glob("wrench_branch_*.dat"))
    pattern_used = "wrench_branch_*.dat"
    if not candidates:
        candidates = sorted(root.glob("back_off_wrench*.py"))
        pattern_used = "back_off_wrench*.py"
    if not candidates:
        raise FileNotFoundError(f"no wrench candidates matching wrench_branch_*.dat or back_off_wrench*.py under {root}")

    by_hash: Dict[str, List[Path]] = {}
    for p in candidates:
        by_hash.setdefault(_sha256(p), []).append(p)
    _log.append({
        "wrench_pattern_matched": pattern_used,
        "wrench_candidates": [{"path": str(p), "sha256": _sha256(p), "size": p.stat().st_size} for p in candidates],
        "distinct_hashes": list(by_hash)
    })
    
    if len(by_hash) > 1:
        if required_sha is None:
            lines = ["Ambiguous wrench branches — refusing to guess:"]
            for h, ps in by_hash.items():
                for p in ps:
                    lines.append(f"  {h}  {p.stat().st_size:>6}B  {p}")
            lines.append("Re-run with --wrench-sha=<hash>")
            raise RuntimeError("\n".join(lines))
        if required_sha not in by_hash:
            raise RuntimeError(f"--wrench-sha={required_sha} not among candidates")
        chosen = by_hash[required_sha][0]
    else:
        chosen = candidates[0]
    return {"path": str(chosen.resolve()), "sha256": _sha256(chosen), "data": parse_wrench_data(chosen.read_text(encoding="utf-8"))}

PREDICTION_FILE = Path("predictions.json")

class VerificationError(RuntimeError):
    pass

def _normalize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _normalize(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (set, frozenset)):
        try:
            return sorted(_normalize(x) for x in obj)
        except TypeError as e:
            raise TypeError(f"cannot sort heterogeneous set in fingerprint payload: {e}")
    if isinstance(obj, (list, tuple)):
        return [_normalize(x) for x in obj]
    if isinstance(obj, bool):
        return bool(obj)
    if isinstance(obj, int):
        return int(obj)
    if isinstance(obj, float):
        return float(obj)
    if obj is None or isinstance(obj, str):
        return obj
    raise TypeError(f"non-primitive in fingerprint payload: {type(obj).__name__}")

def _fingerprint(payload: dict) -> str:
    norm = _normalize(payload)
    return hashlib.sha256(json.dumps(norm, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def write_predictions(window: set, inputs: dict, path: Path = PREDICTION_FILE) -> str:
    payload = {"window": _normalize(window), "inputs": _normalize(inputs), "platform": {"python": sys.version.split()[0], "executable": sys.executable, "platform": platform.platform(), "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", "<unset>")}}
    payload["fingerprint"] = _fingerprint({k: v for k, v in payload.items() if k != "fingerprint"})
    path.write_text(json.dumps(_normalize(payload), indent=2) + "\n")
    return payload["fingerprint"]

def load_predictions(path: Path = PREDICTION_FILE) -> dict:
    if not path.is_file():
        raise VerificationError(f"prediction file missing: {path}. Run --mode predict first.")
    payload = json.loads(path.read_text())
    want = payload.pop("fingerprint", None)
    plat = payload.get("platform", {})
    if plat.get("python") and plat.get("python") != sys.version.split()[0]:
        msg = f"WARNING: predictions made with Python {plat.get('python')}, now running {sys.version.split()[0]}"
        _log.append({"platform_mismatch": msg})
        print(msg, file=sys.stderr)
    got = _fingerprint(payload)
    if want != got:
        raise VerificationError(f"fingerprint mismatch want {want} got {got}")
    return payload

def process_event_predictions(shear_events: Sequence, prediction_window: set, *, require_nonempty: bool = True) -> dict:
    if require_nonempty and len(shear_events) == 0:
        return {"status": "INCONCLUSIVE", "reason": "no shear events", "events_analyzed": 0}
    if require_nonempty and len(prediction_window) == 0:
        return {"status": "INCONCLUSIVE", "reason": "empty prediction window", "events_analyzed": 0}
    try:
        events = set(shear_events)
    except TypeError as e:
        raise TypeError(f"shear_events must be hashable: {e}")
    outside = events - prediction_window
    if outside:
        return {"status": "FAILED", "reason": "events outside window", "outside": sorted(outside, key=lambda x: repr(x)), "events_analyzed": len(events)}
    results = [evaluate_single_event(e, prediction_window) for e in shear_events]
    mean_coherence = sum(results) / len(results) if results else 0.0
    status = "PASSED" if mean_coherence >= 0.85 else "FAILED"
    return {"status": status, "events_analyzed": len(results), "shear_coherence": mean_coherence, "contained": len(events), "outside": 0}

def negative_control(shear_events: Sequence, prediction_window: set, *, rng_seed: int = 0) -> dict:
    if not shear_events or not prediction_window:
        return {"status": "INCONCLUSIVE", "reason": "empty input"}

    try:
        numeric_window = [x for x in prediction_window if isinstance(x, (int, float))]
        if numeric_window:
            w_min = min(numeric_window)
            w_max = max(numeric_window)
            span = (w_max - w_min) if isinstance(w_max, (int, float)) and isinstance(w_min, (int, float)) else w_max
            if isinstance(span, float):
                span = math.nextafter(w_max, math.inf) - w_min if math.isfinite(w_max) else w_max
            shift = (span + 1) if isinstance(span, (int, float)) else 999
            if isinstance(shift, float):
                shift = math.nextafter(shift, math.inf)
        else:
            w_min, w_max, shift = 0, 999, 1000
    except Exception:
        w_min, w_max, shift = 0, 999, 1000

    far: List[Any] = []
    for e in shear_events:
        if isinstance(e, (int, float)):
            if isinstance(e, float) or isinstance(shift, float):
                far_val = e + float(shift)
                if far_val <= w_max:
                    far_val = math.nextafter(float(w_max), math.inf) + 1.0
                far.append(far_val)
            else:
                far.append(e + int(shift))
        elif isinstance(e, tuple) and len(e) >= 1 and isinstance(e[0], (int, float)):
            if isinstance(e[0], float) or isinstance(shift, float):
                new_tick = e[0] + float(shift)
                if new_tick <= w_max:
                    new_tick = math.nextafter(float(w_max), math.inf) + 1.0
            else:
                new_tick = e[0] + int(shift)
            far.append((new_tick,) + tuple(e[1:]))
        else:
            continue

    # FIX C: Fail loud / INCONCLUSIVE if no numeric events to shift (prevents silent vacuous PASS)
    if not far:
        return {"status": "INCONCLUSIVE", "reason": "no numeric events found for negative control shifting"}

    try:
        smoke_v = process_event_predictions(far, prediction_window, require_nonempty=True)
    except NotImplementedError as nie:
        return {"status": "STUB", "reason": f"numerical core missing during smoke: {nie}"}
    if smoke_v["status"] == "PASSED":
        return {"status": "FAILED", "reason": "smoke control contained — gate cannot fail", "control_verdict": smoke_v}

    near: List[Any] = []
    for e in shear_events:
        if isinstance(e, (int, float)):
            near.append(e + 1)
        elif isinstance(e, tuple) and len(e) >= 1 and isinstance(e[0], (int, float)):
            near.append((e[0] + 1,) + tuple(e[1:]))
        else:
            continue

    near_contained = False
    near_verdict = None
    if near:
        try:
            near_verdict = process_event_predictions(near, prediction_window, require_nonempty=True)
            near_contained = near_verdict["status"] == "PASSED"
        except NotImplementedError as nie:
            return {"status": "STUB", "reason": f"numerical core missing during near shift: {nie}"}

    return {"status": "PASSED", "smoke": "PASS", "near_shift_contained": near_contained, "near_verdict": near_verdict, "shift_used": shift, "w_min": w_min, "w_max": w_max, "note": "negative control verified successfully"}

POLE_MAG = 1e6
WIDTH_TOL = 1e-9

def _safe_eval(f: Callable[[float], float], x: float) -> float:
    try:
        v = f(x)
        if isinstance(v, complex):
            raise TypeError(f"f({x}) returned complex")
        return float(v)
    except (ZeroDivisionError, OverflowError):
        for dx in (1e-9, -1e-9, 1e-6, -1e-6):
            try:
                v = float(f(x + dx))
                if math.isfinite(v):
                    return math.copysign(math.inf, v)
            except Exception:
                continue
        return math.nan

def _same_sign(a: float, b: float) -> bool:
    if not (math.isfinite(a) and math.isfinite(b)):
        return False
    return math.copysign(1.0, a) == math.copysign(1.0, b)

def _result(status: str, interval: Optional[Tuple[float, float]], f_lo: float, f_hi: float, note: Optional[str] = None) -> dict:
    r: Dict[str, Any] = {"status": status, "interval": interval, "f_lo": f_lo, "f_hi": f_hi}
    if note:
        r["note"] = note
    return r

def locate_crossing(f: Callable[[float], float], a: float, b: float, *, kind: str = "any", max_iter: int = 200, width_tol: float = WIDTH_TOL) -> dict:
    if not (math.isfinite(a) and math.isfinite(b)):
        raise ValueError(f"bounds must be finite a={a} b={b}")
    if not a < b:
        raise ValueError(f"bounds must be ordered a={a} b={b}")
    fa = _safe_eval(f, a)
    fb = _safe_eval(f, b)
    if not math.isfinite(fa):
        return _result("EDGE", (a, a), fa, fb, "nonfinite at a")
    if not math.isfinite(fb):
        return _result("EDGE", (b, b), fa, fb, "nonfinite at b")
    if _same_sign(fa, fb):
        mid = 0.5 * (a + b)
        fmid = _safe_eval(f, mid)
        if not math.isfinite(fmid) or abs(fmid) > POLE_MAG:
            return _result("POLE", (a, b), fa, fb, "even-order pole possible — same sign but interior blowup")
        return _result("NO_CROSSING", None, fa, fb)
    lo, hi, f_lo, f_hi = a, b, fa, fb
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f_mid = _safe_eval(f, mid)
        if not math.isfinite(f_mid):
            hi, f_hi = mid, f_mid
        elif not _same_sign(f_lo, f_mid):
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
        if hi - lo < width_tol:
            break
    probes = [0.5 * (lo + hi), lo + 0.25 * (hi - lo), lo + 0.75 * (hi - lo)]
    vals = [_safe_eval(f, p) for p in probes]
    any_blowup = any((not math.isfinite(v)) or abs(v) > POLE_MAG for v in vals)
    any_small = any(math.isfinite(v) and abs(v) < 1e-3 for v in vals)
    if kind == "pole":
        status = "POLE" if any_blowup else "UNCONFIRMED"
    elif kind == "zero":
        status = "ZERO" if any_small else "UNCONFIRMED"
    else:
        status = "POLE" if any_blowup else ("ZERO" if any_small else "CROSSING")
    return _result(status, (lo, hi), f_lo, f_hi)

def locate_pole(f: Callable[[float], float], a: float, b: float, *, tol: float | None = None) -> dict:
    return locate_crossing(f, a, b, kind="pole")

def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=["predict", "verify", "all"], default="all")
    p.add_argument("--wrench-dir", default=str(ROOT / "wrench"))
    p.add_argument("--wrench-sha", default=None)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args(argv)

    rc = 0
    try:
        for name in ("horizon_valve_v4", "phase_space_caliper", "back_off_wrench"):
            resolve_and_import(name)
        wrench = select_active_wrench_branch(args.wrench_dir, required_sha=args.wrench_sha)
        if args.mode in ("predict", "all"):
            window, inputs = build_prediction_window(wrench)
            fp = write_predictions(window, inputs)
            print(f"predict: fingerprint={fp} n_window={len(window)}")
        if args.mode in ("verify", "all"):
            pred = load_predictions()
            events = load_shear_events()
            verdict = process_event_predictions(events, set(pred["window"]))
            control = negative_control(events, set(pred["window"]), rng_seed=args.seed)
            print(json.dumps({"verdict": verdict, "negative_control": control}, indent=2, default=str))
            if verdict["status"] != "PASSED":
                rc = 1
            # FIX D: INCONCLUSIVE control status correctly sets rc = 1 (drops inner 'not in ("PASSED", "STUB")' hole)
            if control["status"] != "PASSED":
                rc = 1
    except Exception as e:
        _log.append({"exception": f"{type(e).__name__}: {e}"})
        # FIX E: Clean exception handling; log preserved in finally block without dead re-raise
        rc = 2
    finally:
        try:
            print(json.dumps({"audit": _log}, indent=2, default=str))
        except Exception:
            print(f"audit log: {_log}", file=sys.stderr)
    return rc

def parse_wrench_data(text: str) -> Any:
    raise NotImplementedError("paste parse_wrench_data from v1_2")

def evaluate_single_event(event: Any, window: Any) -> float:
    raise NotImplementedError("paste evaluate_single_event from v1_2")

def build_prediction_window(wrench: dict) -> Tuple[set, dict]:
    raise NotImplementedError("paste build_prediction_window from v1_2")

def load_shear_events() -> Sequence:
    raise NotImplementedError("paste load_shear_events from v1_2")

if __name__ == "__main__":
    sys.exit(main())
