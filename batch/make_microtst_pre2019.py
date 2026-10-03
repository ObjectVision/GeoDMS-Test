#!/usr/bin/env python3
"""Generate the pre-20.19 variant of the MicroTst config (t1642).

MicroTst/functions.dms uses the function/instantiate syntax of GeoDMS >= 20.19
("function g(...) -> parameter<float32>", "instantiate g(x)").  That is syntax,
not an operator, so GeoDmsVersion() cannot gate it: an older GeoDmsGuiQt crashes
with an access violation (<= 20.8) or hangs (20.12-20.17) while loading a config
that contains it -- t1642 did on every build below 20.19 from 2026-08-25 on,
while its report cells stayed green from earlier runs.

This script writes MicroTst_pre2019.dms plus MicroTst_pre2019/<part>.dms for
every part the stem includes, byte-identical except that the
`#include <functions.dms>` line is replaced by a comment.  The other include
lines keep working unchanged because GeoDMS resolves them relative to the
subdirectory named after the including file.  full.py routes t1642 to this
variant when the GeoDMS version under test is < 20.19.0, and regenerates it
automatically when it is missing or older than any source file.

Line endings are normalized to LF on write, for the reason explained in
make_operator_pre1810.py: the output must depend only on the CONTENT of the
sources, not on how the checkout spelled their line endings.
"""
import re
import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
CFG = HERE.parent / "Operator" / "cfg"
SRC_STEM = CFG / "MicroTst.dms"
SRC_DIR = CFG / "MicroTst"
DST_STEM = CFG / "MicroTst_pre2019.dms"
DST_DIR = CFG / "MicroTst_pre2019"
DROP = b"functions.dms"

BANNER = (
    b"// AUTO-GENERATED from MicroTst.dms (+includes) by batch/make_microtst_pre2019.py -- DO NOT EDIT BY HAND.\n"
    b"// Pre-20.19 GeoDMS variant: the include of MicroTst/functions.dms (function/instantiate syntax) is left out.\n"
    b"// Edit MicroTst.dms / MicroTst/*.dms and re-run the script instead.\n"
)
INCLUDE = re.compile(rb"^([ \t]*)#include[ \t]*<([^>\r\n]+)>[ \t]*$", re.M)

def transform(data: bytes, name: str):
    """LF-normalized copy in which the functions.dms include is replaced by a
    comment.  Returns (bytes, names of the includes that stay, number dropped)."""
    data = data.replace(b"\r\n", b"\n")
    keep, dropped = [], 0
    def sub(m):
        nonlocal dropped
        if m.group(2).strip() == DROP:
            dropped += 1
            return m.group(1) + b"// pre-20.19 mirror: #include <functions.dms> left out (function/instantiate syntax needs GeoDMS >= 20.19)"
        keep.append(m.group(2).strip().decode("latin-1"))
        return m.group(0)
    out = INCLUDE.sub(sub, data)
    return out, keep, dropped

stem_out, part_names, n_dropped = transform(SRC_STEM.read_bytes(), SRC_STEM.name)
if n_dropped != 1:
    sys.exit(f"ERROR: expected exactly one #include <{DROP.decode()}> in {SRC_STEM.name}, found {n_dropped}")

DST_DIR.mkdir(exist_ok=True)
for stale in DST_DIR.glob("*.dms"):
    if stale.name not in part_names:
        stale.unlink()
for name in part_names:
    part_out, nested, part_dropped = transform((SRC_DIR / name).read_bytes(), name)
    if nested or part_dropped:
        # a nested include would resolve relative to <part-name>/ in the mirror too; mirror
        # that subtree before relying on it
        sys.exit(f"ERROR: {name} has includes of its own ({nested}); extend this script to mirror them.")
    (DST_DIR / name).write_bytes(BANNER + part_out)
DST_STEM.write_bytes(BANNER + stem_out)
print(f"wrote {DST_STEM.name} + {len(part_names)} parts in {DST_DIR.name}/ (functions.dms left out)")
