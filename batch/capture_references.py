#!/usr/bin/env python3
"""Promote indicator reference VALUES from a trusted-build run into references.json.

The report (batch/generic/regression.py) judges every version's measured indicator value
against these references. This is a DELIBERATE "promote" step: run it once after a
trusted-build regression run. A normal test run NEVER writes references.json, so a real
regression can never silently rebaseline itself.

Only VALUE metrics (scalar indicators) are captured. Cell/diff tests (n_diff: t101/t200/
t301/t611/t810/...) keep their own recorded reference (.fss/.tif in TestReferenceFiles)
and are judged against 0 -- they are intentionally NOT written here.

SAFETY (this script used to be a footgun; see the guards below)
--------------------------------------------------------------
It previously rewrote the whole file from every *.result.json it found in the folder,
flattening the epoch maps ({name: {threshold: {v, src}}}) back to bare {name: value} and
silently rebaselining every other test in that folder. Now:

  * it MERGES into the existing file and preserves epoch maps, notes and flavor prefixes;
  * you must name the tests (--tests t020) or opt in explicitly with --all;
  * it is a DRY RUN unless you pass --write;
  * changing a value that is already recorded needs --force, so a regressing build cannot
    quietly overwrite a good baseline. Adding a new test/metric/epoch is free.

Usage:
    python capture_references.py <results_folder> --tests t020 --epoch 20.3.0 --build 20.3.0.m
    python capture_references.py <results_folder> --tests t020 ... --write
"""
import argparse
import glob
import json
import os
import re
import sys


def _load(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _dump(doc, path):
    """Serialise in the file's established layout: top-level keys at 2 spaces, one metric
    per line at 4, epoch map inline. Keeps promote-diffs to the lines that changed."""
    parts = []
    for key, val in doc.items():
        if not isinstance(val, dict):
            parts.append(f"  {json.dumps(key)}: {json.dumps(val, ensure_ascii=False)}")
            continue
        rows = [f"    {json.dumps(m, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}"
                for m, v in val.items()]
        parts.append(f"  {json.dumps(key)}: {{\n" + ",\n".join(rows) + "\n  }")
    text = "{\n" + ",\n".join(parts) + "\n}\n"
    json.loads(text)                      # never write something the report cannot read
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(text)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results_folder", help="version result folder holding <test>.result.json files")
    ap.add_argument("--tests", default="", help="comma-separated test names to promote (e.g. t020). Required unless --all")
    ap.add_argument("--all", action="store_true", help="promote EVERY test found in the folder (rarely what you want)")
    ap.add_argument("--epoch", default="0.0.0", help="version threshold this baseline starts at (default 0.0.0 = always)")
    ap.add_argument("--build", default="", help="label for the build the values come from (default: folder name)")
    ap.add_argument("--note", default="", help="why this baseline exists; shown on the report's 'ref' pill")
    ap.add_argument("--force", action="store_true", help="allow CHANGING values that are already recorded")
    ap.add_argument("--write", action="store_true", help="actually write; without this it is a dry run")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "generic", "references.json"))
    args = ap.parse_args()

    if not args.tests and not args.all:
        sys.exit("refusing to guess: name the tests with --tests t020 (or pass --all to take every test in the folder)")
    wanted = {t.strip() for t in args.tests.split(",") if t.strip()}

    files = sorted(glob.glob(os.path.join(args.results_folder, "result", "*.result.json"))) \
         or sorted(glob.glob(os.path.join(args.results_folder, "*.result.json")))
    if not files:
        sys.exit(f"no *.result.json found in {args.results_folder}")

    if not re.match(r"^\d+(\.\d+)*$", args.epoch):
        sys.exit(f"--epoch must be a version threshold like 20.3.0 (got {args.epoch!r})")
    build = args.build or os.path.basename(args.results_folder.rstrip("/\\"))

    doc = _load(args.out)
    adds, changes, same, skipped = [], [], [], []
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                measured = json.load(f)
        except (OSError, ValueError) as e:
            print(f"  skip {os.path.basename(fp)}: {e}")
            continue
        test = measured.get("test")
        if not test:
            continue
        if not args.all and test not in wanted:
            skipped.append(test)
            continue
        for m in measured.get("metrics", []):
            if "value" not in m or "name" not in m:
                continue          # cell/diff metric: judged against its own recorded reference
            entry = {"v": m["value"], "src": args.epoch, "captured_from": build}
            if args.note:
                entry["note"] = args.note
            cur = doc.setdefault(test, {}).setdefault(m["name"], {})
            if not isinstance(cur, dict):        # legacy bare value -> lift into an epoch map
                cur = {"0.0.0": {"v": cur, "src": "unknown"}}
                doc[test][m["name"]] = cur
            old = cur.get(args.epoch)
            if old is None:
                adds.append((test, m["name"], m["value"]))
                cur[args.epoch] = entry
            elif old.get("v") == m["value"]:
                same.append((test, m["name"]))
            else:
                changes.append((test, m["name"], old.get("v"), m["value"]))
                if args.force:
                    cur[args.epoch] = entry

    unknown = wanted - {t for t, *_ in adds} - {t for t, *_ in changes} - {t for t, *_ in same}
    if unknown:
        sys.exit(f"no value metrics found for: {', '.join(sorted(unknown))} (cell/diff tests are not captured here)")

    print(f"epoch {args.epoch}  from {build}  ->  {args.out}")
    for t, n, v in adds:            print(f"  + {t} / {n}: {v}")
    for t, n in same:               print(f"  = {t} / {n}: unchanged")
    for t, n, o, v in changes:      print(f"  ! {t} / {n}: {o} -> {v}")
    if skipped:
        print(f"  ({len(set(skipped))} test(s) in the folder not selected: {', '.join(sorted(set(skipped)))})")

    if changes and not args.force:
        sys.exit("\nrefusing to overwrite recorded baselines (listed with ! above).\n"
                 "A changed value can mean the build under test regressed -- verify against another\n"
                 "version first, then re-run with --force if the new value is genuinely the better one.")
    if not args.write:
        print("\ndry run; nothing written. Re-run with --write to apply.")
        return
    if not (adds or (changes and args.force)):
        print("\nnothing to change.")
        return
    _dump(doc, args.out)
    print(f"\nwrote {args.out}  (+{len(adds)} added, {len(changes) if args.force else 0} changed)")


if __name__ == "__main__":
    main()
