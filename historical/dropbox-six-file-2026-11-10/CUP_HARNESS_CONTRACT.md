# CUP_HARNESS_CONTRACT.md, v0.1

Line 1: This file specifies the audit harness for a deterministic trajectory. It does not specify a state-transition function; none exists in the current bytes.

Scope: Operational definition of the audit harness in horizon_nonlinear_v1_3_2.py, back_off_wrench.py, and horizon_valve_v4.py, PLAIN, reference-pinned. This is layer (a): a deterministic verification harness. It is not layer (b): no state-transition function is defined here, and none exists in the current bytes.

### 1. Objects

- ticks, x0, eps | harness inputs, int greater than 0, float, float | sourced from active wrench branch, data, with defaults_used recorded when absent
- threads | 3-tuple of dicts, x float, v float, one each for logistic, blowup, stable | each is closed-form function of t, x0, eps | no inter-tick recurrence
- phase_sig | list of thread x for thread in threads | length-3 float vector
- det, centered_det, centroid, status | returned by caliper.measure_tick(threads) | PIN: phase_space_caliper sha256
- ledger entry | state, context, hash hex, prev_hash hex | hash computed by valve._compute_hash(state, context, prev_hash) with genesis 0 repeated 64 | PIN: horizon_valve_v4 sha256
- TensionEvent | index, kind, magnitude, detail, confidence | kind in PHASE_SHEAR, JACOBIAN_SPIKE, CRYPTO_SHEAR, MALFORMED_RECORD | UNRESOLVED_HASH_CONTRACT is deferred to wrench v0.5, not in v1.3.2 gate

### 2. S_t, what the harness logs per tick

Not a state in the dynamical-systems sense. Per tick t, the harness logs:

- state.tick | t | int
- state.r | L2 distance of phase_sig_t from phase_sig_0 | float
- state.x_blowup | blowup x clipped to plus or minus CLIP_MAG | float
- state.dt_eff | 0.01 divided by 1 plus 0.1 times blowup x | float
- context.t_arc_length | cumulative L2 distance of phase_sig_t from phase_sig_{t-1} | float
- context.t_pole_analytic | 1 divided by x0 times eps | float
- context.clipping | first clipping entry at t, or null | dict
- context.loom_slice, context.anomaly | see bytes | dict

The state is fully determined by t, x0, eps and the deterministic thread schedules. There is no feedback from $S_t$ into $S_{t+1}$.

### 3. T, what generates the trajectory

$T(t) = t+1$. That is the entire transition rule. Threads are evaluated at each tick from closed-form expressions. blowup x has a pole at $t_{pole} = 1 / (x0 \cdot eps)$ and is clipped for numerical safety. This is the only source of nonlinearity in the current bytes.

GAP: If intent is layer (b), T must be replaced by a genuine recurrence, and the harness contract below must be re-derived. Not in scope for v0.1.

### 3.1 What would be required to claim layer (b)

To claim layer (b), a future contract must provide all of the following, and re-pin:

- Recurrence: $S_{t+1} = T(S_t, O_t)$, where $S_t$ includes ledger state, not only t
- Feedback: observables $O_t$ feed into the next step, not only into the audit log
- Noise boundary: noise enters as observable perturbation to the ledger, measured by the wrench, logged by the valve, never inside T
- Gate re-derivation: Section 5 gate re-derived for the new T, with new thresholds justified, not carried over
- New pins: new sha256 pins for every file changed, old pins marked historical

Until those exist, layer (b) is aspiration, not claim. This contract claims layer (a) only.

### 4. O, observable extraction

- O_phase(t) | phase_sig_t | 3-vector
- O_radial(t) | r_t | distance from tick 0
- O_jac(t) | context.anomaly.cross_jacobian_det | from caliper | PIN
- O_arc(t) | t_arc_length | cumulative path length

### 5. A, anomaly predicates and the gate

Applied by back_off_wrench.reverse_walk:

- PHASE_SHEAR | L2 distance of phase_sig_t from phase_sig_{t-1} greater than 50.0 | magnitude is L2 jump
- JACOBIAN_SPIKE | jacobian_delta of det_t, det_{t-1} greater than 10.0 | magnitude is delta
- CRYPTO_SHEAR | recomputed hash not equal to stored hash | magnitude inf
- MALFORMED_RECORD | entry not dict, missing hash, or processing error | magnitude inf
- UNRESOLVED_HASH_CONTRACT | valve._compute_hash absent | magnitude inf | deferred to wrench v0.5, not in v1.3.2 gate

Gate, v1.3.2: actual_shear is set of e.index for e in reverse_events where e.kind in PHASE_SHEAR, JACOBIAN_SPIKE. predicted_window is set of round(t_pole) minus 1, round(t_pole), round(t_pole) plus 1, intersected with range(ticks). contained_r is actual_shear subset of predicted_window. Verdict: PASSED if contained, FAILED if not contained, INCONCLUSIVE if either input is empty. mean_coherence is logged, threshold 0.85 is recorded as placeholder, not enforced, until evaluate_single_event lands with graded semantics. GAP: evaluate_single_event is stubbed, exits 3, its semantics, flat 1.0 vs graded, are undecided and shape what mean_coherence would mean.

Negative control: shifts actual_shear by plus w_max minus w_min plus 1, smoke, and plus 1, near, and requires the smoke to fall outside the window.

### 6. What this contract does NOT claim

- Not a claim that the harness detects unknown nonlinearities. The pole is analytic. The harness localizes a known feature. A bench, not a discovery tool.
- Not a claim of layer (b) semantics. No recurrence, no noise injection, no field dynamics.
- Not a claim that mean_coherence is a meaningful measure until evaluate_single_event lands and its semantics are pinned.
- Not a claim that stochastic execution is auditable under this contract. If noise is later introduced, it must enter as observable perturbation to the ledger, measured by the wrench, logged by the valve, never inside T. Otherwise write_predictions, load_predictions fingerprinting and the sha256 chain break by construction.
- Not a claim about valve verify(). Drive copies inspected show verify_integrity, log_state, _compute_hash, no bare verify(). A different valve byte-state claiming bare verify() is forked per byte-state until its sha256 plus grep paste crosses. This contract pins the PLAIN copy by reference below.

### 7. Pins, fill on real-tool read

- horizon_nonlinear_v1_3_2.py | 27218 bytes | md5 dd964d95 | sha256 PENDING | IN DRIVE, BENCH-PENDING, ID 1n7nEnaFszqV3AQWLqCptcEyIexTv_f3I
- back_off_wrench.py | 11818 bytes | md5 f3e94157 | sha256 PENDING | PRESERVED, v0.5 deferrals in header, _l2 and verify_forward notes live here, not in v1_3_2
- horizon_valve_v4.py, PLAIN, reference pin | 3321 bytes | md5 7f2ba5ae | sha256 PENING (PENDING) | bench-paired by reference, ID 1Tyz4shNXnrVhLHrlMUEXiccAKI-uuEwl, no duplicate
- phase_space_caliper.py | bytes unknown | md5 unknown | sha256 PENDING | PIN only, internals not described here
