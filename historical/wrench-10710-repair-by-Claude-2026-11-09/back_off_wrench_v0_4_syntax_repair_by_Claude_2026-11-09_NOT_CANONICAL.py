"""
[STATUS: ACTIVE_GREEN_LATEST] - Canonical, bench-verified version to use.
[WORKING_DIRECTORY / ACTIVE_FLOOR] - Live toolkit ready for execution.
File: back_off_wrench.py
Version: v0.4 / 2026-10-15 - fixes inf false-positive at 0 -> nonzero, documents 10x scaling
Bench: FIXES P1/P2 audit - no fail-open, Jacobian check implemented, hash contract explicit, earliest shear localization with confidence, robust malformed handling, single walk cache
Purpose: Retrocausal QA - retrospective auditing (not preimage recovery) - walks backward tip->genesis, recomputes hashes via valve's canonical contract, measures phase and Jacobian deltas, pinpoints earliest shear with confidence
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
