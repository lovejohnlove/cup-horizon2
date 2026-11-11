# phase_space_caliper.py — v3.1.1 corrective aggregate propagation fix
import math
GENESIS = "phase-space-caliper-v3.1.1-aggregate-blowup-fix"

def _det(matrix):
    n = len(matrix)
    a = [row[:] for row in matrix]
    det = 1.0
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(a[r][i]))
        if abs(a[pivot][i]) < 1e-15:
            return 0.0
        if pivot != i:
            a[pivot], a[i] = a[i], a[pivot]
            det = -det
        det *= a[i][i]
        for r in range(i + 1, n):
            factor = a[r][i] / a[i][i]
            for c in range(i, n):
                a[r][c] -= factor * a[i][c]
    return det

def _matmul(A, B):
    return [[math.fsum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

def _transpose(A):
    return [list(col) for col in zip(*A)]

class PhaseSpaceCaliper:
    def __init__(self, collapse_eps=1e-9, blowup_factor=100.0):
        self.collapse_eps = collapse_eps
        self.blowup_factor = blowup_factor

    @staticmethod
    def _extract_vector(state):
        if isinstance(state, dict):
            keys = sorted(state.keys())
            if 'x' in keys and 'v' in keys:
                other = [k for k in keys if k not in ('x','v')]
                ordered = ['x','v'] + other
                numeric_keys = [k for k in ordered if isinstance(state[k], (int, float)) and not isinstance(state[k], bool) and math.isfinite(float(state[k]))]
                non_numeric = [k for k in keys if k not in numeric_keys]
            else:
                numeric_keys = [k for k in keys if isinstance(state[k], (int, float)) and not isinstance(state[k], bool) and math.isfinite(float(state[k]))]
                non_numeric = [k for k in keys if k not in numeric_keys]
            vector = [float(state[k]) for k in numeric_keys]
            return vector, numeric_keys, non_numeric
        vector = [float(v) for v in state]
        return vector, list(range(len(vector))), []

    def measure_tick(self, states_at_tick):
        if not states_at_tick or len(states_at_tick) < 2:
            return {"det": None, "status": "DEGENERATE_PROJECTION", "detail": "fewer than 2 threads", "threads": len(states_at_tick or [])}
        extracted = [self._extract_vector(s) for s in states_at_tick]
        dims = [len(e[0]) for e in extracted]
        if any(d == 0 for d in dims):
            empty = [i for i, d in enumerate(dims) if d == 0]
            return {"det": None, "status": "DEGENERATE_PROJECTION", "detail": f"thread(s) {empty} have no numeric state", "threads": len(states_at_tick)}
        if len(set(dims)) > 1:
            return {"det": None, "status": "DIMENSION_MISMATCH", "detail": f"per-thread dims {dims}", "threads": len(states_at_tick)}
        mat = [e[0] for e in extracted]
        k, dim = len(mat), dims[0]
        
        # Corrected: restricted pre-check to x-components (or renamed max_abs_component as noted)
        max_abs_component = 0.0
        for row in mat:
            for v in row:
                if math.isfinite(v):
                    max_abs_component = max(max_abs_component, abs(v))
        if max_abs_component > 1e6:
            centroid = [math.fsum(row[d] for row in mat) / k for d in range(dim)]
            return {"det": None, "status": "TENSION_BLOWUP", "detail": f"pre-check max_abs_component={max_abs_component:.2e} > 1e6 -> blowup-by-definition, avoids Gram underflow", "threads": k, "dim": dim, "non_numeric_fields": {i: e[2] for i, e in enumerate(extracted) if e[2]}, "centered_det": None, "uncentered_magnitude": None, "centroid": centroid, "max_abs": max_abs_component}
        
        centroid = [math.fsum(row[d] for row in mat) / k for d in range(dim)]
        centered = [[row[d] - centroid[d] for d in range(dim)] for row in mat]
        if k == dim:
            det_uncentered = _det(mat)
            det = det_uncentered
            magnitude = abs(det_uncentered)
            true_centered = _det(centered)
        elif k > dim:
            gram = _matmul(_transpose(centered), centered)
            det_gram = _det(gram)
            det = math.sqrt(max(0.0, det_gram))
            magnitude = det
            true_centered = det
        else:
            gram = _matmul(centered, _transpose(centered))
            det_gram = _det(gram)
            det = math.sqrt(max(0.0, det_gram))
            magnitude = det
            true_centered = det
        
        result = {"det": det, "status": "STABLE_TENSION", "detail": None, "threads": k, "dim": dim,
                  "non_numeric_fields": {i: e[2] for i, e in enumerate(extracted) if e[2]},
                  "centered_det": true_centered,
                  "uncentered_magnitude": magnitude if k == dim else None,
                  "centroid": centroid}
        if magnitude < self.collapse_eps:
            result["status"] = "TENSION_COLLAPSE"
            result["detail"] = f"|centered det|={magnitude:.2e} < eps={self.collapse_eps}"
        elif k == dim and det < 0:
            result["status"] = "ORIENTATION_FLIP"
            result["detail"] = "signed determinant negative"
        return result

    def measure_stability(self, ticks):
        per_tick = [self.measure_tick(tick) for tick in ticks]
        mags = []
        for r in per_tick:
            if r["det"] is None:
                continue
            if r.get("threads", 0) == r.get("dim", -1) and r.get("threads", 0) > 0:
                mags.append(abs(r["det"]))
            elif "centered_det" in r:
                mags.append(abs(r["centered_det"]))
            else:
                mags.append(abs(r["det"]))
        
        # Corrected aggregate verdict propagation: TENSION_BLOWUP now bubbles up correctly
        if any(r["status"] == "TENSION_COLLAPSE" for r in per_tick):
            verdict = "TENSION_COLLAPSE"
        elif any(r["status"] == "TENSION_BLOWUP" for r in per_tick):
            verdict = "TENSION_BLOWUP"
        elif mags and mags[-1] > mags[0] * self.blowup_factor:
            verdict = "TENSION_BLOWUP"
        elif any(r["status"] == "ORIENTATION_FLIP" for r in per_tick):
            verdict = "ORIENTATION_FLIP_EVENT"
        else:
            verdict = "STABLE_TENSION"
        return {"verdict": verdict, "per_tick": per_tick}

    def calibrate_ledger(self, ledger):
        ticks, skipped = [], 0
        for entry in ledger:
            loom = (entry.get("context") or {}).get("loom_slice") or {}
            thread_states = loom.get("thread_states")
            if thread_states:
                ticks.append(thread_states)
            else:
                skipped += 1
        if not ticks:
            return {"verdict": "NO_LOOM_SLICES", "detail": "no ledger entries carry loom_slice.thread_states", "entries": len(ledger), "skipped": skipped}
        result = self.measure_stability(ticks)
        result["entries"] = len(ledger)
        result["skipped"] = skipped
        return result
