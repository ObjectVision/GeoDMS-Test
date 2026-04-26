#!/usr/bin/env bash
# statistics.sh — run the statistics test. Called as a function from unit_linux.sh.
geodms_statistics() {
    local cmd="$GEODMS_RUN_PATH /S1 /S2 /S3 \"$TST_DIR/Unit/operator/cfg/select_orgrel.dms\" @statistics full/id"
    echo "**************** Statistics"
    echo "Test: $cmd"
    "$GEODMS_RUN_PATH" /S1 /S2 /S3 "$TST_DIR/Unit/operator/cfg/select_orgrel.dms" "@statistics" "full/id"
    local rc=$?
    echo ""
    if [[ $rc -ne 0 ]]; then
        echo "TEST FAILED (exit $rc)"
        echo "$cmd  FAILED (exit $rc)" >> "$RESULT_FILENAME"
        REGR_RESULT=FAILED
    fi
    echo "end test"
    echo "****************"
    echo ""
}
