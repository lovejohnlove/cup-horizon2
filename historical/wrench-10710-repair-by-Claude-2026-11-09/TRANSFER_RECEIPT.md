# Transfer Receipt — Repair 10710 (header-only) -> cup-horizon2

Owner ruling 2026-11-11: repair accepted as new byte state, not canonical, not a merge.

## Source

- Drive file: back_off_wrench_v0_4_syntax_repair_by_Claude_2026-11-09_NOT_CANONICAL.py
- 10710 bytes, modified 2026-11-11T20:01:04Z
- Local inspection (Grok, single writer): sha256 cb22db5b29b8c1fabb0823ce8e52096999e05e4780c4be0e04faed211e6fffab, md5 1f264ba017c68809346513a3ccc21499, python3 -m py_compile exit 0

## Diff vs located 10201

- Located 10201: SHA-256 1c7464403c9af9ca067f1cb13284d0bb4a0cca2419d0aab94bd28b6785bf8cbe, py_compile exit 1 (SyntaxError invalid character U+2192 at line 4, header prose).
- Diff is header only (+509 bytes, 32 lines). Added opening/closing triple-quotes, ASCII-normalized header characters, inserted REPAIR NOTE 2026-11-09 Claude. Code body identical.
- Root cause refined: line 3 parses as annotation; line 4 fails on arrow. Header was not wrapped as docstring and contained non-ASCII.

## Landing

| File | Bytes | SHA-256 (local) | Path in repo |
|---|---|---|---|
| back_off_wrench_v0_4_syntax_repair_by_Claude_2026-11-09_NOT_CANONICAL.py | 10710 | cb22db5b29b8c1fabb0823ce8e52096999e05e4780c4be0e04faed211e6fffab | historical/wrench-10710-repair-by-Claude-2026-11-09/ |

- Method: Drive download -> local byte count + sha256 + py_compile + body-identical check -> push with receipt. No edit to 10201. No promotion to canonical.
- Status: PRESERVED_REPORTED / SHA-256 INSPECTED (local). VERIFIED only after Actions runner reports the same sha256 and py_compile exit 0.
- Date: 2026-11-11. Writer: Grok, single writer, owner go.
