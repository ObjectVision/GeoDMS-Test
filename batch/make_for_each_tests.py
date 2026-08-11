#!/usr/bin/env python3
"""Genereer Operator/cfg/Operator/ForEach.dms: een structurele test per
geregistreerde for_each_*-variant.

De for_each-familie is EEN metascript-constructie met ~1632 geregistreerde
suffixcombinaties (zie de wiki-pagina For_each voor de grammatica). Beleid
(Jip, 2026-08-11): ook al die varianten moeten werken. Deze generator leest de
operator-groependumps van de geteste GeoDMS-versies (t010_operator_groups.txt),
neemt de unie van alle for_each_*-namen, ontleedt elke suffix volgens de
grammatica en genereert per variant een container die de variant aanroept met
bij de tokens passende argumenten, plus een structurele toets: de gegenereerde
container moet precies de twee verwachte subitems (x0, x1) hebben. Varianten
zonder domein/waardetype-token krijgen ook een waardetoets (x0 = 7).

De gegenereerde items zelf worden bewust NIET doorgerekend (alleen de
subitem-namen worden opgevraagd), zodat storage-/sql-/cdf-tokens geen echte
bestanden of databronnen nodig hebben.

Suffixgrammatica (wiki For_each):
  for_each_n [e|t] [i] ( d[n] v[n] [vcs|vcp] | x[n] ) [l] [d] [a[t]] [s] [c] [u]
De tweede 'd' (description) is te onderscheiden van de domein-'d' doordat de
domein-'d' altijd door (n en/of) 'v' gevolgd wordt.

Argumentsynthese per token (volgorde = tokenvolgorde):
  n   -> Src/name                  e  -> Src/expr ('uint32(7)')
  t   -> SimpleT (template)        i  -> Src/ic ('true')
  d   -> void                      dn -> DomC, Src/name
  v   -> uint32 (waardetype-unit)  vn -> ValC, Src/name
  vcs/vcp -> geen extra argument (compositiemarkering); v-arg wordt PntU
  x   -> uint32                    xn -> XC, Src/name
  l   -> Src/lab                   d(escr) -> Src/descr
  a   -> Src/sn ('%localDataProjDir%/fe_probe_<naam>.txt')
  at  -> idem + 'str'              s  -> Src/sql
  c   -> Src/cdf                   u  -> Src/url

Draaien: python make_for_each_tests.py <dump1> [<dump2> ...]
Daarna: python make_operator_pre1810.py (de spiegel neemt het deel automatisch mee).
"""
import io
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DST = HERE.parent / "Operator" / "cfg" / "Operator" / "ForEach.dms"


def parse_suffix(sfx: str):
    """Ontleed een for_each-suffix in tokens; None als hij niet in de
    grammatica past."""
    toks = []
    i = 0
    n = len(sfx)

    def at(j):
        return sfx[j] if j < n else ""

    if at(0) != "n":
        return None
    toks.append("n")
    i = 1
    # e, i en t zijn onafhankelijk combineerbaar, in deze volgorde (empirisch:
    # de registraties bevatten o.a. neit..., nit..., net..., nt...)
    if at(i) == "e":
        toks.append("e")
        i += 1
    if at(i) == "i":
        toks.append("i")
        i += 1
    if at(i) == "t":
        if at(i + 1) == "n":
            toks.append("tn")
            i += 2
        else:
            toks.append("t")
            i += 1
    # domein/waarden-groep of x-groep; domein-'d' herkenbaar aan (n?)v erna
    if at(i) == "d" and (at(i + 1) == "v" or (at(i + 1) == "n" and at(i + 2) == "v")):
        if at(i + 1) == "n":
            toks.append("dn")
            i += 2
        else:
            toks.append("d")
            i += 1
        if at(i) != "v":
            return None
        if at(i + 1) == "n":
            toks.append("vn")
            i += 2
        else:
            toks.append("v")
            i += 1
        if sfx[i:i + 3] in ("vcs", "vcp"):
            toks.append(sfx[i:i + 3])
            i += 3
    elif at(i) == "x":
        if at(i + 1) == "n":
            toks.append("xn")
            i += 2
        else:
            toks.append("x")
            i += 1
    for opt in ("l", "d", "a", "s", "c", "u"):
        if at(i) == opt:
            if opt == "a" and at(i + 1) == "t":
                toks.append("at")
                i += 2
            elif opt == "d":
                # hier is 'd' altijd de description-eigenschap (de domein-'d'
                # is hierboven al geconsumeerd, herkenbaar aan de v erna)
                toks.append("d2")
                i += 1
            else:
                toks.append(opt)
                i += 1
    return toks if i == n else None


def args_for(toks, name):
    args = []
    vcs = "vcs" in toks or "vcp" in toks
    for t in toks:
        if t == "n":
            args.append("Src/name")
        elif t == "e":
            args.append("Src/expr")
        elif t == "t":
            args.append("SimpleT")
        elif t == "tn":
            args.append("TC")
            args.append("Src/name")
        elif t == "i":
            args.append("Src/ic")
        elif t == "d":
            args.append("void")
        elif t == "dn":
            args.append("DomC")
            args.append("Src/name")
        elif t == "v":
            args.append("PntU" if vcs else "uint32")
        elif t == "vn":
            args.append("ValC")
            args.append("Src/name")
        elif t in ("vcs", "vcp"):
            pass
        elif t == "x":
            args.append("uint32")
        elif t == "xn":
            args.append("XC")
            args.append("Src/name")
        elif t == "l":
            args.append("Src/lab")
        elif t == "d2":
            args.append("Src/descr")
        elif t == "a":
            args.append(f"const('%localDataProjDir%/fe_probe_{name}.dbf', Src)")
        elif t == "at":
            args.append(f"const('%localDataProjDir%/fe_probe_{name}.dbf', Src)")
            args.append("'str'")
        elif t == "s":
            args.append("Src/sql")
        elif t == "c":
            args.append("Src/cdf")
        elif t == "u":
            args.append("Src/url")
        else:
            raise AssertionError(t)
    return args


def normalize(toks):
    """Identiteit; het d/d2-onderscheid wordt al bij het parsen gemaakt."""
    return toks


def main():
    dumps = sys.argv[1:]
    if not dumps:
        sys.exit("geef 1+ t010_operator_groups.txt-dumps op")
    names = set()
    for p in dumps:
        txt = io.open(p, encoding="utf-8", errors="replace").read()
        for g in txt.split(";"):
            g = g.strip()
            if g.startswith("for_each_"):
                names.add(g)
    # for_each_ind (de indirecte vorm met de suffix als stringargument) heeft een
    # eigen test in MetaScript.dms en valt buiten de suffixgrammatica
    names.discard("for_each_ind")
    names = sorted(names)

    parsed = {}
    bad = []
    for nm in names:
        sfx = nm[len("for_each_"):]
        toks = parse_suffix(sfx)
        if toks is None:
            bad.append(nm)
        else:
            parsed[nm] = normalize(toks)
    if bad:
        print(f"WAARSCHUWING: {len(bad)} namen passen niet in de grammatica en worden overgeslagen:")
        for b in bad:
            print("  " + b)

    out = io.StringIO()
    w = out.write
    w("// AUTO-GENERATED by batch/make_for_each_tests.py -- DO NOT EDIT BY HAND.\n")
    w("// Structurele test per geregistreerde for_each_*-variant; zie de docstring\n")
    w("// van de generator en de wiki-pagina For_each voor de suffixgrammatica.\n")
    w("container ForEach\n{\n")
    w("\tunit<uint32> Src: nrofrows = 2\n\t{\n")
    w("\t\tattribute<string> name:  ['x0','x1'];\n")
    w("\t\tattribute<string> expr  := const('uint32(7)', .);\n")
    w("\t\tattribute<string> ic    := const('true', .);\n")
    w("\t\tattribute<string> lab   := const('label', .);\n")
    w("\t\tattribute<string> descr := const('omschrijving', .);\n")
    w("\t\tattribute<string> sql   := const('', .);\n")
    w("\t\tattribute<string> cdf   := const('', .);\n")
    w("\t\tattribute<string> url   := const('', .);\n")
    w("\t}\n")
    w("\tunit<dpoint> PntU;\n")
    w("\tcontainer DomC { unit<uint32> x0: nrofrows = 1; unit<uint32> x1: nrofrows = 1; }\n")
    w("\tcontainer ValC { unit<uint32> x0 := uint32; unit<uint32> x1 := uint32; }\n")
    w("\tcontainer XC   { unit<uint32> x0 := uint32; unit<uint32> x1 := uint32; }\n")
    w("\tTemplate SimpleT { parameter<uint32> tv := uint32(7); }\n")
    w("\tcontainer TC\n\t{\n\t\tTemplate x0 { parameter<uint32> tv := uint32(7); }\n\t\tTemplate x1 { parameter<uint32> tv := uint32(7); }\n\t}\n\n")

    value_checked = 0
    for nm, toks in parsed.items():
        sfx = nm[len("for_each_"):]
        args = args_for(toks, sfx)
        # waardetoets alleen voor varianten zonder domein/template/storage/sql/
        # cdf-tokens: daar is het gegenereerde item een kale parameter met de
        # expressie; bij een a-token zou het opvragen van de waarde de storage
        # aanspreken i.p.v. de expressie
        value_safe = "e" in toks and all(t in ("n", "e", "i", "l", "d2", "u") for t in toks)
        w(f"\tcontainer fe_{sfx}\n\t{{\n")
        w(f"\t\tcontainer res := {nm}(\n\t\t\t {args[0]}\n")
        for a in args[1:]:
            w(f"\t\t\t,{a}\n")
        w("\t\t);\n")
        w("\t\tunit<uint32> chk := SubItem_PropValues(res, 'name');\n")
        if value_safe:
            value_checked += 1
            w("\t\tparameter<bool> test := asList(lowercase(chk/name), ';') = 'x0;x1' && uint32(res/x0) = uint32(7);\n")
        else:
            w("\t\tparameter<bool> test := asList(lowercase(chk/name), ';') = 'x0;x1';\n")
        w("\t}\n")

    w("\n\tcontainer results\n\t{\n")
    w(f"\t\tunit<uint32> Cand : nrofrows = {len(parsed)}\n\t\t{{\n")
    w("\t\t\tattribute<string> Spec :\n\t\t\t[\n")
    rows = [f"'fe_{nm[len('for_each_'):]}/test|{nm}'" for nm in parsed]
    w("\t\t\t\t " + "\n\t\t\t\t,".join(rows) + "\n")
    w("\t\t\t];\n\t\t}\n")
    w("\t\tcontainer selection := TestSet(Cand, Cand/Spec);\n")
    w("\t\tparameter<bool>   tests        := =selection/test_expr;\n")
    w("\t\tparameter<uint32> nrExecuted   := =selection/count_expr;\n")
    w("\t\tparameter<uint32> nrConfigured := =selection/conf_expr;\n")
    w("\t\tparameter<string> failing      := =selection/fail_expr;\n")
    w("\t\tparameter<string> skipped      := =selection/skip_expr;\n")
    w("\t}\n}\n")

    DST.write_bytes(out.getvalue().encode("utf-8"))
    print(f"{DST.name}: {len(parsed)} varianten ({value_checked} met waardetoets), {len(bad)} niet-ontleedbaar")


if __name__ == "__main__":
    main()
