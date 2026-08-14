# GeoDMS-Test — GeoDMS regression suite

Runs the GeoDMS regression tests and generates an HTML report comparing results
across GeoDMS versions. Entry point: `batch/full.py`.

## Running

- **Always run from `batch/`** — `TstDir` is derived from the current directory:
  `python full.py -version 20.1.0.m`
- **`-version` selects an installed GeoDms build** (mapped in `get_geodms_paths`):
  - Windows: `20.1.0.m` / `20.1.0.c` → `%ProgramFiles%/ObjectVision/GeoDms<ver>`
    (`.m` = msbuild, `.c` = cmake; pre-20 builds have no flavor suffix).
  - **Linux (`.l`): `20.1.0.l` → installed `.deb` inside WSL at
    `/opt/ObjectVision/GeoDms<ver>.l`, invoked via `wsl --`.** It is *not* a
    `C:\dev` build — see "Linux / WSL" below.
- **`-tests <substr>`** — run only experiments whose name contains `<substr>`.
  ⚠️ **Substring match**: `-tests t200` also matches `t2000`. Use a precise stem
  (`t200_grid`, `t641_1_RSopen_MakeBaseData`, `t2000_hestia`).
- **`-report-only`** — rebuild the HTML report from existing result folders; run nothing.
- **`-linux-gui`** — also run the Qt GUI tests on `.l` (off by default; they pass now — the `.l` executable bundles its own Qt).

## Critical rules

- **Long runs MUST be detached:**
  `powershell -ExecutionPolicy Bypass -File batch\run_detached.ps1 -Version <ver> [-Tests ...]`
  A run started as a child of an interactive terminal or an agent session gets
  reaped when that session is cleaned up — the whole python + wsl + GeoDmsRun tree
  dies at once, with no error and the GeoDMS log cut off mid-line. It *looks* like a
  crash but isn't. `run_detached.ps1` starts it as an independent Windows process and
  writes the PID next to the results. Check progress via the PID / `.out` / result
  files — watchdogs get reaped too, so don't rely on them.
- **Never mask a failure.** No "hollow OK" (a green that silently skipped its
  indicator or log check). When a reference looks stale, cross-check another version
  before rebaselining — a real engine regression must not be hidden by regenerating
  its reference from the regressing build. (Live example: **t810** is a real 20.1.0
  land-use regression — https://github.com/ObjectVision/GeoDMS/issues/1136 — its
  references were left untouched on purpose.)
- **Report outcomes faithfully** — if a test failed or was skipped, say so plainly.
- **Flaky ≠ versiegedrag.** `Grid/perimeter/test_attr` staat rood op vrijwel elke
  build t/m 20.10: `perimeter()` las niet-geïnitialiseerd geheugen, dus dezelfde
  build geeft per run een andere uitkomst (20.10.0.m 6 van 10 fout, 19.0.0 3 van
  5; 20.12 20 van 20 goed). De groene cellen bij 19.0.0 en 20.7.0.m zijn dus
  muntworpen, en 20.7.0.m groen naast 20.7.0.c rood is geen msbuild/cmake-
  verschil. Gemeld en gefixt: GeoDMS #1169 (gesloten 2026-08-07, fix tussen 20.10
  en 20.12) — geen nieuw issue aanmaken. Herhaal een meting voor je uit zo'n rij
  een versieconclusie trekt; er kwamen ook plausibele waarden als `13,12` en
  `11,11` voorbij.
- **Bekende engine-issues parkeren, niet rood laten staan**: is een gebrek als
  GeoDMS-issue geregistreerd, dan wordt de betreffende toets een expliciete
  skip mét issueverwijzing (Spec-rij uit / skip-notitie in de indicator) —
  longstanding issues mogen de release niet ophouden, maar blijven zichtbaar.
  Zodra het issue gefixt is gaat de toets weer aan. Werkt een geregistreerde
  operator niet, dan is dat een issue voor Maarten (fixen of verwijderen, zie
  https://github.com/ObjectVision/GeoDMS/issues/1177).

## Werkafspraken (Jip)

- **Commits bundelen**: commit per logische mijlpaal, niet per prompt/iteratie;
  vormgevings- en feedbackrondes samenvoegen tot één commit.
- **GitHub-issues zonder attributievoettekst** ("Generated with Claude Code")
  — de Co-Authored-By-regel in gitcommits blijft wel.
- Rapportcellen tonen alleen run-uitslagen (tellingen, `FAILING (n): …`,
  skip-samenvatting) — geen testopzet-metrieken zoals documentatiedekking;
  die staan in `t010_operator_coverage.txt` en op de wiki-werklijst.
- Tests klein genoeg houden om snel te draaien; opschalen is een aparte,
  bewuste stap. Geen databeschikbaarheidschecks: ontbrekende data hoort als
  rode cel op te vallen.

## Meerdere machines tegelijk in deze repo

Er wordt vanaf meerdere PC's (OVSRV05/OVSRV08/OVSRV10) tegelijk aan deze repo
gewerkt, vaak in dezelfde bestanden. Twee regels die dat werkbaar houden:

- **Controleer na elke pull/merge op verlies.** Een merge kan een conflict
  "oplossen" door één kant te houden, waarmee bewuste wijzigingen van de andere
  kant stil verdwijnen. Draai `git diff <binnengekomen-commit> HEAD -- <bestand>`
  en loop de `-`-regels langs: wat daar staat, bedoelde de ander en heb jij niet.
  Zet per regel in de commitboodschap of het verlies opzettelijk is, anders
  herhaalt de volgende sessie de discussie. Op 2026-08-12 verdween zo de
  cgal-un-skip uit `compare.dms` terwijl het gróótste deel van hetzelfde commit
  (`ring_encoding.dms` + de include) wél overleefde — een half toegepast commit
  ziet er bij oppervlakkige controle uit als een toegepast commit.
- **Machinespecifieke paden nooit hardcoderen**, altijd een overridable parameter
  met een env-var in `full.py`; anders blijft elke machine het van de ander
  terugdraaien. Zo verschilt de BAG-snapshot per machine (OVSRV08
  `VolledigeTabel_20240708`, OVSRV05 `_20250710`) — vandaar `%PandSnapshot%`.
- **Regenereer de pre-1810-spiegelboom** na elke wijziging in
  `Operator/cfg/Operator/`: `python batch/make_operator_pre1810.py`, en kijk of
  er een diff uit komt. Bij een merge wordt dat makkelijk vergeten.

## Testjes nooit vooruit op de engine aanzetten

De suite draait tegen **geïnstalleerde releases**, niet tegen de
engine-werkkopie. Een testje aanzetten waarvan de fix nog op een branch staat,
geeft geen rood vinkje maar een stille storing — zet er meteen een
versie-ondergrens `;>=<releaseversie>` op, dan activeert hij zichzelf zodra die
build er is. Twee vormen, beide waargenomen op 2026-08-12:

- **Geregistreerd maar niet geïmplementeerd** (reserved stub, bv. `UrlEncode`,
  GeoDMS #1177): harde parsefout die de héle indicator tegenhoudt, dus alle
  versies houden hun oude uitslag — in het rapport niet te onderscheiden van "er
  is niets veranderd". Een `|operator`-eis helpt hier niet: de naam ís
  geregistreerd. Hiervoor bestaat `;>=NN`.
- **Werkt, maar onbetaalbaar** (de `*_16`-allocatierijen, GeoDMS #1175): geen
  foutmelding, maar t010 liep naar 86 GB op een 64 GB-machine (was 2,6 GB).

Diagnose: vers `log/<test>.txt` naast een oude `result/<test>.txt` betekent dat
de run is gevallen, niet dat er niets veranderde. Onderscheid rood van stil — een
falende toets mag rood staan (zichtbaar), een gekilld proces of parsefout niet
(geen uitslag). Gate alleen het tweede.

## Aanpassen aan nieuwe syntax: houd oudere versies groen

Spiegelbeeld van de regel hierboven. De suite draait tegen **meerdere
geïnstalleerde releases tegelijk**, dus een verwachting die je aanpast aan nieuwe
engine-uitvoer — een andere notatie, een hernoemde eigenschap, een gewijzigde
rendering — maakt daarmee élke oudere versie in het rapport rood, terwijl daar
niets mis is. De cel hoort alleen rood te worden als het resultaat zélf fout is.

Verplaats de verwachting daarom niet, maar maak hem **versie-afhankelijk**: laat
`GeoDmsVersion()` in een meta-scriptconditie de spelling kiezen die bij de
draaiende versie hoort, zoals de `idemFixed`-vlaggen bij de cgal-invarianten in
t020. Voorbeeld uit `Storage/cfg/regression.dms` (`Tiff/GeoReference`), na de
xy(x; y)-notatie van 20.14.0:

```
parameter<bool>   xyTagged := GeoDmsVersion() >= 20.14;
parameter<string> expected := xyTagged
	? 'xy(40.5; -40.5)*m+xy(216000; 384000)'  // 20.14.0+ : getagd, x eerst
	: '{-40.5, 40.5}*m+{384000, 216000}';     // ouder    : ongetagd {row, col}
```

**Controleer beide takken**, niet alleen de build onder handen: draai het testje
ook tegen een geïnstalleerde oudere release
(`%ProgramFiles%\ObjectVision\GeoDms<versie>`). Een oude tak die je niet gedraaid
hebt, is een aanname.

Pas als terugwaartse compatibiliteit echt niet kan — de oude versie kán het
resultaat niet produceren — vervalt de oude tak; zet er dan een versie-ondergrens
op zoals hierboven beschreven, zodat oudere versies **overslaan** in plaats van
rood staan.

## Operator test (t010) — versie-afhankelijke testjes

- **Bestandsindeling**: `Operator/cfg/Operator.dms` is een stam van ~100 regels met
  `#include <Naam.dms>`-regels; de delen (één per thema/top-container) staan in
  `Operator/cfg/Operator/`. GeoDMS resolvet includes vanuit de submap met de naam
  van het verwijzende bestand. De pre-18.1.0-variant is een gegenereerde
  spiegelboom (`operator_pre1810.dms` + `operator_pre1810/`).
- `Operator/cfg/Operator.dms` selecteert testjes per GeoDMS-versie via
  `MetaInfo/OperatorList` (DocData) en het root-`Template TestSet`. Elke
  results-container heeft een `Cand`-tabel; een Spec-rij is `'pad/naar/test_bool'`
  (draait altijd), `'pad|op1[;op2]'` (draait alleen als die operator-groepen in de
  draaiende versie bestaan — noem óók operatoren die het testje intern gebruikt),
  of `'AGG|pad/naar/results'`. Een vereiste `>=NN` is een versie-ondergrens, voor
  namen die in oude versies wél geregistreerd staan maar als "reserved"-stub
  erroren (bv. `geos_buffer_point;>=18`).
- **Dekking is compleet** (2026-08-11): elke testbare operatorgroep heeft een test
  én wiki-documentatie (~4778 testjes, 2276/2276 groepen op 20.8+). De
  `for_each_*`-suffixfamilie (1632 varianten) wordt gegenereerd getest:
  `Operator/cfg/Operator/ForEach.dms` komt uit **`batch/make_for_each_tests.py`**
  (draaien met de `t010_operator_groups.txt`-dumps van de te dekken versies als
  argumenten; daarna pre1810 regenereren). Uitsluitingen-met-reden staan in
  `batch/generic/operator_coverage_exclusions.txt` — issue-geparkeerde rijen gaan
  weer aan zodra het issue gefixt is. **Toeschrijven op basis van co-timing in de
  log is onbetrouwbaar**: de negen `*_16`-allocatievarianten stonden geparkeerd als
  GeoDMS #1175 ("alloceert GB's"), maar de huge allocs bleken van
  `join_equal_values_uint8/16/32/64` te komen (stack-attributie, branch
  `issue_1175`); die rijen staan sinds 2026-08-11 weer aan.
- Rapportcel toont alleen run-uitslagen: uitgevoerd-telling, `FAILING (n)` als
  bulletlijst met operatornaam, en de skips als één samenvattingsregel
  gegroepeerd op reden (volledige lijst: `t010_operator_test_skipped_tests.txt`).
  Dekkings- en documentatiestand: `t010_operator_coverage.txt` per versie
  (doellijst `batch/generic/operator_coverage_targets.txt`, gegenereerd uit de
  wiki met `batch/make_operator_coverage_targets.py`) en de wiki-pagina
  Operator-coverage-worklist.
- **Na elke wijziging aan `Operator.dms`: `python batch/make_operator_pre1810.py`**
  (full.py waarschuwt als de pre-18.1.0-kopie ouder is dan de bron).
- `profiler.py` heeft per-test-timeoutcaps (`TEST_TIMEOUTS`); een te lage cap
  tree-killt de run, wat eruitziet als een stille enginecrash (log midden in een
  regel afgebroken, geen [E]). t010-cap: 600 s.

## Polygonentest (t020)

- **Eén test** (`Polygons/cfg/compare.dms`): geos/bg/bp/cgal vergeleken op
  union-invarianten (som/idempotentie/splitsaantal/areaal-vs-geos), op
  synthetische scenario's (ManySmall/FewLarge) én CBS/BAG-data (gemeenten
  Noord-Holland, BAG-panden binnenstad Amsterdam) — bewust klein gehouden om
  snel te draaien; opschalen is een aparte stap. geos is de referentie.
- Databron per machine via `GEODMS_Overridable_PolyDataDir` (default =
  OVSRV08-locatie). Geen beschikbaarheidscheck: ontbreekt de data, dan is de
  cel rood. Op GeoDMS < 20 draait alleen het synthetische deel
  (`results/all`): pre-20 past `area()` de gridset-projectie niet toe, wat op
  de echte data een bp-artefact van ×1e4/1e6 geeft.
- Cel: ankerregel met de exacte geos-arealen (versievergelijking), daarna één
  bulletregel per familie; bekende issues zijn expliciete skips met issuelink
  (bg-buildings, #1176: de engine-crash is weg, maar de reparatie van de invoer
  lukt nog steeds niet, dus het item wordt bewust niet aangeroepen — de fout zou
  anders de hele run laten falen). De cgal-idempotentieskip is vervallen met de
  fix van #1178 en telt weer mee; op 20.13.0 en ouder is die regel dus terecht
  rood. De issue-882-repro en `ring_encoding` draaien stil mee en melden zich
  alleen bij falen.
- **`Polygons/main/ring_encoding.dms`**: synthetische bewakers op het
  multi-polygoon-RINGFORMAAT (buitenring met de klok mee, binnenringen tegen de
  klok in, deelpolygonen geregen met terugkeerpunten). Daar zaten #1176 en #1178
  in — in de PARSER per familie, niet in de union. Met de hand geschreven
  puntenreeksen, geen SourceData nodig, dus ze draaien ook in `results/all`:
  `island_in_hole` (polygoon in het gat van een andere polygoon, moet 68 m²
  opleveren bij geos/bg/cgal), `overlapping_outers` (ongeldige invoer: geos en bg
  moeten hetzelfde repareren) en `infix` (`+`/`*`/`-` gelijk aan
  geos_union/intersect/difference).
- **bp-schaal**: de gridset-units (rd_mm/rd_cm) dragen hun schaal zelf in
  `area()` — geen extra deling (intAreaDiv = 1.0 voor de echte scenario's;
  gemeenten in cm wegens de 25-bits-coordinaatlimiet van bp).

## Linux / WSL (`.l`)

- The `.l` binary is an **installed Debian package inside the WSL distro** at
  `/opt/ObjectVision/GeoDms<ver>.l`. **Do not build GeoDMS or touch `C:\dev\GeoDMS`** —
  the `LocalBuilds.linux-release` path in `local_settings.json` is only for the
  dev-build pseudo-version `-version local-linux-release`, never the regression `.l` runs.
- The **WSL distro + swap live on `D:\WSL`**; WSL runs as **root**; the ext4 root has
  ~950 GB free. After a Windows reboot, run `wsl --shutdown` then boot once so the
  D: swap re-allocates.
- For `.l`, full.py translates every Windows path to `/mnt/<drive>/...` and forwards
  env vars via `WSLENV`.
- **Heavy writes go to ext4, not `/mnt/c`.** drvfs (`/mnt/c`) sporadically fails large
  sequential writes (`gdal Failure: TIFFAppendToStrip: Write error at scanline N` — a
  drvfs/9p reliability limit, not disk-full). So t641's `%LocalDataProjDir%`
  (BaseData/CalcCache) is relocated to `/root/regression` (ext4) on `.l`;
  `tmpFileDir` / `results_folder.txt` / `%LocalDataDir%` stay on `/mnt/c` (small, and
  written by the Windows-side python which can't reach the distro ext4 fs).
- **Known `.l` blockers:**
  - **GUI tests** (t1630/t1640/t1642): no longer a blocker — they pass on `.l` now (the
    `.l` executable bundles its own Qt, so no system-Qt mismatch). Off by default; pass
    `-linux-gui` to include them (verified green on 20.2.1.l).
  - **RAM-bound tests** auto-skipped on small hosts (`_HEAVY_L_MIN_HOST_GB` in
    full.py): **t2000** (Hestia, ~73 GB working set → needs ≥96 GB) and **t641**
    (RSopen, ~155 GB → needs ≥192 GB). They pass on Windows (`.m`; the OS page file
    absorbs the overflow) but swap-thrash on `.l`. OVSRV05 has 64 GB, so both are
    skipped there.

## Config & data

- **`batch/local_settings.json`** (gitignored, per-machine) holds the SourceData /
  LocalData / Results paths and build locations; copy it from the committed template
  and adjust. Each key can also be overridden by an env var of the same name.
  On OVSRV05: SourceData on `D:/SourceData`, LocalData `C:/LocalData`, results under
  `C:/LocalData/GeoDMS_Test_Results`.
- **References** are read-only under `%SourceDataDir%/TestReferenceFiles/<test>`
  (`%TestRefDir%`). Project configs live in `Projects/`; the large source data lives
  in SourceData and is passed to the configs via `GEODMS_Overridable_*` env vars.
- **Results + report**: one folder per version (`20_1_0_m`, `19_0_0`, `20_1_0_l`, …)
  plus `reports/*.html`, all under the results base.
- The report scripts (`profiler.py`, `regression.py`) are bundled in `batch/generic/`.

## More

- Operational wiki (also linked at the top of `batch/full.py`):
  - https://github.com/ObjectVision/GeoDMS-Test/wiki/Running-tests-with-Claude
  - https://github.com/ObjectVision/GeoDMS-Test/wiki/Running-Linux-tests-on-Windows
  - https://github.com/ObjectVision/GeoDMS-Test/wiki/Test-references-and-report-generation
- New-machine setup: `batch/README.MD`.
