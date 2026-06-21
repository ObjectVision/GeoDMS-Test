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
