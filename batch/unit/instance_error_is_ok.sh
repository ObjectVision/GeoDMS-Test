#!/usr/bin/env bash
# instance_error_is_ok.sh — run a GeoDmsRun test that is expected to fail
# (exit code 1 or 2). Records pass/fail in RESULT_FILENAME.
# Called as a function from unit_linux.sh (not directly executed).
#
# Usage: geodms_instance_error_is_ok <dms_file> <item> <result_file> [flag1] [flag2] [flag3]
geodms_instance_error_is_ok() {
    local dms_file="$1"
    local item="$2"
    local result_file="$3"
    local f1="${4:-S1}" f2="${5:-S2}" f3="${6:-S3}"

    echo "****************"
    echo "Test (error expected): $GEODMS_RUN_PATH /$f1 /$f2 /$f3 $dms_file $item"
    "$GEODMS_RUN_PATH" "/$f1" "/$f2" "/$f3" "$dms_file" "$item"
    local rc=$?
    echo ""

    if [[ $rc -eq 0 ]]; then
        echo "TEST FAILED — an error was expected but none occurred"
        echo "$GEODMS_RUN_PATH /$f1 /$f2 /$f3 $dms_file $item  FAILED, ERROR EXPECTED" >> "$RESULT_FILENAME"
        REGR_RESULT=FAILED
    elif [[ $rc -ne 1 && $rc -ne 2 ]]; then
        echo "TEST FAILED — unexpected exit code $rc (expected 1 or 2)"
        echo "$GEODMS_RUN_PATH /$f1 /$f2 /$f3 $dms_file $item  FAILED (exit $rc, expected 1 or 2)" >> "$RESULT_FILENAME"
        REGR_RESULT=FAILED
    fi

    echo "end test"
    echo "****************"
    echo ""
}
