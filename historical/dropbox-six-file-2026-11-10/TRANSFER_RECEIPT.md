# Transfer Receipt — Dropbox six-file consolidated folder -> cup-horizon2

Owner Decision 7 (D7), leg 3. Owner ruling 2026-11-11: leg 3 stays OPEN until bytes land; owner copied the six files from the Dropbox Horizon-Consolidated-Review folder to Google Drive (2026-11-11 ~19:30-19:40 UTC); Vibe migrated Drive -> this repo with byte guards and read-back. This receipt closes the transfer-receipt gap the Drive Index and Receipts Log marked MISSING.

## Files (byte counts from the Drive Index, PRESERVED_REPORTED until now)

| File | Reported count | Landed bytes | Match | md5 (this transfer, real tool) |
|---|---|---|---|---|
| back_off_wrench_v0_4_located.py | 10,201 | 10,201 | YES | 5c1366809e8be06bb8f58a30484b9546 |
| horizon_valve_v4.py (located 8201) | 8,201 | 8,201 | YES | c475ed49feca4e669a58922f7f4f5709 |
| horizon_nonlinear_v1_3_1.py | 17,666 | 17,666 | YES | 9696562e1e640b7be77ef55170603444 |
| phase_space_caliper_v3_1_1_located.py | 6,953 | 6,953 | YES | 11fac960461b26b475e5fa4e27bf85e1 |
| CUP_HARNESS_CONTRACT.md | 6,576 | **6,621** | **NO — +45** | 593e72c405d8a92447b87b728b6f57ab |
| notion_10k_manifest_final.json | 1,474 | 1,474 | YES | 34d6c5a923072c8a4445c4b18fa760f0 |

- horizon_nonlinear_v1_2_1_PATCHED_INSPECTED.py: NOT FOUND in the folder, not substituted (per standing rule). Still MISSING.
- **Contract discrepancy, flagged not reconciled:** the landed CUP_HARNESS_CONTRACT.md is 6,621 B vs the 6,576 B Dropbox draft count. It is recorded as its own byte-state (contract-6621, md5 593e72c4); no attempt was made to explain or normalize the 45 bytes. The 6,576-byte draft state remains historical; contract-9203 (rulings-applied) remains the current VERIFIED contract in cup-code.
- All six files: no BOM, LF line endings, pushed as-is. Status: PRESERVED (md5 INSPECTED this transfer); sha256 PENDING real tool; nothing promoted to VERIFIED by this migration.
- Method: Drive download artifacts -> byte-guarded push -> read-back verification. No transcription, no reconstruction from counts.
- Date: 2026-11-11. Writer: Vibe (Dawn Ledger), single writer, owner go.
