#!/usr/bin/env python3
"""Generate Operator/cfg/operator_pre1810.dms from Operator/cfg/Operator.dms.

The bare point-literal syntax  yx(y, x)  /  xy(x, y)  was introduced in GeoDMS
v18.1.0 (engine commit 80932667) as the non-ambiguous replacement for the older
braced notation  {y, x}.  GeoDMS < 18.1.0 does not understand yx()/xy(), so the
Operator config fails to parse and the regression tests that run it (t010 and
t1742) break on 17.x builds.

This script writes a sibling config that is byte-identical to Operator.dms
except that every *bare* yx(...) / xy(...) point literal is rewritten to the
pre-18.1.0 brace notation.  point_yx(...) / point_xy(...) (available since
v14.9/14.10) are deliberately left untouched.  full.py routes t010/t1742 to
this file when the GeoDMS version under test is < 18.1.0.

Re-run this whenever Operator.dms changes:
    python batch/make_operator_pre1810.py
"""
import re
import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "Operator" / "cfg" / "Operator.dms"
DST = HERE.parent / "Operator" / "cfg" / "operator_pre1810.dms"

# Operate on raw bytes: the file is CRLF and contains non-ASCII bytes; this
# keeps line endings/encoding byte-exact and only the ASCII yx()/{} change.
data = SRC.read_bytes()

# Bare xy( (x-first) would map to the REVERSED brace order {x2, x1}; there are
# none today (only yx( is used). Fail loudly if that ever changes so nobody
# silently gets the argument order wrong.
n_xy = len(re.findall(rb"(?<![_a-zA-Z])xy\(", data))
if n_xy:
    sys.exit(f"ERROR: {n_xy} bare xy( found; extend this script to emit {{x,y}}->{{y,x}} reversed before regenerating.")

# yx(y, x) -> {y, x}. Args are plain numerics with no nested parens (verified),
# so [^()]+ captures exactly one literal's contents. The lookbehind keeps
# point_yx( untouched.
out, n = re.subn(rb"(?<![_a-zA-Z])yx\(([^()]+)\)", rb"{\1}", data)

banner = (
    b"// AUTO-GENERATED from Operator.dms by batch/make_operator_pre1810.py -- DO NOT EDIT BY HAND.\r\n"
    b"// Pre-18.1.0 GeoDMS variant: bare point literals rewritten to the brace {y,x} notation.\r\n"
    b"// Edit Operator.dms and re-run the script instead.\r\n"
)
DST.write_bytes(banner + out)
print(f"replaced {n} bare yx() literals; wrote {DST.name} ({len(banner) + len(out)} bytes)")
