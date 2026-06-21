import os
import json
import re
import platform
import importlib
import warnings
import sys
from packaging.version import Version, InvalidVersion

_FLAVOR_SUFFIXES = ("c", "m", "l")

def _try_parse_version(s:str):
    """Return packaging.Version(s), or None if s is not a semantic version
    (e.g. the "local" pseudo-version). None means "newer than anything"
    in the comparisons below. A trailing flavor suffix (".c"/".m"/".l")
    is stripped before parsing — otherwise PEP 440 would interpret ".c"
    as a release-candidate marker (e.g. "20.0.0.c" -> 20.0.0rc0)."""
    if "." in s:
        head, tail = s.rsplit(".", 1)
        if tail in _FLAVOR_SUFFIXES:
            s = head
    try:
        return Version(s)
    except InvalidVersion:
        return None
import glob
from bs4 import BeautifulSoup
import webbrowser
import subprocess
from datetime import datetime

def get_empty_table_row_col_html() -> str:
    # An empty cell means the experiment was not run for that version -> show it
    # explicitly instead of a blank (e.g. GUI tests skipped on the linux flavor).
    return '<td class="cell skip"><span class="pill skip">not run</span></td>\n'

def get_status_meta(status:str) -> tuple:
    """Map a raw status (OK / TIMEOUT / FCFAIL / a numeric GeoDmsRun exit code /
    an indicator <result> text) to (human label, css class, code note) for the
    report. css class is one of: ok, fail, warn, timeout."""
    code_labels = {"1": "data error", "2": "config / parse error", "6": "config error",
                   "15": "timeout", "99": "output differs", "134": "crashed (no log)"}
    if status == "OK":
        return ("ok", "ok", "")
    if status == "TIMEOUT":
        return ("timeout", "timeout", "exit 15")
    if status == "FCFAIL":
        return ("output differs", "fail", "exit 99")  # output differs from reference = a real failure (red)
    if status == "no result":
        return ("not validated", "warn", "indicator missing")
    if status == "reference pending":
        return ("reference pending", "warn", "no reference yet")
    if status == "error":
        return ("error", "fail", "")
    if status in ("False", "false"):
        return ("failed", "fail", "")
    if status.lstrip("-").isdigit():
        if int(status) < 0:
            return ("not run", "skip", "")
        return (code_labels.get(status, f"error (code {status})"), "fail", f"exit {status}")
    return (status, "ok", "")  # arbitrary <result> text

def fmt_gb(x:float) -> str:
    """Uniform GB formatting: always 2 decimals so a column lines up
    (mem 51.00 / rd 0.00 / wr 0.00)."""
    return f"{x:.2f}"

def cap_testname(name:str) -> str:
    """Uniformly capitalize the first letter of a test name's descriptive part,
    leaving the tNNN[_n] code lowercase and preserving deviant casing elsewhere
    (e.g. hWP, Poly2Grid, RSopen). Only the first descriptive word is touched,
    and only if it currently starts lowercase."""
    words = name.split(" ")
    for i, w in enumerate(words):
        if i == 0 and re.match(r"^t\d", w):   # leading test code (t010, t641)
            continue
        if w.isdigit():                        # sub-number (t641 _3_ ...)
            continue
        if w and w[0].islower():
            words[i] = w[0].upper() + w[1:]
        break
    return " ".join(words)

def get_days_hours_minutes_seconds_from_duration(duration:int):
    # split duration [s] into components
    time = duration
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    return day, hour, minutes, seconds

def format_duration(duration:int) -> str:
    """Format a duration [s] as a zero-padded H:MM:SS string, prefixed with
    a day count only when it is non-zero (e.g. "3:23:09" or "1d 2:30:19")."""
    day, hour, minutes, seconds = get_days_hours_minutes_seconds_from_duration(duration)
    time_part = f"{int(hour)}:{int(minutes):02d}:{int(seconds):02d}"
    return f"{int(day)}d {time_part}" if day else time_part

def _add_thousand_separators(text:str) -> str:
    """Insert thousand separators into standalone integers of 4+ digits, leaving
    decimals (dot- or comma-separated) and already-grouped numbers untouched."""
    return re.sub(r"(?<![\d.,])(\d{4,})(?![\d.,])", lambda m: f"{int(m.group(1)):,}", text)

def get_indicator_part_from_parsed_results(parsed_results:dict)->list:
    # Render each indicator's VALUE (the label lives in the value, set by the test's
    # result_html) -- not "tagname: value", so no underscored tag names leak into the
    # overview. 'result' is the verdict pill; 'description' is shown under the test name.
    indicator_part = ""
    # The "changed" badge marks a REFERENCE-EPOCH switch at this version (a refset was
    # deliberately re-baselined here), NOT per-version drift -- drift that matters already
    # shows as a red (failing) line via the status. So it is driven by _epoch_changed.
    set_indicator_flag = bool(parsed_results.get("_epoch_changed", [False])[0])
    for indicator in parsed_results:
        if indicator in ("result", "description", "issue", "_epoch_changed", "_is_ref", "_ref_src"):  # verdict pill / under title / metadata / cell flags
            continue
        value = parsed_results[indicator][0]
        status = parsed_results[indicator][1]
        cls = "ind-line changed" if not status else "ind-line"   # red for a failing metric (vs its reference)
        indicator_part += f"<div class='{cls}'>{_add_thousand_separators(value)}</div>"
    if indicator_part:
        indicator_part = f"<div class='ind'>{indicator_part}</div>"
    return [indicator_part, set_indicator_flag]

def _perf_class(value, baseline, warn_ratio, bad_ratio, floor):
    # Colour a duration/memory cell by how far it sits ABOVE the row's fastest/lightest run.
    # Robust to machine noise: needs BOTH a large relative ratio AND an absolute jump >= floor,
    # so seconds / 0.x-GB wobble on fast/light tests stays neutral (3:50-vs-4:00, 5s-vs-9s),
    # while 1:30-vs-2:00 turns amber/red. floor is in the value's own unit (sec / GB).
    if not baseline or not value or (value - baseline) < floor:
        return ""
    r = value / baseline
    return "perf-bad" if r >= bad_ratio else ("perf-warn" if r >= warn_ratio else "")

def get_table_regression_test_row(result_paths:dict, summary_row:list) -> str:
    regression_test_row = get_table_row_title_html_template()
    testname = summary_row[0]
    testclass = testname.replace(" ", "_")
    regression_test_row = regression_test_row.replace("@@@TESTNAME@@@", testname)
    regression_test_row = regression_test_row.replace("@@@TESTCLASS@@@", testclass)
    regression_test_row = regression_test_row.replace("@@@TESTDESC@@@", get_test_description(testname))
    # perf-colouring baselines: the fastest / lightest run across this test's versions
    _pcells = [c for c in summary_row[1:] if c]
    _min_dur = min([c["duration"] for c in _pcells if c.get("duration")], default=0)
    _min_mem = min([c["highest_commit"] for c in _pcells if c.get("highest_commit")], default=0)
    for summary_col_row in summary_row[1:]:
        if not summary_col_row:
            regression_test_row += get_empty_table_row_col_html()
            continue
        table_col_header = get_table_row_col_html_template(result_paths, summary_col_row["log_filename"], summary_col_row["profile_figure_filename"])
        status = summary_col_row["status"]
        status_label, status_class, status_code = get_status_meta(status)
        table_col_header = table_col_header.replace("@@@TESTCLASS@@@", testclass)
        table_col_header = table_col_header.replace("@@@STATUSLABEL@@@", status_label)
        table_col_header = table_col_header.replace("@@@STATUSCLASS@@@", status_class)
        table_col_header = table_col_header.replace("@@@STATUSCODE@@@", status_code)
        _dcls = _perf_class(summary_col_row["duration"], _min_dur, 1.25, 1.5, 30)   # >=30s AND >=25%/50% slower
        _dval = format_duration(summary_col_row["duration"])
        table_col_header = table_col_header.replace("@@@DURATION@@@", f'<span class="{_dcls}" title="vs fastest run in this row">{_dval}</span>' if _dcls else _dval)

        #2025 05 21 : 12.24.32
        command = summary_col_row["command"]#.replace("GeoDmsRun.exe", "GeoDmsGuiQt.exe")
        # Merge the leading "dir"/GeoDmsRun.exe into one quoted token so the
        # executable path — which lives under "Program Files" (a space) — stays
        # paste-ready (issue #21). Linux 'wsl -- /opt/...' commands have no
        # leading quote and are left untouched.
        command = re.sub(r'^"([^"]*)"(\S+)', r'"\1\2"', command)
        # HTML-escape for the href attribute; copy_href reads getAttribute("href"),
        # which decodes entities, so the clipboard receives the real quotes.
        command = command.replace("&", "&amp;").replace('"', "&quot;")
        table_col_header = table_col_header.replace("@@@GEODMS_CMD@@@", command)
        start_time_value = summary_col_row["start_time"]
        table_col_header = table_col_header.replace("@@@STARTTIME@@@", start_time_value.strftime("%Y-%m-%d %H:%M") if start_time_value else "n/a")
        _mcls = _perf_class(summary_col_row["highest_commit"], _min_mem, 1.10, 1.25, 0.5)  # >=0.5GB AND >=10%/25% heavier
        _mval = fmt_gb(summary_col_row["highest_commit"])
        table_col_header = table_col_header.replace("@@@HIGHESTCOMMIT@@@", f'<span class="{_mcls}" title="vs lightest run in this row">{_mval}</span>' if _mcls else _mval)
        # perf badge next to the status pill: a green/OK cell can still hide a 2x-memory or much-slower run
        _pbadge = ""
        if _mcls:
            _pbadge += f'<span class="perfbadge {_mcls}" title="peak memory vs the lightest run in this row">mem +{round((summary_col_row["highest_commit"]/_min_mem - 1) * 100)}%</span>'
        if _dcls:
            _pbadge += f'<span class="perfbadge {_dcls}" title="duration vs the fastest run in this row">dur +{round((summary_col_row["duration"]/_min_dur - 1) * 100)}%</span>'
        table_col_header = table_col_header.replace("@@@PERF_BADGE@@@", _pbadge)
        table_col_header = table_col_header.replace("@@@MAXTHREADS@@@", str(summary_col_row["max_threads"]))
        table_col_header = table_col_header.replace("@@@TOTALREAD@@@", fmt_gb(summary_col_row["total_read"]))
        table_col_header = table_col_header.replace("@@@TOTALWRITE@@@", fmt_gb(summary_col_row["total_write"]))
        table_col_header = table_col_header.replace("@@@LOG@@@", summary_col_row["log_filename"])
        table_col_header = table_col_header.replace("@@@PROFILE_FIGURE@@@", summary_col_row["profile_figure_filename"])

        # indicators        
        indicator_part, indicator_flag = get_indicator_part_from_parsed_results(summary_col_row["results"][1])
        is_ref_cell = summary_col_row["results"][1].get("_is_ref", [False])[0]
        # triangle = the comparison baseline (refset) changes here; suppress it on the ref-source cell,
        # where the "ref" pill already conveys it (avoids the double marker -- e.g. t910 at the new ref).
        _refsrc = summary_col_row["results"][1].get("_ref_src", [""])[0]
        _flag_title = "comparison baseline (refset) changed starting at this version" + (f" -- reference captured from {_refsrc}" if _refsrc else "")
        table_col_header = table_col_header.replace("@@@INDICATOR_FLAG@@@", f'<span class="flag" title="{_flag_title}">&#9650;</span>' if (indicator_flag and not is_ref_cell) else "")
        table_col_header = table_col_header.replace("@@@REF_PILL@@@", '<span class="refpill" title="this version IS the reference (baseline) for this test">ref</span>' if is_ref_cell else "")
        table_col_header = table_col_header.replace("@@@INDICATORS@@@", indicator_part)

        regression_test_row += table_col_header

    return f'<tr>{regression_test_row}</tr>\n'

TEST_DESCRIPTIONS = {
    "t010": "Operator/function test — exercises many DMS operators on the Operator config.",
    "t050": "Storage: write an ESRI shapefile (polygon) via the storage manager; round-trip.",
    "t060": "Storage: build a BAG snapshot (Utrecht) as GeoPackage; compare to reference.",
    "t100": "Network: connect PC6 points to the road network (NL/BE/DE); compare to reference.",
    "t101": "Network: OD PC4 dense impedance matrix over the road network (NL/BE/DE).",
    "t102": "Network: OD PC6 sparse impedance matrix (with cut) over the road network.",
    "t151": "Coordinate conversion Belgian Lambert → RD for Belgian municipalities.",
    "t200": "Grid: poly2grid of CBS land use (BBG) to a 10 m grid (NL).",
    "t300": "Read BAG XML files and parse polygon geometries.",
    "t301": "Derive residential type from BAG pand/vbo geometry; compare to reference (1‰).",
    "t405_1": "NetworkModel PBL, step 1: prepare input data.",
    "t405_2": "NetworkModel PBL, step 2.1: tiled model run without fence.",
    "t405_2_2": "NetworkModel PBL: indicator comparison of the no-fence run.",
    "t405_3": "NetworkModel PBL, step 2.2: tiled model run with fence.",
    "t405_3_2": "NetworkModel PBL: indicator comparison of the fenced run.",
    "t410": "NetworkModel EU: indicator-results regression test.",
    "t611": "LUS Demo 2023 (Land Use Scanner): compare allocation results.",
    "t641_1": "RuimteScanner Open v2025H2: generate base data (write BaseData).",
    "t641_1_2": "RSopen: indicator comparison of the base-data step.",
    "t641_3": "RSopen: land-use allocation for target year 2050.",
    "t710": "2UP global urbanisation model: indicator results.",
    "t720": "2BURP model: indicator-results regression test.",
    "t810": "ValLuisa / 100m DynaPop (EuClueScanner): land use & population, Czechia 2050.",
    "t910": "Cusa2 Africa model: indicator-results regression test.",
    "t1630": "GUI robustness: fully expand RSLight_2020 SourceData/Claims/ReadData.",
    "t1640": "GUI: value-info detail page on aggregations vs recorded reference.",
    "t1642": "GUI: statistics/value-info detail page with group-by on geometry.",
    "t1742": "Command-line @statistics on the Operator config (Arithmetics/UnTiled/add/attr).",
    "t2000": "Hestia development: @statistics on /Jaarreeksen/hWP_asl.",
}

def get_test_description(testname:str) -> str:
    """Short English description for a test, keyed by its leading code (t010,
    t405_3_2, ...). Returns '' when no description is defined."""
    m = re.match(r"(t\d+(?:[ _]\d+)*)", testname, re.IGNORECASE)
    if not m:
        return ""
    code = m.group(1).lower().replace(" ", "_")
    return TEST_DESCRIPTIONS.get(code, "")

def get_table_row_title_html_template() -> str:
    return '<td class="testname">\
                <button onclick="expand_test_row(\'@@@TESTCLASS@@@\')" title="click to expand/collapse all versions of this test">@@@TESTNAME@@@</button>\
                <div class="testdesc">@@@TESTDESC@@@</div>\
            </td>\n'

def get_table_row_col_html_template(result_paths:dict, log_fn:str=None, profile_fig_fn:str=None) -> str:
    absolute_log_fn = f"{result_paths["results_base_folder"]}/{log_fn[3:]}"
    absolute_profile_fn = f"{result_paths["results_base_folder"]}/{profile_fig_fn[3:]}"

    log_part = "" if not os.path.isfile(absolute_log_fn) else '<a href="@@@LOG@@@" target="_blank" title="log">log</a>'
    profile_part = "" if not os.path.isfile(absolute_profile_fn) else '<a href="@@@PROFILE_FIGURE@@@" target="_blank" title="profile">profile</a>'
    geodms_part = '<a href="@@@GEODMS_CMD@@@" onclick="copy_href(event, this)" title="copy GeoDmsRun command">command</a>'
    return f'<td class="cell @@@STATUSCLASS@@@">\
    <details class=@@@TESTCLASS@@@>\
    <summary><span class="pill @@@STATUSCLASS@@@">@@@STATUSLABEL@@@</span><span class="code">@@@STATUSCODE@@@</span>@@@PERF_BADGE@@@@@@INDICATOR_FLAG@@@@@@REF_PILL@@@</summary>\
    <div class="meta">@@@STARTTIME@@@ &middot; @@@DURATION@@@</div>\
    <div class="metrics">mem @@@HIGHESTCOMMIT@@@ GB &middot; rd @@@TOTALREAD@@@ GB &middot; wr @@@TOTALWRITE@@@ GB &middot; @@@MAXTHREADS@@@ thr</div>\
    @@@INDICATORS@@@\
    <div class="links">{log_part} {geodms_part} {profile_part}</div>\
    </details>\
    </td>\n'

def collect_experiment_summaries(version_range:tuple, result_paths:dict, sorted_valid_result_folders:list, regression_test_names:list, regression_test_files:dict) -> list[list]:
    # initialize table
    rows = len(regression_test_names)+1
    cols = len(sorted_valid_result_folders)+1
    summaries = [[None for _ in range(cols)] for _ in range(rows)]
    # Per column, which column counts as its "previous version" for the
    # indicator-changed (gewijzigd) flag -- same flavor preferred, else mainline.
    prev_col_map = build_prev_col_map(sorted_valid_result_folders)

    if "title" in result_paths and "logo" in result_paths:
        summaries[0][0] = f"<img src='{result_paths["logo"]}' alt='TNO logo' width='150' height='75'><br>\
                            {result_paths["title"]}<br>"
    else:
        summaries[0][0] = "GeoDMS regression test results"

    # fill table with summaries
    for regression_test in regression_test_files.keys():
        row = get_result_row(regression_test, regression_test_names)
        summaries[row][0] = cap_testname(regression_test.replace("_", " "))
        binary_experiment_result_files = regression_test_files[regression_test]
        regression_test_experiments = []
        for experiment_file in reversed(binary_experiment_result_files):
            col = get_result_col(experiment_file, sorted_valid_result_folders)
            if not summaries[0][col]:
                summaries[0][col] = get_col_header(col, sorted_valid_result_folders)
            experiment = profiler.loadExperimentFromPickleFile(None, experiment_file)
            summaries[row][col] = experiment.summary()
            regression_test_experiments.append(experiment)
            log_filename = get_log_filename(sorted_valid_result_folders[col-1][0], regression_test)
            profile_fig_filename = get_profile_figure_filename(sorted_valid_result_folders[col-1][0], regression_test)
            summaries[row][col]["profile_figure_filename"] = f"../{profile_fig_filename}"
            summaries[row][col]["log_filename"] = f"../{log_filename}"
            status_code = experiment.result["status_code"] if "status_code" in experiment.result else 0
            prev_indicators = {}
            prev_version = None
            prev_col = prev_col_map.get(col)
            # prev_col is always an older version => higher column index, which
            # is processed earlier (experiments run old->new here), so it is
            # already filled in `summaries` by the time we reach this column.
            if prev_col and summaries[row][prev_col]:
                prev_indicators = summaries[row][prev_col]["results"][1]
            # Epoch (refset-change) flag: compare to the nearest OLDER column that actually
            # has data for THIS test -- not the flavour-prev, which may be an empty cell for a
            # version that didn't run this test (e.g. 20.0.1 wasn't in the chain).
            for _c in range(col + 1, len(sorted_valid_result_folders) + 1):
                if summaries[row][_c]:
                    prev_version = _try_parse_version(get_semantic_version_from_folder_name(sorted_valid_result_folders[_c - 1][0]))
                    break

            results = get_regression_test_result(status_code, regression_test, f"{result_paths["results_base_folder"]}/{sorted_valid_result_folders[col-1][0]}", experiment.file_comparison, experiment.result.get('indicators'), prev_indicators, getattr(experiment, "indicator_results_file", None), prev_version)
            summaries[row][col]["status"] = results[0]
            summaries[row][col]["results"] = results
        
        target_visualized_experiments_filename = get_profile_figure_filename(result_paths["results_folder"], regression_test)
        if not os.path.exists(target_visualized_experiments_filename):
            visualized_experiments_filename = profiler.VisualizeExperiments(regression_test_experiments, show_figure=False)
            #os.remove(target_visualized_experiments_filename)
            os.rename(visualized_experiments_filename, target_visualized_experiments_filename)

    # get column total duration and success ratio
    for col in range(1, cols):
        total_tests = rows - 1
        total_duration = 0
        succeeded = 0
        for row in range(1, rows):
            if not summaries[row][col]:
                total_tests -= 1
                continue
            summary_row_col = summaries[row][col]
            total_duration += summary_row_col["duration"]
            if summaries[row][col]["status"] == "OK":
                succeeded += 1
        if summaries[0][col] is None:
            summaries[0][col] = get_col_header(col, sorted_valid_result_folders)
        summaries[0][col]["total_duration"] = total_duration
        summaries[0][col]["success_ratio"] = (succeeded, total_tests)
    return summaries

def parse_indicators(indicators:str) -> dict:
    # <description>operator test</description><size>number unique tests: 1356</size><result>OK</result>
    raw_html = indicators
    result_dict = {}
    soup = BeautifulSoup(raw_html, "html.parser")
    for child in soup.children:
        if child.name is None:  # stray text node between tags -> skip
            continue
        # decode_contents() keeps inner <br>/<b> markup so multi-value indicator
        # blocks (t405/t641/t710/t720/t910) render with their line breaks instead
        # of being collapsed onto one line by .text.
        result_dict[child.name] = [child.decode_contents(), True]
    return result_dict

# --- Reference values + tolerance policy (applied by the REPORT; GeoDMS only MEASURES) ---
# Indicator reference VALUES live in a version-controlled file, references.json, captured
# deliberately from the trusted GeoDMS build (17.4.6) -- a test run NEVER writes it, so a
# regression cannot silently rebaseline itself. The report judges each version's measured
# value against this reference; tolerance is 0% (exact) everywhere unless overridden in
# TOLERANCES. Cell/diff tests (n_diff) are judged against 0 (their reference is the recorded
# .fss/.tif in TestReferenceFiles). Re-capture deliberately via batch/capture_references.py
# after a trusted-build run -- never automatically.
def _load_reference_doc() -> dict:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "references.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}

_REFERENCE_DOC   = _load_reference_doc()
REFERENCE_BUILD  = _REFERENCE_DOC.get("_captured_from", "reference")
REFERENCE_VALUES = {k: v for k, v in _REFERENCE_DOC.items() if not k.startswith("_")}

# Optional per test+metric tolerance override (percent); default 0.0 = exact match.
TOLERANCES = {}

def _tol(test:str, name:str) -> float:
    return TOLERANCES.get(test, {}).get(name, 0.0)

def _fmt_num(x):
    """Human-friendly number for the report: thousands separators, no trailing noise."""
    if isinstance(x, bool) or x is None or isinstance(x, str):
        return str(x)
    try:
        return f"{x:,}"
    except (ValueError, TypeError):
        return str(x)

def _fmt_pct(dev:float) -> str:
    """Signed deviation %. A nonzero diff below 0.001% is shown as '<0.001%' rather than
    rounding to a misleading '0.000%' -- so 1-ulp float noise stays visibly nonzero."""
    if abs(dev) >= 0.001:
        return f"{dev:+.3f}%"
    return ("+" if dev >= 0 else "-") + "<0.001%"

def _resolve_ref(entry, version):
    """A reference value is either a scalar (one baseline for every version) or a
    {threshold_version: value} map = version-dependent epochs (connect changed at
    19.5.0 -> a new accepted baseline; t810 land-use has several epochs). Returns
    (value, epoch_label) for the highest threshold <= the version under test, or
    (None, None) if no epoch applies yet."""
    if not isinstance(entry, dict):
        return entry, REFERENCE_BUILD, REFERENCE_BUILD
    best = None  # (threshold_version, value_entry, threshold_str)
    for thr, val in entry.items():
        tv = _try_parse_version(thr)
        if tv is None:
            continue
        if version is None or version >= tv:
            if best is None or tv > best[0]:
                best = (tv, val, thr)
    if best is None:
        return None, None, None
    val = best[1]
    if isinstance(val, dict):   # {"v": <value>, "src": "<version>"} = the value + the build it came from
        return val.get("v"), f">={best[2]}", val.get("src")
    return val, f">={best[2]}", None   # bare value (no recorded source)

def _version_from_result_path(path):
    """Version under test, from a result.json path .../<folder>[/result]/<file>."""
    d = os.path.dirname(path)
    folder = os.path.basename(os.path.dirname(d)) if os.path.basename(d) == "result" else os.path.basename(d)
    try:
        return _try_parse_version(get_semantic_version_from_folder_name(folder))
    except Exception:
        return None

def parse_result_json(path:str, prev_indicators:dict={}, prev_version=None) -> tuple:
    """Read a <test>.result.json MEASUREMENT (raw counts / values; GeoDMS does not judge)
    and return the (verdict_text, indicator_dict) the report expects. The verdict is computed
    HERE, so it is tunable with -report-only: a cell metric (n_diff) is judged against 0 within
    tolerance; a value metric is compared to the trusted reference value (references.json,
    captured from REFERENCE_BUILD) within tolerance. A value metric with no reference yet ->
    'reference pending'. indicator_dict maps a display line key -> [html, ok]; ok=False
    highlights the line (a failing metric, or drift vs the previous version)."""
    with open(path, "r", encoding="utf-8") as f:
        doc = json.load(f)
    test = doc.get("test", "")
    refs = REFERENCE_VALUES.get(test, {})
    metrics = doc.get("metrics", [])

    lines = {}
    any_fail = any_pending = False
    totals = {m.get("n_total") for m in metrics if "n_diff" in m and m.get("n_total") is not None}
    single_total = len(totals) == 1
    if single_total:
        lines["cells in test"] = [f"cells in test: {_fmt_num(next(iter(totals)))}", True]

    version = _version_from_result_path(path)
    epoch_changed = False  # did any metric's reference EPOCH begin at THIS version (a new refset baseline)?
    is_ref = False         # is THIS version the source/baseline for any metric? (-> "ref" pill, top-right of the cell)
    epoch_srcs = set()     # which version(s) the NEW refset was captured from when the epoch changes here (-> triangle hover)

    for m in metrics:
        name = str(m.get("name", "metric"))
        unit = m.get("unit", "")
        unit_s = f" {unit}" if unit else ""
        tol = _tol(test, name)
        ref, epoch, src = _resolve_ref(refs.get(name), version)
        if src is not None and version is not None and version == _try_parse_version(src):
            is_ref = True   # this version's own value IS the reference for this metric/epoch
        if prev_version is not None and ref is not None and epoch != _resolve_ref(refs.get(name), prev_version)[1]:
            epoch_changed = True   # this metric's reference baseline switched at this version
            if src:
                epoch_srcs.add(src)   # the version this new refset was captured from (for the triangle hover)
        if "n_diff" in m:
            n_total = m.get("n_total") or 0
            n_diff = m.get("n_diff") or 0
            extra = "" if (single_total or m.get("n_total") is None) else f" of {_fmt_num(m.get('n_total'))}"
            if ref is not None:
                # Accepted-diff baseline (version-dependent), e.g. t810 land-use: the model
                # never matches LUISA exactly, so judge the diff-count against the accepted
                # level for this version's epoch instead of against 0.
                ok = n_diff == ref
                any_fail = any_fail or not ok
                suffix = f"(= {epoch} baseline)" if ok else f"(baseline {epoch} {_fmt_num(ref)})"
                lines[name] = [f"{name}: {_fmt_num(n_diff)} differ{extra} {suffix}", ok]
            else:
                pct = (100.0 * n_diff / n_total) if n_total else 0.0
                ok = pct <= tol
                any_fail = any_fail or not ok
                if n_diff:
                    lines[name] = [f"{name}: {_fmt_num(n_diff)} differ{extra} ({pct:.3f}%)", ok]
                else:
                    lines[name] = [f"{name}: no differences{extra}", ok]
        else:  # a measured VALUE -> compare to the trusted reference value
            value = m.get("value")
            if ref is None:
                any_pending = True
                lines[name] = [f"{name}: {_fmt_num(value)}{unit_s} (no reference yet)", True]
            else:
                dev = (100.0 * (value - ref) / abs(ref)) if ref else (0.0 if value == ref else 100.0)
                ok = abs(dev) <= tol
                any_fail = any_fail or not ok
                if value == ref:
                    lines[name] = [f"{name}: {_fmt_num(value)}{unit_s}", ok]
                else:
                    lines[name] = [f"{name}: {_fmt_num(value)}{unit_s} (ref {_fmt_num(ref)}, {_fmt_pct(dev)})", ok]

    verdict = "False" if any_fail else ("reference pending" if any_pending else "OK")
    parsed = {"result": [verdict, True]}
    parsed.update(lines)

    verdir = os.path.basename(os.path.dirname(path))
    for a in doc.get("artifacts", []):
        kind, metric = a.get("kind", "artifact"), a.get("metric", "")
        label = f"{kind} ({metric})" if metric else kind
        parsed[f"artifact:{kind}:{metric}"] = [f"<a href='../{verdir}/{a.get('path')}'>{label}</a>", True]

    # "Gewijzigd"-vlag = de referentie-baseline (epoch) is bij DEZE versie gewisseld,
    # NIET per-versie drift (drift die ertoe doet staat al rood via de status). Zo
    # markeert het icoon waar een refset bewust is herijkt; latere versies in dezelfde
    # epoch krijgen 'm niet meer.
    parsed["_epoch_changed"] = [epoch_changed, True]
    parsed["_is_ref"] = [is_ref, True]
    parsed["_ref_src"] = [", ".join(sorted(epoch_srcs)), True]
    return (verdict, parsed)

def get_regression_test_result(status_code:int, regression_test:str, regression_test_folder:str, file_comparison:tuple, indicators:str=None, prev_indicators:dict={}, indicator_results_file:str=None, prev_version=None) -> tuple:

    # Did the experiment DECLARE a result indicator? If so its <result> is the
    # test's verdict and a missing file must NOT silently become a hollow "OK".
    declared_indicator = bool(indicator_results_file)
    rdir = _result_dir(regression_test_folder)  # <version>/result, or the flat folder if un-migrated
    if not indicators and indicator_results_file:
        # The cfg writes the file the experiment declared; read exactly that one
        # (its basename can be longer than the experiment name, e.g.
        # t810_ValLuisa -> t810_ValLuisa_Czech_LU_POP.txt).
        declared = f"{rdir}/{os.path.basename(indicator_results_file)}"
        if os.path.isfile(declared):
            with open(declared, "r") as f:
                indicators = f.read()

    if not indicators: # attempt get default indicators from experiment if not specified
        indicators_default_fn_txt = f"{rdir}/{regression_test}.txt"
        indicators_default_fn_xml = f"{rdir}/{regression_test}.xml"
        if os.path.isfile(indicators_default_fn_txt):
            with open(indicators_default_fn_txt, "r") as f:
                indicators = f.read()
        elif os.path.isfile(indicators_default_fn_xml):
            with open(indicators_default_fn_xml, "r") as f:
                indicators = f.read()
        else:
            # Prefer the real result .txt. The *.xml here are GeoDMS MetaInfo
            # sidecars (incl. *.result.xml written next to a migrated .result.json),
            # which have no <result> tag -- only fall back to .xml when there is no
            # .txt, and never to a *.result.xml sidecar.
            cands = sorted(glob.glob(f"{rdir}/{regression_test}*.txt"))
            if not cands:
                cands = sorted(c for c in glob.glob(f"{rdir}/{regression_test}*.xml")
                               if not c.endswith(".result.xml"))
            for cand in cands:
                with open(cand, "r") as f:
                    indicators = f.read()
                break

    if status_code == 99:
        return ("FCFAIL", {})

    if status_code == 15:
        return ("TIMEOUT", {})

    if status_code != 0:
        return (str(status_code), {})

    # Prefer the structured <test>.result.json (new standard) over the legacy tag
    # .txt; fall through to the legacy path on a parse error.
    json_cands = sorted(glob.glob(f"{rdir}/{regression_test}*.result.json"))
    if json_cands:
        try:
            return parse_result_json(json_cands[0], prev_indicators, prev_version)
        except Exception as e:
            warnings.warn(f"{regression_test}: unreadable result.json ({e}); using legacy result")

    if not indicators:
        # exit 0 but the declared result indicator is missing -> the test ran but
        # was never validated. Surface it (red) instead of a hollow "OK".
        return ("no result", {}) if declared_indicator else ("OK", {})
    
    # compare previous with current indicators for flagging differences
    parsed_indicators = parse_indicators(indicators)
    for indicator in parsed_indicators:
        if not indicator in prev_indicators:
            continue
        if parsed_indicators[indicator][0] != prev_indicators[indicator][0]:
            parsed_indicators[indicator][1] = False

    if parsed_indicators.get("result"):    
        result_text = parsed_indicators["result"][0]
        if len(result_text)>15:
            
            #if "OK" in result_text:
            print(f"Compressing geodms result_text from '{result_text}' to 'OK'")
            result_text = "OK"
    else:
        warnings.warn(f"Experiment {regression_test} has no 'result' indicator")
        result_text = "no result"  # surface honestly (red), never crash / hollow OK

    return (result_text, parsed_indicators)

# --- Per-version-folder layout: log/ bin/ result/ html/. Reads fall back to the flat
# layout, so historical / not-yet-migrated folders keep working. ---
def _result_dir(folder:str) -> str:
    """GeoDMS result files (.result.json/.xml, legacy .txt) live in <folder>/result;
    fall back to the flat <folder> for folders not migrated to the new layout."""
    sub = f"{folder}/result"
    return sub if os.path.isdir(sub) else folder

def _bin_glob(folder:str) -> list:
    """*.bin under <folder>/bin, falling back to the flat <folder>."""
    sub = glob.glob(f"{folder}/bin/*.bin")
    return sub if sub else glob.glob(f"{folder}/*.bin")

def get_log_filename(result_folder:str, regression_test:str):
    return f"{result_folder}/log/{regression_test}.txt"

def get_profile_figure_filename(result_folder:str, regression_test:str):
    d = f"{result_folder}/html"
    os.makedirs(d, exist_ok=True)
    return f"{d}/{regression_test}.html"

def get_col_header(col:int, sorted_valid_result_folders:list) -> dict:
    result_folder_name, _,_ = sorted_valid_result_folders[col-1]
    major, minor, patch, flavor, architecture, sf, multithreading, local_machine_name, time, hash = parse_folder_name(result_folder_name)
    display_version = f"{major}.{minor}.{patch}" + (f".{flavor}" if flavor else "")
    return {"version":display_version, "build":"Release", "platform":architecture, "multi_tasking":multithreading, "computer_name":local_machine_name, "time":time, "hash":hash}

def get_result_col(experiment_file:str, sorted_valid_result_folders:list):
    col = 1
    experiment_filename = os.path.basename(experiment_file)
    foldername_from_experiment_file = experiment_filename.split("__")[0]
    for foldername, _,_ in sorted_valid_result_folders:
        if foldername == foldername_from_experiment_file:
            return col
        col+=1

    raise(Exception(f"col out of range regression: {col}"))

def get_result_row(regression_test:str, regression_test_names:list):
    row = 1
    for testname in regression_test_names:
        if testname == regression_test:
            return row
        row+=1
    return row

def collect_experiment_filenames_per_experiment(regression_tests:list, result_paths:dict, sorted_valid_result_folders:list) -> dict:
    regression_tests_experiment_filenames = {}
    for regression_test in regression_tests:
        regression_tests_experiment_filenames[regression_test] = []
        for experiment_folder, _, _ in sorted_valid_result_folders:
            experiment_folder_path = f"{result_paths["results_base_folder"]}/{experiment_folder}"
            experiment_filenames = get_all_experiments_from_experiment_folder(experiment_folder_path)
            for experiment_filename in experiment_filenames:
                experiment_name = get_experiment_name_from_experiment_filename(experiment_filename)
                if not experiment_name == regression_test:
                    continue
                regression_tests_experiment_filenames[regression_test].append(experiment_filename)
    return regression_tests_experiment_filenames

def test_sort_key(name:str):
    """Order test names by their numeric tNNN code (and sub-numbers), so e.g.
    t200 sorts before t1742 -- not alphabetically, where 't1742' < 't200'
    because '1' < '2'. t405_2 sorts before t405_3 via the sub-numbers."""
    m = re.match(r"t(\d+)((?:_\d+)*)", name)
    if not m:
        return (10**9, [], name)
    return (int(m.group(1)), [int(x) for x in m.group(2).split("_") if x], name)

def get_all_regression_tests_by_name(result_paths:dict, valid_result_folders:list):
    regression_tests = []
    for result_folder in valid_result_folders:
        experiment_folder_path = f"{result_paths["results_base_folder"]}/{result_folder}"
        experiment_filenames = get_all_experiments_from_experiment_folder(experiment_folder_path)
        for experiment_filename in experiment_filenames:
            experiment_name = get_experiment_name_from_experiment_filename(experiment_filename)
            if experiment_name in regression_tests:
                continue
            regression_tests.append(experiment_name)
    return sorted(regression_tests, key=test_sort_key)

def sort_valid_result_folders_new_to_old(valid_result_folders:list) -> list:
    sorted_valid_result_folders = []
    for result_folder in valid_result_folders:
        time = get_datetime_from_folder_name(result_folder)
        version = Version(get_semantic_version_from_folder_name(result_folder))
        sorted_valid_result_folders.append((result_folder, time, version))
        sorted_valid_result_folders.sort(reverse=True, key=lambda x: (x[1], x[2]))
    return sorted_valid_result_folders

def build_prev_col_map(sorted_valid_result_folders:list) -> dict:
    """For each column (1-based, as used in `summaries`), the column to diff its
    indicators against = the "previous version". Flavor-aware: prefer the newest
    strictly-older result of the SAME flavor (e.g. 20.1.0.m -> 20.0.x.m), and if
    there is none, fall back to the newest strictly-older result with NO flavor
    (the mainline reference, e.g. 20.1.0.m -> 19.0.0). Returns col -> prev_col|None."""
    metas = []  # (col, flavor, version)
    for i, (folder, _, _) in enumerate(sorted_valid_result_folders):
        major, minor, patch, flavor, *_ = parse_folder_name(folder)
        metas.append((i + 1, flavor, Version(f"{major}.{minor}.{patch}")))
    prev_col_map = {}
    for col, flavor, ver in metas:
        same_flavor_older = [(c, v) for (c, f, v) in metas if f == flavor and v < ver]
        if same_flavor_older:
            prev_col_map[col] = max(same_flavor_older, key=lambda cv: cv[1])[0]
            continue
        mainline_older = [(c, v) for (c, f, v) in metas if f == "" and v < ver]
        prev_col_map[col] = max(mainline_older, key=lambda cv: cv[1])[0] if mainline_older else None
    return prev_col_map

def get_all_experiments_from_experiment_folder(experiment_folder_path:str):
    return _bin_glob(experiment_folder_path)

def get_experiment_name_from_experiment_filename(experiment_filename:str) -> str:
    return experiment_filename.split("__")[1][:-4]

# Set to True (by full.py for -all-versions) to drop the "<= version under test"
# filter below, so EVERY result folder in ResultsBaseDir becomes a report column
# -- including versions NEWER than the one whose run triggered the report.
report_include_all_versions = False

def get_valid_result_folders(version:str, result_paths:dict) -> list:
    valid_result_folders = []
    if not os.path.isdir(result_paths["results_base_folder"]):
        return valid_result_folders
    target = _try_parse_version(version)
    result_folder_candidates = os.listdir(result_paths["results_base_folder"])
    for candidate in result_folder_candidates:
        if not folder_is_results_folder(candidate):
            continue
        major, minor, patch, flavor, architecture, sf, multithreading, local_machine_name, time, hash = parse_folder_name(candidate)
        # Non-semver `version` (e.g. "local") is treated as newer than any
        # historical numeric version, so all candidates are valid for compare.
        if report_include_all_versions or target is None or Version(f"{major}.{minor}.{patch}") <= target:
            # Skip folders with no stored experiments (*.bin) -- they only
            # produce empty report columns. These are typically abandoned runs
            # or old preset-named folders (e.g. 20_0_1_x64-linux-cmake_... and
            # 20_0_1_x64-windows-{cmake,msbuild}_... instead of 20_0_1_{l,c,m}_...),
            # which carry 0 experiments.
            if not _bin_glob(f"{result_paths['results_base_folder']}/{candidate}"):
                continue
            valid_result_folders.append(candidate)

    return valid_result_folders

def folder_is_results_folder(result_folder_name:str) -> bool:
    # A result folder starts with a numeric major_minor_patch version. Accepts
    # both the current short names (e.g. 20_1_0_m, 20_1_0_m_<ts>_<hash>) and the
    # historical long names (e.g. 17_4_5_x64_SF_C1C2C3_OVSRV07[_<ts>_<hash>]).
    parts = result_folder_name.split("_")
    if len(parts) < 3:
        return False
    major, minor, patch = parts[0:3]
    return major.isdigit() and minor.isdigit() and patch.isdigit()

def parse_folder_name(result_folder_name:str) -> list:
    """Always returns 10 elements:
    [major, minor, patch, flavor, arch, sf, multitask, machine, time, hash].
    Parsed by content so both the current short names (20_1_0_m[_<ts>_<hash>])
    and historical long names (17_4_5_x64_SF_C1C2C3_OVSRV07[_<ts>_<hash>]) work;
    fields absent in a given name come back as empty strings."""
    parts = result_folder_name.split("_")
    major, minor, patch = (parts + ["", "", ""])[0:3]
    rest = parts[3:]
    # trailing timestamp(14 digits) + abbreviated hash
    time = hash = ""
    if len(rest) >= 2 and re.fullmatch(r"\d{14}", rest[-2]):
        time, hash = rest[-2], rest[-1]
        rest = rest[:-2]
    flavor = ""
    if rest and re.fullmatch(r"[a-z]", rest[0]):          # single-letter flavor (m/c/l)
        flavor, rest = rest[0], rest[1:]
    arch = ""
    if rest and re.match(r"x(64|86)", rest[0]):           # x64, x86, x64-windows-msbuild, ...
        arch, rest = rest[0], rest[1:]
    sf = ""
    if rest and rest[0] == "SF":                          # vestigial status-flags marker
        sf, rest = rest[0], rest[1:]
    multitask = ""
    if rest and re.fullmatch(r"[SC]1[SC]2[SC]3", rest[0]):
        multitask, rest = rest[0], rest[1:]
    machine = rest[0] if rest else ""
    return [major, minor, patch, flavor, arch, sf, multitask, machine, time, hash]

def get_datetime_from_folder_name(result_folder_name:str) -> datetime:
    # Timestamp is the 14-digit part (present only for local-build folders).
    for part in result_folder_name.split("_"):
        if re.fullmatch(r"\d{14}", part):
            return datetime.strptime(part, r'%Y%m%d%H%M%S')
    return datetime(1970, 1, 1)

def get_semantic_version_from_folder_name(result_folder_name:str):
    major, minor, patch, *_ = parse_folder_name(result_folder_name)
    return f"{major}.{minor}.{patch}"

def get_display_version_from_folder_name(result_folder_name:str) -> str:
    """Numeric version + optional flavor suffix, e.g. "20.0.0.c" or "17.9.5"."""
    major, minor, patch, flavor, *_ = parse_folder_name(result_folder_name)
    return f"{major}.{minor}.{patch}" + (f".{flavor}" if flavor else "")

def get_version_range(valid_result_folders:list) -> tuple:
    """Returns (newest_display, oldest_display) where the strings include any
    flavor suffix so reports for different flavors land in distinct files."""
    if not valid_result_folders:
        return ("", "")
    newest_numeric = get_semantic_version_from_folder_name(valid_result_folders[0])
    oldest_numeric = newest_numeric
    newest_display = get_display_version_from_folder_name(valid_result_folders[0])
    oldest_display = newest_display
    for result_folder_name in valid_result_folders:
        version = get_semantic_version_from_folder_name(result_folder_name)
        display = get_display_version_from_folder_name(result_folder_name)
        if Version(version) > Version(newest_numeric):
            newest_numeric = version
            newest_display = display
        if Version(version) < Version(oldest_numeric):
            oldest_numeric = version
            oldest_display = display
    return (newest_display, oldest_display)

def get_full_regression_test_environment_string(local_machine_parameters:dict, geodms_paths:dict, regression_test_paths:dict, result_paths:dict) -> str:
    full_regression_test_string = ""
    for key in local_machine_parameters:
        value = local_machine_parameters[key]
        full_regression_test_string = f"{full_regression_test_string};{key}={value}"

    for key in geodms_paths:
        value = geodms_paths[key]
        full_regression_test_string = f"{full_regression_test_string};{key}={value}"
    
    for key in regression_test_paths:
        value = regression_test_paths[key]
        full_regression_test_string = f"{full_regression_test_string};{key}={value}"
    
    for key in result_paths:
        value = result_paths[key]
        full_regression_test_string = f"{full_regression_test_string};{key}={value}"

    return full_regression_test_string[1:]

def import_module_from_path(path):
    module_name = os.path.splitext(os.path.basename(path))[0]  # Extract "module" from "module.py"

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise ImportError(f"Can't find spec for {module_name} at {path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    globals()[module_name] = module  # Inject into global namespace
    spec.loader.exec_module(module)
    
    return module

def get_geodms_paths(version:str) -> dict:
    assert(version)
    geodms_profiler_env_key = f"%GeodmsProfiler%"
    geodms_profiler = os.path.expandvars(geodms_profiler_env_key)
    geodms_paths = {}
    geodms_paths["GeoDmsPlatform"] = "x64"
    geodms_paths["GeoDmsPath"] = os.path.expandvars(f"%ProgramFiles%/ObjectVision/GeoDms{version}")
    geodms_paths["GeoDmsProfilerPath"] = geodms_profiler if geodms_profiler_env_key!=geodms_profiler else f"{geodms_paths["GeoDmsPath"]}/profiler.py"
    geodms_paths["GeoDmsRunPath"] = f"{geodms_paths["GeoDmsPath"]}/GeoDmsRun.exe"
    geodms_paths["GeoDmsGuiQtPath"] = f"{geodms_paths["GeoDmsPath"]}/GeoDmsGuiQt.exe"
    return geodms_paths

def get_git_repo_latest_commit_timestamp_and_hash(local_git_repo:str) -> list[datetime, str]:
    if local_git_repo == "latest":
        time_object_full = datetime.now()
        time_object = time_object_full.replace(minute=0, second=0, microsecond=0)
        abbreviated_hash = "latest"
        return [time_object, abbreviated_hash]

    # check if repo is clean
    repo_porcelain_status = str(subprocess.check_output(r"git status --porcelain", cwd=local_git_repo))
    if len(repo_porcelain_status)>4:
        raise(Exception("git repo has non-empty porcelain status, use 'latest' or make sure there are no uncommitted changes"))

    # commit time
    commit_time = str(subprocess.check_output(r"git show -s --format=%cd --date=format:%Y%m%d%H%M%S HEAD", cwd=local_git_repo))
    commit_time = commit_time[2:-3]
    time_object = datetime.strptime(commit_time, r'%Y%m%d%H%M%S')

    # abbreviated hash
    abbreviated_hash = str(subprocess.check_output(r"git show -s --format=%h HEAD", cwd=local_git_repo))
    abbreviated_hash = abbreviated_hash[2:-3]

    return [time_object, abbreviated_hash]

def get_result_folder_name(version:str, geodms_paths:dict, MT1:str, MT2:str, MT3:str, local_git_repo:str=None) -> str:
    # datetime format: git show
    # Folder identity = version (incl. flavor), e.g. "20_1_0_m". Architecture
    # (always x64 since 32-bit is gone), the SF/multitasking flags (dropped from
    # the report) and the machine name (one ResultsBaseDir holds one machine's
    # results) are no longer encoded. Local builds still get a timestamp+hash
    # suffix to distinguish successive builds of the same version.
    folder_name = version.replace(".", "_")
    if local_git_repo:
        latest_commit_timestamp, abbreviated_hash = get_git_repo_latest_commit_timestamp_and_hash(local_git_repo)
        folder_name = f"{folder_name}_{latest_commit_timestamp.strftime('%Y%m%d%H%M%S')}_{abbreviated_hash}"
    return folder_name

def get_result_paths(geodms_paths:dict, regression_test_paths:dict, version:str, MT1:str, MT2:str, MT3:str) -> dict:
    result_paths = {}
    # Results tree base. Prefer the configured ResultsBaseDir (full.py sets it
    # from the RegressionResultsDir setting, default {LocalDataDir}/GeoDMS-Test)
    # so results live under C:\LocalData, not the source/tst tree. Falls back to
    # TstDir for callers that don't set it (legacy behavior).
    result_base = regression_test_paths.get("ResultsBaseDir") or regression_test_paths["TstDir"]
    result_paths["results_base_folder"] = f"{result_base}/Regression/GeoDMSTestResults"
    result_paths["results_folder"] = f"{result_paths["results_base_folder"]}/{get_result_folder_name(version, geodms_paths, MT1, MT2, MT3)}"
    result_paths["results_log_folder"] = f"{result_paths["results_folder"]}/log"
    return result_paths

def get_local_machine_name() -> str:
    return platform.node()

def header_stuff_to_be_removed_in_future(local_machine_parameters:dict, result_paths:dict, MT1:str, MT2:str, MT3:str):
    """
    needed for:
    regression/cfg/stam.dms /results/VersionInfo/results_folder results/VersionInfo/all /results/VersionInfo/ComputerName /results/VersionInfo/RegionalSettings
    operator/cfg/operator.dms /results/Regression/results_folder /results/Regression/t010_operator_test
    """
    local_machine_name = get_local_machine_name()
    date_format = "YYYYMMDD"
    status_flags = f"{MT1}{MT2}{MT3}"

    if not os.path.exists(local_machine_parameters["tmpFileDir"]):
        os.makedirs(local_machine_parameters["tmpFileDir"])

    with open(f"{local_machine_parameters["tmpFileDir"]}/computername.txt", "w") as f:
        f.write(local_machine_name)

    with open(f"{local_machine_parameters["tmpFileDir"]}/date_format.txt", "w") as f:
        f.write(date_format)

    with open(f"{local_machine_parameters["tmpFileDir"]}/statusflags.txt", "w") as f:
        f.write(status_flags)

    result_data_dir = f"{result_paths["results_folder"]}/result"
    os.makedirs(result_data_dir, exist_ok=True)
    with open(f"{local_machine_parameters["tmpFileDir"]}/results_folder.txt", "w") as f:
        f.write(result_data_dir)
    return

def get_table_title_html_template() -> str:
    return '<td class="corner"><div class="report-title">@@@TITLE@@@</div></td>\n'

def get_table_col_header_html_template() -> str:
    return '<td class="colhdr"><div class="ver">@@@VERSION@@@</div>\
    <div class="subhdr">@@@GITSHORTHASH@@@</div>\
    <div class="subhdr">@@@TOTALTIME@@@ &middot; @@@SUCCESSRATIO@@@ ok</div></td>\n'

    #'<td style="border-right: 0px; border-bottom: 1px solid #BEBEE6; box-shadow: 0 1px 0 #FFFFFF; padding: 0px;"><B>@@@VERSION@@@</B><BR>\
    #<B>Release</B><BR>\
    #<B>@@@PLATFORM@@@</B><BR>\
    #<B>@@@MULTITASKING@@@</B><BR>\
    #<B>@@@COMPUTER_NAME@@@</B><BR> </td>\n'

def get_table_header_row(summary_row:list) -> str:
    table_header_row = get_table_title_html_template()
    table_header_row = table_header_row.replace("@@@TITLE@@@", summary_row[0])
    for summary_col_header in summary_row[1:]:
        table_col_header = get_table_col_header_html_template()
        table_col_header = table_col_header.replace("@@@GITSHORTHASH@@@", summary_col_header["hash"])
        table_col_header = table_col_header.replace("@@@VERSION@@@", summary_col_header["version"])
        table_col_header = table_col_header.replace("@@@PLATFORM@@@", summary_col_header["platform"])
        table_col_header = table_col_header.replace("@@@TOTALTIME@@@", format_duration(summary_col_header["total_duration"]))
        table_col_header = table_col_header.replace("@@@SUCCESSRATIO@@@", f"{summary_col_header["success_ratio"][0]}/{summary_col_header["success_ratio"][1]}")
        table_col_header = table_col_header.replace("@@@COMPUTER_NAME@@@", summary_col_header["computer_name"])
        table_header_row += table_col_header
        
    return f'<tr class="hdr">{table_header_row}</tr>'

def get_table_rows(result_paths:dict, regression_test_summaries:list[list]) -> str:
    rows = ""    
    for index, summary_row in enumerate(regression_test_summaries):
        if index == 0:
            rows += get_table_header_row(summary_row)
            continue
        rows += get_table_regression_test_row(result_paths, summary_row)
    return rows

def render_regression_test_result_html(version_range:tuple, result_paths:dict, regression_test_summaries:dict) -> str:
    result_html = '<!DOCTYPE html>\
    <html>\
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />\
        <head>\
            <meta charset="UTF-8">\
            <style>\
              body { font-family: "Aptos","Aptos Display","Segoe UI Variable","Segoe UI",system-ui,-apple-system,sans-serif; color:#1c1c1a; background:#fbfbfa; margin:20px; font-size:13px; }\
              table.report { border-collapse:separate; border-spacing:0; }\
              table.report td { padding:7px 10px; vertical-align:top; border-bottom:1px solid #ececE6; }\
              tr.hdr td { border-bottom:1.5px solid #d7d7d0; position:sticky; top:0; background:#fbfbfa; }\
              td.corner .report-title { font-weight:500; font-size:16px; white-space:nowrap; }\
              td.colhdr .ver { font-weight:500; font-size:14px; }\
              td.colhdr .subhdr { color:#86867e; font-size:11.5px; }\
              td.testname { white-space:nowrap; font-weight:500; }\
              td.testname button { border:0; background:transparent; font:inherit; font-weight:500; color:#1c1c1a; cursor:pointer; padding:0; text-align:left; }\
              td.testname button:hover { color:#534ab7; text-decoration:underline; }\
              td.cell { border-left:3px solid transparent; }\
              td.cell.ok { background:#d6efce; border-left-color:#2e9e5b; }\
              td.cell.fail { background:#ffd1d1; border-left-color:#d6453d; }\
              td.cell.warn { background:#ffe4b8; border-left-color:#d98a1f; }\
              td.cell.skip { background:#ececE8; border-left-color:#b8b8b0; }\
              summary { cursor:pointer; list-style:none; outline:none; display:flex; align-items:center; flex-wrap:wrap; gap:3px 8px; } summary::-webkit-details-marker { display:none; }\
              .pill { display:inline-flex; align-items:center; line-height:1; font-size:11.5px; font-weight:500; padding:3px 10px; border-radius:999px; color:#fff; }\
              .pill.ok { background:#2e9e5b; } .pill.fail { background:#d6453d; } .pill.warn { background:#cf8420; } .pill.timeout { background:#3a78c2; } .pill.skip { background:#9a9a92; }\
              .code { color:#a6a69e; font-size:11px; } .code:empty { display:none; }\
              .meta { color:#6b6b64; font-size:11.5px; margin-top:6px; white-space:nowrap; }\
              .metrics { color:#444441; font-size:12px; margin-top:3px; white-space:nowrap; font-variant-numeric:tabular-nums; }\
              .ind { margin-top:6px; padding-top:5px; border-top:1px solid #ececE6; font-size:11.5px; color:#5f5e5a; }\
              .ind-line.changed { color:#a32d2d; font-weight:500; }\
              td.testname .testdesc { font-weight:400; font-style:italic; color:#86867e; font-size:11px; white-space:normal; max-width:300px; margin-top:3px; }\
              .flag { color:#a32d2d; font-size:11px; font-weight:500; white-space:nowrap; }\
              .perf-warn { color:#b8860b; font-weight:600; }\
              .perf-bad { color:#a32d2d; font-weight:700; }\
              .perfbadge { font-size:10px; font-weight:600; white-space:nowrap; }\
              .refpill { display:inline-flex; align-items:center; line-height:1; margin-left:auto; background:#2d6da3; color:#fff; font-size:10px; font-weight:600; padding:3px 7px; border-radius:9px; letter-spacing:.3px; }\
              .links { margin-top:7px; font-size:11px; } .links a { color:#9a9a92; text-decoration:none; margin-right:9px; }\
              .links a:hover { color:#534ab7; text-decoration:underline; }\
            </style>\
        </head>\
        <body>\
            <script>\
                function copy_href(event, element) {\
                event.preventDefault(); \
                const rawPath = element.getAttribute("href");\
                navigator.clipboard.writeText(rawPath)\
                    .then(() => {\
                    alert("Copied the path: " + rawPath);\
                    })\
                    .catch(err => {\
                    console.error("Failed to copy path: ", err);\
                    });\
                }\
                function expand_test_row(element_class_name) {\
                    console.log("TEST");\
                    var elements = document.getElementsByClassName(element_class_name);\
                    const attribute_name = "open";\
                    console.log(elements);\
                    for (const sum_det_element of elements)\
                    {\
                        if (sum_det_element==null) {\
                            continue; \
                        }\
                        const attribute = sum_det_element.getAttribute(attribute_name);\
                        if (attribute == null) {\
                            sum_det_element.setAttribute(attribute_name, "");\
                            console.log("open");\
                        }\
                        else {\
                            sum_det_element.removeAttribute(attribute_name);\
                            console.log("close");\
                        }\
                    }\
                }\
            </script>\
            <table class="report">\
                @@@TABLE_CONTENT@@@\
            </Table>\
        </body>\
    </html>'

    #//sum_det_element.setAttribute(attribute_name, "");\
    #//sum_det_element.removeAttribute(attribute_name);\
    table_content = get_table_rows(result_paths, regression_test_summaries)
    result_html = result_html.replace("@@@TABLE_CONTENT@@@", table_content)

    final_html_filename = f"{result_paths['results_base_folder']}/reports/{version_range[0].replace(".","_")}___{version_range[1].replace(".","_")}.html"
    report_dir = f"{result_paths['results_base_folder']}/reports"
    if not os.path.isdir(report_dir):
        os.makedirs(report_dir)
    with open(final_html_filename, "w", encoding="utf-8") as f:  # report declares <meta charset="UTF-8">
        f.write(result_html)
    return final_html_filename

def collect_and_generate_test_results(version:str, result_paths:dict):
    valid_result_folders        = get_valid_result_folders(version, result_paths)
    version_range               = get_version_range(valid_result_folders)
    # Anchor the report filename and title to the just-run flavor so per-flavor
    # runs produce distinct reports (20_0_0_c vs 20_0_0_m even though both are
    # numerically 20.0.0).
    if version:
        version_range = (version, version_range[1])
    sorted_valid_result_folders = sort_valid_result_folders_new_to_old(valid_result_folders)
    regression_test_names       = get_all_regression_tests_by_name(result_paths, valid_result_folders)
    regression_test_files       = collect_experiment_filenames_per_experiment(regression_test_names, result_paths, sorted_valid_result_folders)
    regression_test_summaries   = collect_experiment_summaries(version_range, result_paths, sorted_valid_result_folders, regression_test_names, regression_test_files)
    final_html_file = render_regression_test_result_html(version_range, result_paths, regression_test_summaries)
    webbrowser.open(final_html_file)
    return

def add_exp(exps:list, name, cmd, exp_fldr, env=None, cwd=None, log_fn=None, indicator_results_file=None, bin_fn=None, file_comparison:tuple=None, store_results=True, pre_clean=None) -> list:
    exps.append(profiler.Experiment(name=name, command=cmd, experiment_folder=exp_fldr, environment_variables=env, cwd=cwd, geodms_logfile=log_fn, indicator_results_file=indicator_results_file, binary_experiment_file=bin_fn, file_comparison=file_comparison, store_results=store_results, pre_clean=pre_clean))
    return exps

def add_cexp(exps:list, name, cmd, exp_fldr, env=None, cwd=None, log_fn=None, bin_fn=None, file_comparison:tuple=None) -> list:
    exps.append(profiler.Experiment(name=name, command=cmd, experiment_folder=exp_fldr, environment_variables=env, cwd=cwd, geodms_logfile=log_fn, binary_experiment_file=bin_fn, file_comparison=file_comparison))
    return exps

def run_experiments(exps):
    profiler.RunExperiments(exps)