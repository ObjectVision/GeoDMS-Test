#!/usr/bin/env bash
# set_geodms_platform.sh — sourced by unit_linux.sh
# Sets GEODMS_RUN_PATH and GEODMS_GUI_QT_PATH based on the build config.
#
# Usage: source generic/set_geodms_platform.sh <config>
# Config: linux-x64-debug | linux-x64-release
#
# Requires GEODMS_ROOT to be set (the GeoDMS repository root).

_config="${1:-linux-x64-release}"

if [[ -z "${GEODMS_ROOT:-}" ]]; then
    echo "ERROR: GEODMS_ROOT is not set." >&2
    return 1
fi

case "$_config" in
    linux-x64-debug)
        GEODMS_BIN="$GEODMS_ROOT/build/linux-x64-debug/bin"
        ;;
    linux-x64-release)
        GEODMS_BIN="$GEODMS_ROOT/build/linux-x64-release/bin"
        ;;
    *)
        echo "ERROR: unknown config '$_config'." >&2
        echo "       Valid values: linux-x64-debug, linux-x64-release" >&2
        return 1
        ;;
esac

GEODMS_RUN_PATH="$GEODMS_BIN/GeoDmsRun"
GEODMS_GUI_QT_PATH="$GEODMS_BIN/GeoDmsGuiQt"

if [[ ! -x "$GEODMS_RUN_PATH" ]]; then
    echo "ERROR: GeoDmsRun not found or not executable: $GEODMS_RUN_PATH" >&2
    echo "       Run: cmake --build --preset $_config" >&2
    return 1
fi

echo "Testing $GEODMS_RUN_PATH"
