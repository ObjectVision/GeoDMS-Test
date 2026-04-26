#!/usr/bin/env bash
# instance.sh — run one GeoDmsRun test, record pass/fail in RESULT_FILENAME.
# Called as a function from unit_linux.sh (not directly executed).
#
# Usage: geodms_instance <dms_file> <item> <result_file> [flag1] [flag2] [flag3]
geodms_instance() {
    local dms_file="$1"
    local item="$2"
    local result_file="$3"
    local f1="${4:-S1}" f2="${5:-S2}" f3="${6:-S3}"

    echo "****************"
    echo "Test: $GEODMS_RUN_PATH /$f1 /$f2 /$f3 $dms_file $item"
    "$GEODMS_RUN_PATH" "/$f1" "/$f2" "/$f3" "$dms_file" "$item"
    local rc=$?
    echo ""

    if [[ $rc -eq 0 ]]; then
        if [[ -f "$result_file" ]]; then
            cat "$result_file"
            cat "$result_file" >> "$RESULT_FILENAME"
        fi
    else
        echo "TEST FAILED (exit $rc)"
        echo "$GEODMS_RUN_PATH /$f1 /$f2 /$f3 $dms_file $item  FAILED (exit $rc)" >> "$RESULT_FILENAME"
        REGR_RESULT=FAILED
    fi

    echo "end test"
    echo "****************"
    echo ""
}
