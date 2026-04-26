#!/usr/bin/env bash
# unit_linux.sh — Linux equivalent of unit_flagged.bat
# Runs the full GeoDMS unit test suite using a CMake Linux build.
#
# Usage: bash unit_linux.sh [linux-x64-debug|linux-x64-release] [flag1] [flag2] [flag3]
#
# Environment:
#   GEODMS_ROOT       path to the GeoDMS repository (set by TestLinux*.sh)
#   GEODMS_LOCAL_DATA local data root (default: ~/geodms_localdata)

set -uo pipefail

BATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TST_DIR="$(dirname "$BATCH_DIR")"

config="${1:-linux-x64-release}"
flag1="${2:-S1}"
flag2="${3:-S2}"
flag3="${4:-S3}"

# ---------------------------------------------------------------------------
# Platform — sets GEODMS_RUN_PATH and GEODMS_GUI_QT_PATH
# ---------------------------------------------------------------------------
source "$BATCH_DIR/generic/set_geodms_platform.sh" "$config"

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------
LOCAL_DATA_DIR="${GEODMS_LOCAL_DATA:-$HOME/geodms_localdata}"
LOCAL_DATA_DIR_REGRESSION="$LOCAL_DATA_DIR/regression"
RESULT_DIR="$LOCAL_DATA_DIR/GeoDMSTestResults"
RESULT_FILENAME="$RESULT_DIR/unit/result.txt"

# Tell GeoDmsRun to use the same local data directory as this script
export GEODMS_directories_LocalDataDir="$LOCAL_DATA_DIR"

mkdir -p "$LOCAL_DATA_DIR_REGRESSION/log"
mkdir -p "$RESULT_DIR/unit/operator"
mkdir -p "$RESULT_DIR/unit/storage"
mkdir -p "$RESULT_DIR/unit/gui"
mkdir -p "$RESULT_DIR/unit/integrity_check"
mkdir -p "$RESULT_DIR/unit/Namespaces"
mkdir -p "$RESULT_DIR/unit/other"
mkdir -p "$RESULT_DIR/unit/unit"
mkdir -p "$RESULT_DIR/unit/grid"
mkdir -p "$RESULT_DIR/unit/crs"
mkdir -p "$RESULT_DIR/unit/Template"

# ---------------------------------------------------------------------------
# Load helper functions
# ---------------------------------------------------------------------------
source "$BATCH_DIR/unit/instance.sh"
source "$BATCH_DIR/unit/instance_error_is_ok.sh"
source "$BATCH_DIR/unit/statistics.sh"

# ---------------------------------------------------------------------------
# Clean old results
# ---------------------------------------------------------------------------
rm -f "$RESULT_DIR"/unit/operator/*.txt
rm -f "$RESULT_DIR"/unit/storage/*.txt "$RESULT_DIR"/unit/storage/*.dbf \
      "$RESULT_DIR"/unit/storage/*.tif "$RESULT_DIR"/unit/storage/*.tfw
rm -rf "$RESULT_DIR"/unit/storage/OneRecord.fss
rm -rf "$RESULT_DIR"/unit/storage/ZeroRecord.fss
rm -f "$RESULT_DIR"/unit/gui/*.txt
rm -f "$RESULT_DIR"/unit/integrity_check/*.txt
rm -f "$RESULT_DIR"/unit/Namespaces/*.txt
rm -f "$RESULT_DIR"/unit/other/*.txt
rm -f "$RESULT_FILENAME"

REGR_RESULT=OK

echo ""
echo "************************"
echo "Starting UNIT test for: $GEODMS_RUN_PATH"
echo "Config:  $config  flags: /$flag1 /$flag2 /$flag3"
echo "TstDir:  $TST_DIR"
echo "Results: $RESULT_DIR"
echo "************************"
echo ""

echo "Unit Test Results for: $GEODMS_RUN_PATH" > "$RESULT_FILENAME"
echo "" >> "$RESULT_FILENAME"

# ---------------------------------------------------------------------------
# GUI tests — skip if no display is available
# ---------------------------------------------------------------------------
if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]; then
    export GEODMS_DIRECTORIES_LOCALDATAPROJDIR="$LOCAL_DATA_DIR_REGRESSION/gui"
    # DPGeneral tests require .tmp baselines written by a prior GUI run; skip if absent.
    if [[ -f "$RESULT_DIR/Unit/GUI/DPGeneral_explicit_supplier_error.tmp" ]]; then
        geodms_instance "$TST_DIR/Unit/GUI/cfg/DPGeneral_explicit_supplier_error.dms" test_log \
            "$RESULT_DIR/unit/gui/DPGeneral_ES_error.txt" $flag1 $flag2 $flag3
    else
        echo "NOTE: DPGeneral_explicit_supplier_error.tmp missing — skipping (run GUI first)"
        echo "NOTE: DPGeneral_explicit_supplier_error skipped (no GUI baseline .tmp)" >> "$RESULT_FILENAME"
    fi
    if [[ -f "$RESULT_DIR/Unit/GUI/DPGeneral_missing_file_error.tmp" ]]; then
        geodms_instance "$TST_DIR/Unit/GUI/cfg/DPGeneral_missing_file_error.dms" test_log \
            "$RESULT_DIR/unit/gui/DPGeneral_MF_error.txt" $flag1 $flag2 $flag3
    else
        echo "NOTE: DPGeneral_missing_file_error.tmp missing — skipping (run GUI first)"
        echo "NOTE: DPGeneral_missing_file_error skipped (no GUI baseline .tmp)" >> "$RESULT_FILENAME"
    fi
    geodms_instance "$TST_DIR/Unit/GUI/cfg/background_layer.dms" test_log \
        "$RESULT_DIR/unit/gui/background_layer_error.txt" $flag1 $flag2 $flag3
else
    echo "NOTE: DISPLAY not set — skipping GUI tests"
    echo "NOTE: GUI tests skipped (no display)" >> "$RESULT_FILENAME"
fi

# ---------------------------------------------------------------------------
# Operator tests
# ---------------------------------------------------------------------------
export GEODMS_DIRECTORIES_LOCALDATAPROJDIR="$LOCAL_DATA_DIR_REGRESSION/operator"
geodms_instance "$TST_DIR/Unit/operator/cfg/subitem.dms"          test_log "$RESULT_DIR/unit/operator/subitem.txt"          $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/operator/cfg/connect.dms"          test_log "$RESULT_DIR/unit/operator/connect_point_arc.txt" $flag1 $flag2 $flag3

sleep 2
geodms_instance "$TST_DIR/Unit/operator/cfg/xml_parse.dms"        test_log "$RESULT_DIR/unit/operator/parse_xml_pand.txt"    $flag1 $flag2 $flag3

geodms_instance         "$TST_DIR/Unit/operator/cfg/select_orgrel.dms"                        test_log "$RESULT_DIR/unit/operator/select_orgrel.txt"                         $flag1 $flag2 $flag3
geodms_instance_error_is_ok "$TST_DIR/Unit/operator/cfg/argmax_different_valuetypes.dms"      test_log "$RESULT_DIR/unit/operator/argmax_different_valuetypes.txt"            $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/operator/cfg/select_orgrel.dms"                        test_log "$RESULT_DIR/unit/operator/select_orgrel.txt"                         $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/Operator/cfg/points2sequence.dms"                      test_log "$RESULT_DIR/unit/operator/points2sequence.txt"                       $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/Operator/cfg/reg_count.dms"                            test_log "$RESULT_DIR/unit/operator/reg_count.txt"                             $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/Operator/cfg/reverse.dms"                              test_log "$RESULT_DIR/unit/operator/reverse.txt"                               $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/Operator/cfg/reverse_uint8.dms"                        test_log "$RESULT_DIR/unit/operator/reverse_uint8.txt"                         $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/Operator/cfg/centroid_or_mid_complex.dms"              test_log "$RESULT_DIR/unit/operator/centroid_or_mid_complex.txt"               $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/Operator/cfg/subitem_of_unit.dms"                      test_log "$RESULT_DIR/unit/operator/subitem_of_unit.txt"                       $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/Operator/cfg/subset.dms"                               test_log "$RESULT_DIR/unit/operator/subset.txt"                                $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/Operator/cfg/merge_indirect_domainunit.dms"            test_log "$RESULT_DIR/unit/operator/merge_indirect_domainunit.txt"             $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/Operator/cfg/ReadElems_flag1.dms"                      test_log "$RESULT_DIR/unit/operator/ReadElems_flag1.txt"                       $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/Operator/cfg/ReadElems_flag24.dms"                     test_log "$RESULT_DIR/unit/operator/ReadElems_flag24.txt"                      $flag1 $flag2 $flag3
geodms_instance         "$TST_DIR/Unit/Operator/cfg/true_function_in_select_by_cond.dms"      test_log "$RESULT_DIR/unit/operator/select_with_attr_by_cond_true_function.txt" $flag1 $flag2 $flag3

sleep 2
geodms_instance "$TST_DIR/Operator/cfg/operator.dms" "results/unit_test_log" "$RESULT_DIR/unit/operator/operator.txt" $flag1 $flag2 $flag3

# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------
geodms_instance_error_is_ok "$TST_DIR/Unit/unit/cfg/categorical_unit.dms" "src/b" "$RESULT_DIR/unit/unit/categorical_unit.txt" $flag1 $flag2 $flag3
geodms_instance_error_is_ok "$TST_DIR/Unit/unit/cfg/categorical_unit.dms" "src/C" "$RESULT_DIR/unit/unit/categorical_unit.txt" $flag1 $flag2 $flag3
geodms_instance_error_is_ok "$TST_DIR/Unit/unit/cfg/categorical_unit.dms" "sub/D" "$RESULT_DIR/unit/unit/categorical_unit.txt" $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/unit/cfg/categorical_unit.dms" test_log "$RESULT_DIR/unit/unit/categorical_unit.txt" $flag1 $flag2 $flag3

# ---------------------------------------------------------------------------
# Storage read
# ---------------------------------------------------------------------------
export GEODMS_DIRECTORIES_LOCALDATAPROJDIR="$LOCAL_DATA_DIR_REGRESSION/storage"
geodms_instance "$TST_DIR/storage/cfg/regression.dms"           "results/unit_test_log"      "$RESULT_DIR/unit/storage/read_geodms_formats.txt"      $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/storage_gdal/cfg/regression.dms"      "results/unit_test_vect_read_log" "$RESULT_DIR/unit/storage/read_gdal_vect_formats.txt" $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/storage/cfg/tiff_configured_domain.dms" test_log              "$RESULT_DIR/unit/storage/read_tiff_configured_domain_error.txt" $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/storage_gdal/cfg/regression.dms"      "results/unit_test_grid_read_log" "$RESULT_DIR/unit/storage/read_gdal_grid_formats.txt" $flag1 $flag2 $flag3
geodms_instance_error_is_ok "$TST_DIR/Unit/storage/cfg/src_indirect.dms" test_log            "$RESULT_DIR/unit/storage/src_indirect_check_file.txt"  $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/storage/cfg/src_indirect.dms"    test_log_file_is_written      "$RESULT_DIR/unit/storage/src_indirect.txt"             $flag1 $flag2 $flag3

# ---------------------------------------------------------------------------
# Storage write (two-step: export then verify)
# ---------------------------------------------------------------------------
geodms_instance "$TST_DIR/Unit/Storage/cfg/write_dbf.dms"           export   "$RESULT_DIR/unit/storage/WriteDbf.txt"       $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/Storage/cfg/write_dbf.dms"           test_log "$RESULT_DIR/unit/storage/WriteDbf.txt"       $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/Storage/cfg/Write_tiff_pal.dms"      export   "$RESULT_DIR/unit/storage/WriteTiff_pal.txt"  $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/Storage/cfg/Write_tiff_pal.dms"      test_log "$RESULT_DIR/unit/storage/WriteTiff_pal.txt"  $flag1 $flag2 $flag3

geodms_instance "$TST_DIR/Unit/Storage/cfg/write_gdal_csv.dms"      export     "$RESULT_DIR/unit/storage/Write_gdal_csv.txt" $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/Storage/cfg/write_gdal_csv.dms"      export_all "$RESULT_DIR/unit/storage/Write_gdal_csv.txt" $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/Storage/cfg/write_gdal_csv.dms"      test_log   "$RESULT_DIR/unit/storage/Write_gdal_csv.txt" $flag1 $flag2 $flag3

geodms_instance "$TST_DIR/Unit/Storage/cfg/Write_NL_tiff_gdal_grid.dms" export   "$RESULT_DIR/unit/storage/WriteNLTiff_gdal.txt" $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/Storage/cfg/Write_NL_tiff_gdal_grid.dms" test_log "$RESULT_DIR/unit/storage/WriteNLTiff_gdal.txt" $flag1 $flag2 $flag3

geodms_instance "$TST_DIR/Unit/Storage/cfg/fss_one_record.dms"   write_data "$RESULT_DIR/unit/storage/fss_one_record.txt"  $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/Storage/cfg/fss_one_record.dms"   test_log   "$RESULT_DIR/unit/storage/fss_one_record.txt"  $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/Storage/cfg/fss_zero_records.dms" write_data "$RESULT_DIR/unit/storage/fss_zero_record.txt" $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/Storage/cfg/fss_zero_records.dms" test_log   "$RESULT_DIR/unit/storage/fss_zero_record.txt" $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/Storage/cfg/csv_with_euro.dms"    test_log   "$RESULT_DIR/unit/storage/csv_with_euro.txt"   $flag1 $flag2 $flag3

# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------
geodms_instance "$TST_DIR/Unit/Template/cfg/read_full.dms" test_log "$RESULT_DIR/unit/Template/ReadFullTemplate.txt" $flag1 $flag2 $flag3

# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------
geodms_instance "$TST_DIR/Unit/grid/cfg/spoint_nrElements.dms"        test_log         "$RESULT_DIR/unit/grid/spoint_nrElements.txt"          $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/grid/cfg/spoint_ZeroElements.dms"      test_log         "$RESULT_DIR/unit/grid/spoint_ZeroElements.txt"         $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/grid/cfg/spoint_ZeroElements.dms"      test_log_to_tiff "$RESULT_DIR/unit/grid/spoint_ZeroElementsToTiff.txt"   $flag1 $flag2 $flag3

# ---------------------------------------------------------------------------
# CRS
# ---------------------------------------------------------------------------
geodms_instance "$TST_DIR/Unit/CRS/cfg/reproject.dms" test_log "$RESULT_DIR/unit/crs/reproject.txt" $flag1 $flag2 $flag3

# ---------------------------------------------------------------------------
# Other
# ---------------------------------------------------------------------------
geodms_instance             "$TST_DIR/Unit/other/cfg/DoubleInstantiation.dms"                   test_log "$RESULT_DIR/unit/other/DoubleInstantiation.txt"                  $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/DoubleInheritance.dms"                     test_log "$RESULT_DIR/unit/other/DoubleInheritance.txt"                    $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/ComplexNamespaces.dms"                     test_log "$RESULT_DIR/unit/other/ComplexNamespaces.txt"                    $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/Kentallen.dms"                             test_log "$RESULT_DIR/unit/other/Kentallen.txt"                            $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/Overrule.dms"                              test_log "$RESULT_DIR/unit/other/Overrule.txt"                             $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/CombineRangeAndExprTest.dms"               test_log "$RESULT_DIR/unit/other/CombineRangeAndExprTest.txt"              $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/TemplateInstAsArg.dms"                     test_log "$RESULT_DIR/unit/other/TemplateInstAsArg.txt"                    $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/InstantiateDataBlock.dms"                  test_log "$RESULT_DIR/unit/other/InstantiateDataBlock.txt"                 $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/GridFromTemplate.dms"                      test_log "$RESULT_DIR/unit/other/GridFromTemplate.txt"                     $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/Namespaces/cfg/TemplDefinition.dms"                  test_log "$RESULT_DIR/unit/Namespaces/TemplDefinition.txt"                 $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/CombineDefinedRange.dms"                   test_log "$RESULT_DIR/unit/other/CombineDefinedRange.txt"                  $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/select_with_attr_by_org_rel_nested.dms"    test_log "$RESULT_DIR/unit/other/select_with_attr_by_org_rel_nested.txt"   $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/propvalue_inherited_no_subitems.dms"       test_log "$RESULT_DIR/unit/other/propvalue_inherited_no_subitems.txt"       $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/other/cfg/CloseGUIIssue1.dms"                        test_log "$RESULT_DIR/unit/other/CloseGUIIssue1.txt"                       $flag1 $flag2 $flag3
geodms_instance_error_is_ok "$TST_DIR/Unit/other/cfg/item_names_equal.dms"                      test_log "$RESULT_DIR/unit/other/item_names_equal.txt"                     $flag1 $flag2 $flag3
geodms_instance_error_is_ok "$TST_DIR/Unit/other/cfg/issue_327_IndirectNullCalcRule.dms"        test_log "$RESULT_DIR/unit/other/issue_327_IndirectNullCalcRule.txt"        $flag1 $flag2 $flag3
geodms_instance_error_is_ok "$TST_DIR/Unit/other/cfg/unbalanced_placeholder_crash.dms"          test_log "$RESULT_DIR/unit/other/unbalanced_placeholder_crash.txt"          $flag1 $flag2 $flag3

# ---------------------------------------------------------------------------
# Integrity checks
# ---------------------------------------------------------------------------
geodms_instance             "$TST_DIR/Unit/Integrity_check/cfg/this.dms"                        test_log "$RESULT_DIR/unit/integrity_check/this.txt"                       $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/Integrity_check/cfg/container.dms"                   test_log "$RESULT_DIR/unit/integrity_check/container.txt"                  $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/Integrity_check/cfg/primary_key_unique.dms"          test_log "$RESULT_DIR/unit/integrity_check/primary_key_unique.txt"          $flag1 $flag2 $flag3
geodms_instance_error_is_ok "$TST_DIR/Unit/Integrity_check/cfg/primary_key_not_unique.dms"      test_log "$RESULT_DIR/unit/integrity_check/primary_key_not_unique.txt"      $flag1 $flag2 $flag3

geodms_instance             "$TST_DIR/Unit/Integrity_check/cfg/must_write.dms"                  export   "$RESULT_DIR/unit/integrity_check/must_write.txt"                 $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/Integrity_check/cfg/must_write.dms"                  test_log "$RESULT_DIR/unit/integrity_check/must_write.txt"                 $flag1 $flag2 $flag3
geodms_instance_error_is_ok "$TST_DIR/Unit/Integrity_check/cfg/must_not_write.dms"              export   "$RESULT_DIR/unit/integrity_check/must_not_write.txt"             $flag1 $flag2 $flag3
geodms_instance             "$TST_DIR/Unit/Integrity_check/cfg/must_not_write.dms"              test_log "$RESULT_DIR/unit/integrity_check/must_not_write.txt"             $flag1 $flag2 $flag3
geodms_instance_error_is_ok "$TST_DIR/Unit/Integrity_check/cfg/CompareFloat64WithInteger.dms"   test_log "$RESULT_DIR/unit/Integrity_check/CompareFloat64WithInteger.txt"   $flag1 $flag2 $flag3

# ---------------------------------------------------------------------------
# WriteStorageIndirect
# ---------------------------------------------------------------------------
geodms_instance "$TST_DIR/Unit/other/cfg/WriteStorageIndirect.dms" export   "$RESULT_DIR/unit/other/WriteStorageIndirect.txt"  $flag1 $flag2 $flag3
geodms_instance "$TST_DIR/Unit/other/cfg/WriteStorageIndirect.dms" test_log "$RESULT_DIR/unit/other/CloseGUIIssue1.txt"        $flag1 $flag2 $flag3

# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
geodms_statistics

# ---------------------------------------------------------------------------
# Final result
# ---------------------------------------------------------------------------
TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
FINAL_NAME="${config}_${REGR_RESULT}_${TIMESTAMP}.txt"
mv "$RESULT_FILENAME" "$RESULT_DIR/unit/$FINAL_NAME"

echo ""
echo "************************"
echo "Unit Test: $REGR_RESULT"
echo "Log: $RESULT_DIR/unit/$FINAL_NAME"
echo "************************"
echo ""

[[ "$REGR_RESULT" == "OK" ]]
