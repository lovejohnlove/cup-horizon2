#!/usr/bin/env python3
"""D2 bench smoke: repair 10710 + PLAIN 3321. Exit 0 on pass."""
import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPAIR = HERE / "back_off_wrench_v0_4_syntax_repair_by_Claude_2026-11-09_NOT_CANONICAL.py"
PLAIN = HERE / "horizon_valve_v4_PLAIN.py"
REPAIR_SHA = "cb22db5b29b8c1fabb0823ce8e52096999e05e4780c4be0e04faed211e6fffab"
PLAIN_SHA = "ed1e81bd70201a8795579725c0bb0b968eb98c30458202f83d5e667200a68a91"
REPAIR_BYTES = 10710
PLAIN_BYTES = 3321

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    r = REPAIR.read_bytes()
    p = PLAIN.read_bytes()
    if len(r) != REPAIR_BYTES or hashlib.sha256(r).hexdigest() != REPAIR_SHA:
        print("FAIL: repair byte/sha guard")
        return 1
    if len(p) != PLAIN_BYTES or hashlib.sha256(p).hexdigest() != PLAIN_SHA:
        print("FAIL: plain byte/sha guard")
        return 1
    print("byte + sha256 guards: PASS")

    valve_mod = load("plain_valve", PLAIN)
    wrench_mod = load("repair_wrench", REPAIR)
    valve = valve_mod.HorizonValveV4()
    wrench = wrench_mod.BackOffWrench(valve)

    r0 = wrench.snap_check()
    if not r0.get("snaps_smoothly"):
        print("FAIL: empty chain did not snap smoothly:", r0.get("verdict"))
        return 2
    print("empty chain: PASS")

    valve.log_state({"x": 1.0}, {"label": "step1"})
    r1 = wrench.snap_check()
    if not r1.get("snaps_smoothly") or not r1.get("forward_ok"):
        print("FAIL: one-step chain:", r1.get("verdict"))
        return 3
    print("one-step chain: PASS")
    print("SANDBOX SMOKE: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
