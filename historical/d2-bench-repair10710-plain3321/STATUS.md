# D2 Bench Crate — repair 10710 + valve PLAIN 3321

**Status:** **VERIFIED** by Actions Run #15 / NOT_CANONICAL / no seal  
**Date:** 2026-11-12  
**Writer:** Grok (single writer)  
**Runner:** https://github.com/lovejohnlove/cup-horizon2/actions/runs/43209731609  
**Head:** fac523ce03e2b362e7655712b0e310a52471f34a

## Bodies (runner-pinned)
| File | Bytes | SHA-256 | Source |
|------|-------|---------|--------|
| back_off_wrench_v0_4_syntax_repair_by_Claude_2026-11-09_NOT_CANONICAL.py | 10710 | cb22db5b29b8c1fabb0823ce8e52096999e05e4780c4be0e04faed211e6fffab | Run #15 VERIFIED |
| horizon_valve_v4_PLAIN.py | 3321 | ed1e81bd70201a8795579725c0bb0b968eb98c30458202f83d5e667200a68a91 | cup-code head df68b213, Run #15 pin |

## Runner results (Run #15)
- d2-bench repair py_compile exit: 0
- d2-bench PLAIN py_compile exit: 0
- bench_smoke: byte+sha guards PASS, empty PASS, one-step PASS, exit 0

## Explicit
- Repair is NOT_CANONICAL. Do not promote. Do not merge into located 10201.
- PLAIN is the historical fork from cup-code; do not confuse with located valve 8201 or the 527-byte stub in cup-horizon2.
- D8 remains GATE. This crate does not seal.
- 10201 and 10675 drift (SHA-256 32367cce…) untouched, preserved.

## Harness
bench_smoke.py — byte/sha guards + snap_check on empty and one-step chains. Exit 0 on pass.
