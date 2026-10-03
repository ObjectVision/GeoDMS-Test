#!/usr/bin/env bash
# instance.sh — run one GeoDmsRun test, record pass/fail in RESULT_FILENAME.
# Called as a function from unit_linux.sh (not directly executed).
#
# Usage: geodms_instance <dms_file> <item> <result_file> [flag1] [flag2] [flag3]
#
# A test passes when GeoDmsRun exits 0 AND leaves <result_file>, its test log, empty: a
# configuration writes into that log only when it fails ("... result: not OK"), so a log
# with any text in it is a failing test, whatever it says. Such a test gets a FAILED line
# in the aggregate and sets REGR_RESULT=FAILED, the exit status of unit_linux.sh that the
# .l setup gates its install on. Until 2026-10-03 the log was only copied into the
# aggregate and REGR_RESULT stayed OK. Mirrors batch/unit/Instance.bat, which also says why
# the log is deleted before the run.
geodms_instance() {
    local dms_file="$1"
    local item="$2"
    local result_file="$3"
    local f1="${4:-S1}" f2="${5:-S2}" f3="${6:-S3}"

    # /SH enables RSF_ShowThousandSeparator so number formatting in test
    # output matches Windows-captured norm files (Windows persists this via
    # registry; Linux has no equivalent persistence so we set it here).
    echo "****************"
    echo "Test: $GEODMS_RUN_PATH /$f1 /$f2 /$f3 /SH $dms_file $item"
    rm -f "$result_file"
    "$GEODMS_RUN_PATH" "/$f1" "/$f2" "/$f3" "/SH" "$dms_file" "$item"
    local rc=$?
    echo ""

    if [[ $rc -eq 0 ]]; then
        if [[ -f "$result_file" ]] && grep -q '[^[:space:]]' "$result_file"; then
            cat "$result_file"
            echo "TEST FAILED (the test log is not empty)"
            echo "$GEODMS_RUN_PATH /$f1 /$f2 /$f3 $dms_file $item  FAILED, its test log reads:" >> "$RESULT_FILENAME"
            cat "$result_file" >> "$RESULT_FILENAME"
            REGR_RESULT=FAILED
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
