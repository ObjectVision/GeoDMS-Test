#!/usr/bin/env bash
# gui_instance.sh — run one GeoDmsGuiQt dmsscript test, record pass/fail.
#
# Mirrors batch/Unit/GUIInstance.bat. Called as a function from unit_linux.sh.
#
# Usage: gui_instance <dmsscript> <dms_file> <result_file> [flag1] [flag2] [flag3]
gui_instance() {
    local dmsscript="$1"
    local dms_file="$2"
    local result_file="$3"
    local f1="${4:-S1}" f2="${5:-S2}" f3="${6:-S3}"

    if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
        echo "NOTE: gui_instance skipped — no DISPLAY/WAYLAND_DISPLAY"
        echo "$GEODMS_GUI_QT_PATH /T$dmsscript /$f1 /$f2 /$f3 $dms_file  SKIPPED (no display)" >> "$RESULT_FILENAME"
        return
    fi

    # /SM enables RSF_DebugMode (DetailPage diagnostic rows) and /SH enables
    # RSF_ShowThousandSeparator (number formatting) — both match the Windows
    # dev environment that captured the norm files; on Linux there's no
    # registry persistence so we set them here.
    echo "****************"
    echo "Test: $GEODMS_GUI_QT_PATH /T$dmsscript /$f1 /$f2 /$f3 /SM /SH $dms_file"
    "$GEODMS_GUI_QT_PATH" "/T$dmsscript" "/$f1" "/$f2" "/$f3" "/SM" "/SH" "$dms_file"
    local rc=$?
    echo ""

    if [[ $rc -eq 0 ]]; then
        if [[ -n "$result_file" && -f "$result_file" ]]; then
            cat "$result_file"
            cat "$result_file" >> "$RESULT_FILENAME"
        fi
    else
        echo "TEST FAILED (exit $rc)"
        echo "$GEODMS_GUI_QT_PATH /T$dmsscript /$f1 /$f2 /$f3 $dms_file  FAILED (exit $rc)" >> "$RESULT_FILENAME"
        REGR_RESULT=FAILED
    fi

    echo "end test"
    echo "****************"
    echo ""
}
