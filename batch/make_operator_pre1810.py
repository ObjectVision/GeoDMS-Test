#!/usr/bin/env python3
"""Generate the pre-18.1.0 variant of the Operator config.

The bare point-literal syntax  yx(y, x)  /  xy(x, y)  was introduced in GeoDMS
v18.1.0 (engine commit 80932667) as the non-ambiguous replacement for the older
braced notation  {y, x}.  GeoDMS < 18.1.0 does not understand yx()/xy(), so the
Operator config fails to parse and the regression tests that run it (t010 and
t1742) break on 17.x builds.

Operator.dms is split into #include parts under Operator/cfg/Operator/.  This
script writes operator_pre1810.dms plus operator_pre1810/<part>.dms for every
part the stem includes, byte-identical except that every *bare* yx(...) point
literal is rewritten to the pre-18.1.0 brace notation.  The include lines keep
working unchanged because GeoDMS resolves them relative to the subdirectory
named after the including file.  point_yx(...) / point_xy(...) (available since
v14.9/14.10) are deliberately left untouched.  full.py routes t010/t1742 to
this variant when the GeoDMS version under test is < 18.1.0, and regenerates it
automatically when it is missing or older than any source file.

Line endings are normalized to LF on write, so the output depends only on the
CONTENT of the sources and not on how they happen to be checked out.  The
sources are .dms files with no .gitattributes entry, so core.autocrlf decides:
on Windows they arrive CRLF, on Linux LF.  Copying those bytes through made the
generated files CRLF on one platform and LF on the other, and because git skips
its CRLF->LF normalization for a path whose index blob already contains CRLF,
that difference did not wash out on `git add` -- regenerating on the other
platform rewrote all ~14k lines of the mirror as a pure line-ending diff.
Emitting LF unconditionally keeps the index blobs free of CRLF, which in turn
lets git normalize consistently from either platform.
"""
import re
import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
CFG = HERE.parent / "Operator" / "cfg"
SRC_STEM = CFG / "Operator.dms"
SRC_DIR = CFG / "Operator"
DST_STEM = CFG / "operator_pre1810.dms"
DST_DIR = CFG / "operator_pre1810"

BANNER = (
    b"// AUTO-GENERATED from Operator.dms (+includes) by batch/make_operator_pre1810.py -- DO NOT EDIT BY HAND.\n"
    b"// Pre-18.1.0 GeoDMS variant: bare point literals rewritten to the brace {y,x} notation.\n"
    b"// Edit Operator.dms / Operator/*.dms and re-run the script instead.\n"
)

def normalize_eol(data: bytes) -> bytes:
    """CRLF -> LF, so the output is the same whatever the checkout did to the
    sources (see the module docstring).  Byte-safe for the non-ASCII content in
    these files: a CRLF pair cannot occur inside a UTF-8 multi-byte sequence,
    whose continuation bytes are all >= 0x80.  Lone CRs are left alone rather
    than guessed at; there are none, and rewriting one inside a string literal
    would be a silent content change."""
    return data.replace(b"\r\n", b"\n")

STRING_LITERAL = re.compile(rb"'[^'\r\n]*'|\"[^\"\r\n]*\"")

def mask_string_literals(data: bytes) -> bytes:
    """A same-length copy with the INSIDE of every quoted string blanked out.

    Only point literals are to be scanned and rewritten; text that merely
    mentions the notation must be left alone.  Since GeoDMS 20.14.0 renders a
    point as xy(x; y), expected-value strings spell that out -- e.g.
    UnitFunctions/CrsUnit_wrap compares against 'xy(1; 0)|xy(2; 1)' -- and an
    unmasked scan reads those as bare literals and aborts the run.  Offsets are
    preserved so matches found here index straight back into the original."""
    return STRING_LITERAL.sub(
        lambda m: m.group(0)[:1] + b"\x00" * (len(m.group(0)) - 2) + m.group(0)[-1:], data)

def transform(data: bytes, name: str):
    """Operate on raw bytes: these files contain non-ASCII bytes, so this keeps
    the encoding byte-exact and changes only the ASCII yx()/{} spelling.  Line
    endings are normalized first, so the yx() rewrite and the output both see
    LF regardless of platform."""
    data = normalize_eol(data)
    masked = mask_string_literals(data)
    n_xy = len(re.findall(rb"(?<![_a-zA-Z])xy\(", masked))
    if n_xy:
        sys.exit(f"ERROR: {n_xy} bare xy( in {name}; extend this script to emit {{x,y}}->{{y,x}} reversed first.")

    # matched on `masked`, spliced from `data`, so the blanking never reaches the output
    out, pos, n = bytearray(), 0, 0
    for m in re.finditer(rb"(?<![_a-zA-Z])yx\(([^()]+)\)", masked):
        out += data[pos:m.start()] + b"{" + data[m.start(1):m.end(1)] + b"}"
        pos, n = m.end(), n + 1
    out += data[pos:]
    return bytes(out), n

stem_bytes = SRC_STEM.read_bytes()
part_names = re.findall(rb"#include <([^>\r\n]+)>", stem_bytes)
part_names = [n.decode("latin-1") for n in part_names]

DST_DIR.mkdir(exist_ok=True)
for stale in DST_DIR.glob("*.dms"):
    if stale.name not in part_names:
        stale.unlink()

total = 0
n_files = 0
for name in part_names:
    src = SRC_DIR / name
    out, n = transform(src.read_bytes(), name)
    (DST_DIR / name).write_bytes(BANNER + out)
    total += n
    n_files += 1
out, n = transform(stem_bytes, SRC_STEM.name)
DST_STEM.write_bytes(BANNER + out)
total += n
print(f"replaced {total} bare yx() literals; wrote {DST_STEM.name} + {n_files} parts in {DST_DIR.name}/")
