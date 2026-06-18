#!/usr/bin/env python3
"""Capture indicator reference VALUES from a trusted-build run into references.json.

The report (batch/generic/regression.py) judges every version's measured indicator value
against these references at 0% tolerance (exact). This is a DELIBERATE "promote" step: run
it once after a trusted-build regression run (e.g. 17.4.6). A normal test run NEVER writes
references.json, so a real regression can never silently rebaseline itself.

Only VALUE metrics (scalar indicators, e.g. t910/t410/t710/t720 and the t100/t102 connect
counts) are captured. Cell/diff tests (n_diff: t101/t200/t301/t611/t810/...) keep their own
recorded reference (.fss/.tif in TestReferenceFiles) and are judged against 0 -- they are
intentionally NOT written here.

Usage:
    python capture_references.py <results_folder> [--build 17.4.6] [--out <path>]
e.g.
    python capture_references.py C:/LocalData/GeoDMS-Test/Regression/17_4_6 --build 17.4.6
"""
import argparse
import glob
import json
import os
import sys


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results_folder", help="version result folder holding <test>.result.json files")
    ap.add_argument("--build", default="17.4.6", help="label for the trusted build the values come from")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "generic", "references.json"))
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.results_folder, "*.result.json")))
    if not files:
        sys.exit(f"no *.result.json found in {args.results_folder}")

    refs = {}
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                doc = json.load(f)
        except (OSError, ValueError) as e:
            print(f"  skip {os.path.basename(fp)}: {e}")
            continue
        test = doc.get("test")
        if not test:
            continue
        vals = {m["name"]: m["value"] for m in doc.get("metrics", []) if "value" in m and "name" in m}
        if vals:
            refs[test] = vals

    out_doc = {
        "_comment": "Indicator reference VALUES captured from a trusted GeoDMS build. The report "
                    "(batch/generic/regression.py) judges each version's measurement against these "
                    "at 0% tolerance. Regenerate deliberately via batch/capture_references.py after "
                    "a trusted-build run; a normal test run never writes this file.",
        "_captured_from": args.build,
        "_source_folder": os.path.basename(args.results_folder.rstrip("/\\")),
    }
    for t in sorted(refs):
        out_doc[t] = refs[t]

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out_doc, f, indent=2)
        f.write("\n")
    n_metrics = sum(len(v) for v in refs.values())
    print(f"wrote {args.out}")
    print(f"  build={args.build}  tests={len(refs)}  metrics={n_metrics}: {', '.join(sorted(refs))}")


if __name__ == "__main__":
    main()
