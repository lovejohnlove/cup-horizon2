# back_off_wrench repair 10710

**Status:** NOT_CANONICAL, new byte state, header-only syntax repair — **VERIFIED by Actions runner**  
**Bytes:** 10710  
**SHA-256:** cb22db5b29b8c1fabb0823ce8e52096999e05e4780c4be0e04faed211e6fffab  
**md5:** 1f264ba017c68809346513a3ccc21499  
**py_compile:** exit 0  
**Runner confirmation:** cup-horizon2 Actions Run #8, head 3195f9d, 2026-11-12  
https://github.com/lovejohnlove/cup-horizon2/actions/runs/43207211179  
**Relation to 10201:** header-only fix; code body from first `from typing` onward is byte-for-byte identical (8221 bytes). Located 10201 remains historical defective byte state; do not delete, overwrite, or edit it.  
**Bench:** accepted as D2 bench candidate (repair 10710 + valve PLAIN 3321 from cup-code).  
**Canonical:** NO. Do not promote. Do not merge into 10201.  
**Landing history:** Initial push truncated (~2831 B, SHA e7bfaa86…). Corrective re-land 2026-11-11 restored full 10710 B (commit 1bf89875). Runner VERIFIED 2026-11-12.  
**Date:** 2026-11-12. Writer: Grok under owner ruling.
