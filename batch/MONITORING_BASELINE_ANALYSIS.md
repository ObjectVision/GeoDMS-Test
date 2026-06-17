# Monitoring tests — cross-version baseline analysis (2026-06-17, overnight)

Goal: decide which monitoring-test values can be **safely baselined** as a reference
(`expected` in `regression.py: TEST_TOLERANCES`). Rule (never mask a failure): only
baseline a value that is **stable across pre-20 builds**; never baseline from the
current/possibly-regressing build alone; a drifting value is baselined from its
**trusted (pre-20) value** with a tolerance tight enough to surface a real change.

Source: values extracted from `<results>/<ver>/<test>.txt` across 17.4.6 / 18.1.2 /
19.0.0 / 20.1.0.m (+ 20.1.0.l where present).

## ⚠️ Regression candidate (must surface, do NOT mask)

**t910 `Sum Diff TA wFlood`**: `-1,050,740,032` (17.4.6→19.0.0, stable) → **`-1,051,036,480`
(20.1.0.m & .l)** — a **~296,448 (0.028%) change introduced at 20.1.0**. Could be a real
regression or a float32 accumulation-order shift, but it is NOT explained.
**Action:** baseline `expected = -1050740032` (trusted pre-20) with a tight tolerance
(0.01%) so **20.1.0 FAILS** → you review whether it's noise (relax) or a real bug.

## Safe to baseline (stable across pre-20 → 20.1.0)

| test | metric(s) | value (baseline) | note |
|---|---|---|---|
| t010 | operator tests | (all pass) | count test; verdict = # failing == 0 |
| t300 | spot-checks | (8 inline checks) | already a real comparison; verdict = # failing |
| t410 | count / mean / max / min / modus | 176064 / 154.73293 / 239.99937 / 2.1098754 / 145 | all stable |
| t720 | Population / BuiltUp cells / BuiltUp area / Pop urban centre | 578020431 / 12653121 / 197180.27 / 270776737 | all stable |
| t910 | Sum NetworkEfficiency / TP_Flood / Diff TP wFlood | 334.64032 / 22439.209 / -6906.0117 | stable (tol 0.01% for float noise) |

## Benign drift (baseline from trusted value, tolerance absorbs it)

| test | metric | values | plan |
|---|---|---|---|
| t710 | Population 2100 | 894019008 (all) | STABLE — baseline exact-ish |
| t710 | Urban 2100 | 234615 (Win) / 234616 (.l) | baseline 234615, tol ~0.01% (Win/Linux +1 cell) |
| t710 | Buildup area 2100 | 0.034366544 (Win) / 0.034366667 (.l) | baseline 0.034366544, tol ~0.01% |
| t910 | Sum PotentialAccess | 46703.84 (pre-20) / 46703.844 (20.1.0) | baseline 46703.84, tol 0.01% (passes) |

## NOT baselinable yet → stay `reference_pending` (honest, never green)

- **t405_2 / t405_3** (NetworkModel PBL, 18 metrics each): only 20.1.0.m/.l data exists
  (no pre-20). Baselining from 20.1.0 alone could mask a 20.1.0 regression → leave pending
  until a pre-20 run confirms stability (or you confirm 20.1.0 is the intended baseline).
- **t641_3** (RSopen, heavy): no cross-version data collected → pending.
- **t151**: lives in `bl_rd_conversie/root.dms` (your parallel edit) → left untouched.

## Tolerance convention
- Integer counts (t010, t410 count, t720 counts): tolerance 0 (exact).
- Float sums/means: tolerance 0.01% (absorbs float32 noise) — **except** where a tight
  tolerance is needed to surface a candidate regression (t910 Diff TA wFlood).
