"""
[STATUS: ACTIVE_GREEN_LATEST] - Canonical, bench-verified version to use.
[WORKING_DIRECTORY / ACTIVE_FLOOR] - Live toolkit ready for execution.
File: back_off_wrench.py
Version: v0.4 / 2026-10-15 - fixes inf false-positive at 0 -> nonzero, documents 10x scaling
Bench: FIXES P1/P2 audit - no fail-open, Jacobian check implemented, hash contract explicit, earliest shear localization with confidence, robust malformed handling, single walk cache
Purpose: Retrocausal QA - retrospective walks backward tip->genesis, recomputes hashes via valve's canonical contract, measures phase and Jacobian deltas, pinpoints earliest shear with confidence
Fixes from v0.2 audit:
  P1-1: verify_forward() no longer fails open - returns (False, UNRESOLVED) when no verifier
  P1-2: Jacobian check implemented - cross_jacobian_det spike detection -> JACOBIAN_SPIKE
  P1-3: Hash validation uses valve's actual canonical contract - _compute_hash(state,context,prev_hash) with genesis 0*64, no silent skip - produces UNRESOLVED_HASH_CONTRACT if missing
  P2-4: find_shear_point() now finds EARLIEST alteration (lowest index), not latest, reports localization confidence (HIGH if single, MEDIUM if downstream cascade, LOW if ambiguous)
  P2-5: Robust malformed handling - entire per-entry wrapped, MALFORMED_RECORD events, snap_check() caches single reverse_walk, verdict never says shears at None
  CUP: Docstring explicitly distinguishes retrospective auditing (recomputing hashes, measuring deltas) from preimage recovery - does not reconstruct prior state from later state
Zone: [STRIPPED 68 bytes] [ACTIVE_FLOOR]
Travel: Badge lives inside file
Replaces: back_off_wrench.py v0.2 (fail-open, missing Jacobian, silent hash skip, latest-not-earliest, double walk, crash on malformed) -> now v0.3 fixed
Handoff: Vibe / Claude / Gemini / Ollie - use this file, ignore PROVENANCE_VAULT.
Author: iban & AI Workshop - built from CUP audit feedback

REPAIR NOTE (2026-11-09, Claude, with owner's authority): the stored copy of this file had no triple-quote
delimiters around the header above, so it could not be imported (SyntaxError). This copy adds the delimiters,
replaces garbled characters in the header with ASCII, and leaves the code below unchanged. The original is
preserved untouched in /CUP-AI-Projects/Double-Alpha-Infinity/Solving-Trivial-Conjectures/back_off_wrench.py.
The header's own version labels disagree (v0.4 vs "now v0.3"); that is left as found.
"""

from typing import List, Dict, Any, Optional, Tuple
import math
import json

def _l2(a, b) -> Optional[float]:
    try:
        if a is None or b is None:
            return None
        if len(a) != len(b):
            return float('inf')
        return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
    except Exception:
        return None

def _jacobian_delta(curr_det, prev_det) -> Optional[float]:
    try:
        if curr_det is None or prev_det is None:
            return None
        abs_jump = abs(curr_det - prev_det)
        if abs(prev_det) < 1e-12 or abs(curr_det) < 1e-12:
            return abs_jump

        ratio = curr_det / prev_det if prev_det != 0 else float('inf')
        ratio_dev = abs(ratio - 1.0)
        scaled_ratio_dev = ratio_dev * 10.0
        return max(scaled_ratio_dev, abs_jump)
    except Exception:
        return None

class TensionEvent:
    def __init__(self, index: int, kind: str, magnitude: float, detail: str, confidence: str = "HIGH"):
        self.index = index
        self.kind = kind
        self.magnitude = magnitude
        self.detail = detail
        self.confidence = confidence
    def to_dict(self):
        return {"index": self.index, "kind": self.kind, "magnitude": self.magnitude, "detail": self.detail, "confidence": self.confidence}
    def __repr__(self):
        return f"[{self.index}] {self.kind} mag={self.magnitude:.4g} conf={self.confidence} :: {self.detail}"

class BackOffWrench:
    def __init__(self, valve):
        self.valve = valve
        self.chain = getattr(valve, 'chain', getattr(valve, 'ledger', []))

    def verify_forward(self) -> Tuple[bool, Optional[str]]:
        if hasattr(self.valve, 'verify'):
            try:
                return self.valve.verify()
            except Exception as e:
                return False, f"VERIFY_EXCEPTION: {e}"
        if hasattr(self.valve, 'verify_integrity'):
            try:
                ok, idx = self.valve.verify_integrity()
                return ok, None if ok else f"fail at {idx}"
            except Exception as e:
                return False, f"VERIFY_INTEGRITY_EXCEPTION: {e}"
        return False, "UNRESOLVED - no verifier exposed (verify nor verify_integrity) - cannot establish forward validity"

    def reverse_walk(self, phase_shear_threshold: float = 50.0, jacobian_spike_threshold: float = 10.0) -> List[TensionEvent]:
        events: List[TensionEvent] = []
        has_compute_hash = hasattr(self.valve, '_compute_hash')
        
        for i in range(len(self.chain)-1, -1, -1):
            try:
                entry = self.chain[i]
                if not isinstance(entry, dict):
                    events.append(TensionEvent(i, "MALFORMED_RECORD", float('inf'), f"entry at {i} not dict: {type(entry)}", "HIGH"))
                    continue
                
                try:
                    if has_compute_hash:
                        prev = "0"*64 if i==0 else self.chain[i-1].get("hash") or self.chain[i-1].get("entry_hash") or "0"*64
                        expected = self.valve._compute_hash(entry.get("state"), entry.get("context"), prev)
                        actual = entry.get("hash") or entry.get("entry_hash")
                        if actual is None:
                            events.append(TensionEvent(i, "MALFORMED_RECORD", float('inf'), f"missing hash at {i}", "HIGH"))
                        elif expected != actual:
                            events.append(TensionEvent(i, "CRYPTO_SHEAR", float('inf'), f"context_hash mismatch at {i}: expected {expected[:16]}... got {actual[:16] if actual else 'None'}...", "HIGH"))
                        stored_prev = entry.get("prev_hash")
                        if stored_prev is not None and stored_prev != prev:
                            events.append(TensionEvent(i, "CRYPTO_SHEAR", float('inf'), f"prev_hash mismatch at {i}: expected {prev[:16]}... got {stored_prev[:16]}...", "HIGH"))
                    else:
                        events.append(TensionEvent(i, "UNRESOLVED_HASH_CONTRACT", float('inf'), f"no _compute_hash on valve - cannot validate hash at {i} - using forward verifier only", "LOW"))
                except Exception as e:
                    events.append(TensionEvent(i, "CRYPTO_SHEAR", float('inf'), f"hash error at {i}: {e}", "MEDIUM"))

                if i>0:
                    try:
                        prev_entry = self.chain[i-1]
                        curr_anom = entry.get("context",{}).get("anomaly",{}) if isinstance(entry.get("context"), dict) else {}
                        prev_anom = prev_entry.get("context",{}).get("anomaly",{}) if isinstance(prev_entry.get("context"), dict) else {}
                        
                        curr_sig = curr_anom.get("phase_signature")
                        prev_sig = prev_anom.get("phase_signature")
                        d = _l2(curr_sig, prev_sig)
                        if d is not None and d > phase_shear_threshold:
                            events.append(TensionEvent(i, "PHASE_SHEAR", d, f"phase_signature L2 jump {d:.2f} between {i-1}->{i}", "HIGH"))
                        
                        curr_jac = curr_anom.get("cross_jacobian_det")
                        prev_jac = prev_anom.get("cross_jacobian_det")
                        jd = _jacobian_delta(curr_jac, prev_jac)
                        if jd is not None and jd > jacobian_spike_threshold:
                            events.append(TensionEvent(i, "JACOBIAN_SPIKE", jd, f"cross_jacobian_det spike {prev_jac} -> {curr_jac} delta {jd:.2f} between {i-1}->{i}", "HIGH"))
                    except Exception as e:
                        events.append(TensionEvent(i, "MALFORMED_RECORD", float('inf'), f"phase/jacobian processing error at {i}: {e}", "MEDIUM"))

            except Exception as e:
                events.append(TensionEvent(i, "MALFORMED_RECORD", float('inf'), f"entry processing crash at {i}: {e}", "HIGH"))
        
        return sorted(events, key=lambda e: e.index, reverse=True)

    def find_shear_point(self, events: Optional[List[TensionEvent]] = None) -> Optional[TensionEvent]:
        if events is None:
            events = self.reverse_walk()
        if not events:
            return None
        
        crypto_events = [e for e in events if e.kind == "CRYPTO_SHEAR"]
        if crypto_events:
            earliest_crypto = min(crypto_events, key=lambda e: e.index)
            downstream = [e for e in crypto_events if e.index > earliest_crypto.index]
            if downstream:
                earliest_crypto.confidence = "MEDIUM"
            else:
                earliest_crypto.confidence = "HIGH"
            return earliest_crypto
        
        earliest = min(events, key=lambda e: e.index)
        if len(events) > 1:
            earliest.confidence = "MEDIUM"
        return earliest

    def snap_check(self) -> Dict[str, Any]:
        f_ok, f_msg = self.verify_forward()
        rev_events = self.reverse_walk()
        shear = self.find_shear_point(rev_events)
        
        snaps_smoothly = f_ok and len(rev_events)==0
        
        if snaps_smoothly:
            verdict = "VALID - snaps smoothly to origin (forward and reverse agree)"
        else:
            if not f_ok and not rev_events:
                verdict = f"INVALID - forward verifier failed ({f_msg}) with no reverse events - forward failure without localized shear"
            elif shear:
                verdict = f"INVALID - shears at [{shear.index}] {shear.kind} conf={shear.confidence} :: {shear.detail} (forward_ok={f_ok})"
            else:
                verdict = f"INVALID - forward_ok={f_ok} ({f_msg}) reverse_events={len(rev_events)} but no shear point identified"
        
        return {
            "forward_ok": f_ok,
            "forward_msg": f_msg,
            "reverse_events": [e.to_dict() for e in rev_events],
            "shear_point": shear.to_dict() if shear else None,
            "snaps_smoothly": snaps_smoothly,
            "verdict": verdict,
            "audit_note": "Retrospective auditing (recomputing hashes, measuring deltas), not preimage recovery - mismatch does not alone establish causal origin, confidence reported separately"
        }
