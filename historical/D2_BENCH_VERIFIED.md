# D2 Bench — VERIFIED

**Date:** 2026-11-12  
**Writer:** Grok (single writer)  
**Source:** cup-horizon2 Actions Run #15, head fac523ce03e2b362e7655712b0e310a52471f34a  
https://github.com/lovejohnlove/cup-horizon2/actions/runs/43209731609  
**Conclusion:** success

## Bodies (runner-pinned)

| File | Bytes | SHA-256 | py_compile |
|------|-------|---------|------------|
| back_off_wrench_v0_4_syntax_repair_by_Claude_2026-11-09_NOT_CANONICAL.py | 10710 | cb22db5b29b8c1fabb0823ce8e52096999e05e4780c4be0e04faed211e6fffab | exit 0 |
| horizon_valve_v4_PLAIN.py | 3321 | ed1e81bd70201a8795579725c0bb0b968eb98c30458202f83d5e667200a68a91 | exit 0 |

Path: `historical/d2-bench-repair10710-plain3321/`

## bench_smoke.py (runner)

```
byte + sha256 guards: PASS
empty chain: PASS
one-step chain: PASS
SANDBOX SMOKE: PASS
bench_smoke exit: 0
```

(Label says SANDBOX; execution was on GitHub Actions runner — counts as runner VERIFIED.)

## Explicit non-claims
- Repair remains **NOT_CANONICAL**. Do not promote. Do not merge into located 10201.
- No seal.
- D8 remains **GATE** until explicit owner ruling.
- 10201 (historical defective) and 10675 drift (SHA-256 32367cce…) are untouched, preserved as distinct byte states.
- PLAIN is the cup-code historical fork (head df68b213); do not confuse with located valve 8201 or the 527-byte stub in cup-horizon2.

## Related
- D7 six bodies: VERIFIED (Run #4, reconfirmed Runs 8/14/15)
- D7 repair 10710 historical path: VERIFIED (Runs 8, 14, 15)
- D2-bench copy: VERIFIED (Run #15)
