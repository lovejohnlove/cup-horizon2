# D7 Leg 3 — VERIFIED

**Date:** 2026-11-12  
**Writer:** Grok (single writer)  
**Scope:** Six Leg 3 bodies + repair 10710. No seal. Repair remains NOT_CANONICAL.

## Six bodies — VERIFIED (Actions Run #4)

Source: https://github.com/lovejohnlove/cup-horizon2/actions/runs/43094509052  
Head: c9d422774d97c87c8de2aacac6eec01a4d3796c8

| File | Bytes | SHA-256 |
|------|-------|---------|
| back_off_wrench_v0_4_located.py | 10201 | 1c7464403c9af9ca067f1cb13284d0bb4a0cca2419d0aab94bd28b6785bf8cbe |
| horizon_valve_v4.py | 8201 | e52621b6e21abeca403536bc0654f7361d7d48bd0ad696b4d7ecdfc65de854c8 |
| horizon_nonlinear_v1_3_1.py | 17666 | c466c5581135b482af9c206d4cd90d67fa6c97aa6c86047409f4ca0c6fe6baa0 |
| phase_space_caliper_v3_1_1_located.py | 6953 | bb7164a61defd094a29db21ba849f8dd309fd0622503c035c0988798d0e939f8 |
| CUP_HARNESS_CONTRACT.md | 6621 | 5295419ab6de25000327cf932289240cc64e578a48d8f8fcf4ca8b3b9d1cd621 |
| notion_10k_manifest_final.json | 1474 | fd929101c74d18061e3e937fdcceb04990012858e313c01666a919a0a31f0ae1 |

Located 10201 fails py_compile as expected (SyntaxError U+2192). Others compile / JSON validate. Re-confirmed in Run #8.

## Repair 10710 — VERIFIED (Actions Run #8)

Source: https://github.com/lovejohnlove/cup-horizon2/actions/runs/43207211179  
Head: 3195f9d73b13519dc3f0cf1aeb2be3afed1d9815  
Path: historical/wrench-10710-repair-by-Claude-2026-11-09/back_off_wrench_v0_4_syntax_repair_by_Claude_2026-11-09_NOT_CANONICAL.py  
Bytes: 10710  
SHA-256: cb22db5b29b8c1fabb0823ce8e52096999e05e4780c4be0e04faed211e6fffab  
py_compile: exit 0  
**NOT_CANONICAL.** Do not promote. Do not merge into 10201. Truncated historical blob e7bfaa86… is a distinct byte state; keep.

## Explicit non-claims
- No seal.  
- D8 remains GATE until explicit owner ruling.  
- D2 unblocked for bench cut only (repair 10710 + cup-code PLAIN 3321).  
- cup-code untouched at df68b213.
