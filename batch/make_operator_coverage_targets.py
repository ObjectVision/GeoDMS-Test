#!/usr/bin/env python3
"""Genereer batch/generic/operator_coverage_targets.txt uit de GeoDMS-wiki.

De wiki-categoriepagina's <Categorie>-functions.md sommen de gedocumenteerde
operatoren op; sommige categorieen (Geometric) delegeren naar subpagina's
("point operators", "arc-polygon operators", ...) die ook worden gevolgd.
Geoogst worden [[link]]-doelen EN -weergaven (beide kanten van [[weergave|doel]],
zodat variantvermeldingen als [[pcount_uint8|pcount]] meetellen), plus platte
variantnamen in bullets ("- pcount_uint8 - is the [[pcount]] variant ...").
Een '(...)'-staart in paginanamen (impedance_table(...)) wordt gestript.
Namen die geen operator-groep blijken, vallen in het rapport vanzelf in de
curatiesectie - te ruim oogsten is dus onschadelijk.

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
BULLET_NAME = re.compile(r"^\s*[-*]\s+([A-Za-z_][A-Za-z0-9_]*)\s+-\s")
NOISE = {"functions", "data item", "domain unit", "values unit", "argument",
         "expression", "operators and functions", "unit", "subitem",
         "point", "arc", "polygon", "points", "arcs", "polygons"}

def norm(name):
    """'impedance_table(...)' -> 'impedance_table'; None als geen identifier."""
    name = re.sub(r"\(\.{0,3}\)$", "", name.strip()).strip()
    if IDENT.match(name) and name.lower() not in NOISE:
        return name
    return None

def page_path(target):
    """Wiki-linkdoel -> md-bestand (spaties worden '-' in paginanamen)."""
    fn = WIKI / (target.replace(" ", "-") + ".md")
    return fn if fn.is_file() else None

targets = {}

def harvest(path, category):
    text = io.open(path, encoding="utf-8", errors="replace").read()
    for line in text.split("\n"):
        mb = BULLET_NAME.match(line)
        if mb:
            n = norm(mb.group(1))
            if n:
                targets.setdefault(n.lower(), (n, category))
        for m in LINK.finditer(line):
            for cand in (m.group(2), m.group(1)):
                if cand is None:
                    continue
                n = norm(cand)
                if n:
                    targets.setdefault(n.lower(), (n, category))

n_sub = 0
for page in sorted(WIKI.glob("*-functions.md")):
    category = page.name[:-len("-functions.md")].replace("-", " ")
    harvest(page, category)
    # subpagina's van het type "... operators" (bv. Geometric -> arc-polygon operators)
    text = io.open(page, encoding="utf-8", errors="replace").read()
    for m in LINK.finditer(text):
        target = (m.group(1) or "").strip()
        if re.search(r"(?i)operators?$", target):
            sub = page_path(target)
            if sub:
                harvest(sub, category)
                n_sub += 1

lines = [
    "# Gedocumenteerde GeoDMS-operatoren (doellijst voor de t010-testdekking).",
    "# GEGENEREERD door batch/make_operator_coverage_targets.py uit de wiki-",
    "# categoriepagina's *-functions.md en hun 'x operators'-subpagina's --",
    "# niet met de hand bewerken, her-genereer na wiki-wijzigingen.",
    "# Formaat: naam<TAB>wiki-categorie.",
]
for low in sorted(targets):
    name, category = targets[low]
    lines.append(f"{name}\t{category}")
io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print(f"{len(targets)} gedocumenteerde operatoren uit {len(list(WIKI.glob('*-functions.md')))} categoriepagina's + {n_sub} subpagina's -> {OUT.name}")
