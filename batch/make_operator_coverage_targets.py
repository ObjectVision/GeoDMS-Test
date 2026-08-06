#!/usr/bin/env python3
"""Genereer batch/generic/operator_coverage_targets.txt uit de GeoDMS-wiki.

De wiki-categoriepagina's <Categorie>-functions.md sommen de gedocumenteerde
operatoren op als [[naam]] / [[weergave|paginanaam]]-links. Die paginanamen
vormen de doellijst "ondersteunde operatoren" waartegen het t010-rapport de
testdekking meet (zie _append_t010_coverage in batch/generic/regression.py).

Gebruik:
    git clone --depth 1 https://github.com/ObjectVision/GeoDMS.wiki.git <dir>
    python batch/make_operator_coverage_targets.py <dir>
"""
import io
import pathlib
import re
import sys

if len(sys.argv) != 2:
    sys.exit(__doc__)
WIKI = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(__file__).resolve().parent / "generic" / "operator_coverage_targets.txt"

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
LINK = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]")
# structurele paginaverwijzingen in de intro-zinnen, geen operatoren
NOISE = {"functions", "data item", "domain unit", "values unit", "argument",
         "expression", "operators and functions", "unit", "subitem"}

targets = {}
for page in sorted(WIKI.glob("*-functions.md")):
    category = page.name[:-len("-functions.md")].replace("-", " ")
    text = io.open(page, encoding="utf-8", errors="replace").read()
    for m in LINK.finditer(text):
        name = (m.group(2) or m.group(1)).strip()
        if not IDENT.match(name) or name.lower() in NOISE:
            continue
        targets.setdefault(name.lower(), (name, category))

lines = [
    "# Gedocumenteerde GeoDMS-operatoren (doellijst voor de t010-testdekking).",
    "# GEGENEREERD door batch/make_operator_coverage_targets.py uit de wiki-",
    "# categoriepagina's *-functions.md -- niet met de hand bewerken, her-genereer",
    "# na wiki-wijzigingen. Formaat: naam<TAB>wiki-categorie.",
]
for low in sorted(targets):
    name, category = targets[low]
    lines.append(f"{name}\t{category}")
io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print(f"{len(targets)} gedocumenteerde operatoren uit {len(list(WIKI.glob('*-functions.md')))} categoriepagina's -> {OUT.name}")
