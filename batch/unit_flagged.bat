Echo off
CLS

set version=%1
set flag1=%2
set flag2=%3
set flag3=%4

if (%2)==() ( Echo off ) else ( Echo %2 )
if (%1)==() ( Echo Usage: UNIT.BAT ^[D32^|R32^|D64^|R64^|^<versionNr^>]
			  GoTo End)
IF (%flag1%) ==() ( set flag1=S1 )
IF (%flag2%) ==() ( set flag2=S2 )
IF (%flag3%) ==() ( set flag3=S3 )

REM SECTION SET RELEVANT DIRS
Call generic\SetLocalDataDir.bat
Set ResultDir=%LocalDataDir%\GeoDMSTestResults
Set ResultFileName=%ResultDir%\unit\result.txt
Call generic\SetGeoDMSPlatform.bat %version%

Set GeoDmsRunCmdBase="%GeoDmsRunPath%" 
Set GeoDmsQtCmdBase="%GeoDmsGuiQtPath%" 

set BatchDir=%CD%
cd ..
set TstDir=%CD%
cd "%BatchDir%"

REM SECTION LOGGING
Echo.
Echo ************************
Echo Starting the UNIT test for: %GeoDmsRunCmdBase%
Echo ************************
Echo.
Echo TstDir: %TstDir%
Echo ResultDir: %ResultDir%
Echo.

REM REMOVE OLD RESULTS
del "%ResultDir%\unit\operator\*.txt 2>nul"
del "%ResultDir%\unit\storage\*.txt 2>nul"
del "%ResultDir%\unit\storage\*.dbf 2>nul"
del "%ResultDir%\unit\storage\*.tif 2>nul"
del "%ResultDir%\unit\storage\*.tfw 2>nul"
del "%ResultDir%\unit\storage\OneRecord.fss\*.dmsdata" 2>nul
del "%ResultDir%\unit\storage\OneRecord.fss\*.fss" 2>nul
del "%ResultDir%\unit\storage\ZeroRecord.fss\*.dmsdata" 2>nul
del "%ResultDir%\unit\storage\ZeroRecord.fss\*.fss" 2>nul
del "%ResultDir%\unit\GUI\*.txt" 2>nul
del "%ResultDir%\unit\integrity_check\*.txt" 2>nul
del "%ResultDir%\unit\Namespaces\*.txt" 2>nul
del "%ResultDir%\unit\other\*.txt" 2>nul

del "%ResultFileName%" 2>nul

rem pause

Echo Unit Test Results (specific operators, all operators, storage read, other) for: %GeoDmsRunCmdBase% >> %ResultFileName%
Echo.>> "%ResultFileName%"

REM SECTION GUI 
Call Unit\GUIInstance.bat "%TstDir%\dmsscript\MapViewClassification.dmsscript" "%TstDir%\Operator\cfg\MicroTst.dms" "%ResultDir%\unit\gui\MicroTst_error.txt" %flag1% %flag2% %flag3%

Call ..\Unit\GUI\bat\DPGeneral_explicit_supplier_error.bat
Call Unit\Instance.bat "%TstDir%\Unit\GUI\cfg\DPGeneral_explicit_supplier_error.dms" test_log "%ResultDir%\unit\gui\DPGeneral_ES_error.txt" %flag1% %flag2% %flag3%

Call ..\Unit\GUI\bat\DPGeneral_missing_file_error.bat
Call Unit\Instance.bat "%TstDir%\Unit\GUI\cfg\DPGeneral_missing_file_error.dms" test_log "%ResultDir%\unit\gui\DPGeneral_MF_error.txt" %flag1% %flag2% %flag3%

Call Unit\Instance.bat "%TstDir%\Unit\GUI\cfg\background_layer.dms" test_log "%ResultDir%\unit\GUI\background_layer_error.txt" %flag1% %flag2% %flag3%

REM SECTION OPERATOR 
Call Unit\Instance.bat "%TstDir%\Unit\operator\cfg\subitem.dms" test_log "%ResultDir%\unit\operator\subitem.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat "%TstDir%\Unit\operator\cfg\connect.dms" test_log "%ResultDir%\unit\operator\connect_point_arc.txt" %flag1% %flag2% %flag3%

timeout /T 2 /NOBREAK
Call Unit\Instance.bat %TstDir%\Unit\operator\cfg\xml_parse.dms test_log "%ResultDir%\unit\operator\parse_xml_pand.txt" %flag1% %flag2% %flag3%
REM timeout /T 2 /NOBREAK

Call Unit\Instance.bat %TstDir%\Unit\operator\cfg\select_orgrel.dms                        test_log "%ResultDir%\unit\operator\select_orgrel.txt" %flag1% %flag2% %flag3%
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\operator\cfg\argmax_different_valuetypes.dms test_log "%ResultDir%\unit\operator\argmax_different_valuetypes.txt"  %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\operator\cfg\select_orgrel.dms                        test_log "%ResultDir%\unit\operator\select_orgrel.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\points2sequence.dms                      test_log "%ResultDir%\unit\operator\points2sequence.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\reg_count.dms                            test_log "%ResultDir%\unit\operator\reg_count.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\reverse.dms                              test_log "%ResultDir%\unit\operator\reverse.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\reverse_uint8.dms                        test_log "%ResultDir%\unit\operator\reverse_uint8.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\centroid_or_mid_complex.dms              test_log "%ResultDir%\unit\operator\centroid_or_mid_complex.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\subitem_of_unit.dms                      test_log "%ResultDir%\unit\operator\subitem_of_unit.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\subset.dms                               test_log "%ResultDir%\unit\operator\subset.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\merge_indirect_domainunit.dms            test_log "%ResultDir%\unit\operator\merge_indirect_domainunit.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\ReadElems_flag1.dms                      test_log "%ResultDir%\unit\operator\ReadElems_flag1.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\ReadElems_flag24.dms                     test_log "%ResultDir%\unit\operator\ReadElems_flag24.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\true_function_in_select_by_cond.dms      test_log "%ResultDir%\unit\operator\select_with_attr_by_cond_true_function.txt" %flag1% %flag2% %flag3%

timeout /T 2 /NOBREAK
Call Unit\Instance.bat %TstDir%\Operator\cfg\operator.dms results/unit_test_log "%ResultDir%\unit\operator\operator.txt" %flag1% %flag2% %flag3%
REM timeout /T 2 /NOBREAK

REM SECTION UNITS // ACTIVATE AFTER SOLVING ISSUE 199
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\unit\cfg\categorical_unit.dms src/b    "%ResultDir%\unit\unit\categorical_unit.txt" %flag1% %flag2% %flag3%
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\unit\cfg\categorical_unit.dms src/C    "%ResultDir%\unit\unit\categorical_unit.txt" %flag1% %flag2% %flag3%
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\unit\cfg\categorical_unit.dms sub/D    "%ResultDir%\unit\unit\categorical_unit.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat          %TstDir%\Unit\unit\cfg\categorical_unit.dms test_log "%ResultDir%\unit\unit\categorical_unit.txt" %flag1% %flag2% %flag3%

REM SECTION STORAGE READ
Call Unit\Instance.bat %TstDir%\storage\cfg\regression.dms results/unit_test_log                "%ResultDir%\unit\storage\read_geodms_formats.txt" %flag1% %flag2% %flag3%
Call Unit\instance.bat %TstDir%\storage_gdal\cfg\regression.dms results/unit_test_vect_read_log "%ResultDir%\unit\storage\read_gdal_vect_formats.txt" %flag1% %flag2% %flag3%
Call Unit\instance.bat %TstDir%\Unit\storage\cfg\tiff_configured_domain.dms test_log            "%ResultDir%\unit\storage\read_tiff_configured_domain_error.txt" %flag1% %flag2% %flag3%
Call Unit\instance.bat %TstDir%\storage_gdal\cfg\regression.dms results/unit_test_grid_read_log "%ResultDir%\unit\storage\read_gdal_grid_formats.txt" %flag1% %flag2% %flag3%
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\storage\cfg\src_indirect.dms test_log             "%ResultDir%\unit\storage\src_indirect_check_file.txt" %flag1% %flag2% %flag3%
Call Unit\instance.bat %TstDir%\Unit\storage\cfg\src_indirect.dms test_log_file_is_written      "%ResultDir%\unit\storage\src_indirect.txt" %flag1% %flag2% %flag3%

REM SECTION STORAGE WRITE IN TWO STEPS, FIRST EXPORT RESULTS, SECOND READ EXPORTED RESULTS
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\write_dbf.dms      export   "%ResultDir%\unit\storage\WriteDbf.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\write_dbf.dms      test_log "%ResultDir%\unit\storage\WriteDbf.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\Write_tiff_pal.dms export   "%ResultDir%\unit\storage\WriteTiff_pal.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\Write_tiff_pal.dms test_log "%ResultDir%\unit\storage\WriteTiff_pal.txt" %flag1% %flag2% %flag3%

Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\write_gdal_csv.dms export "%ResultDir%\unit\storage\Write_gdal_csv.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\write_gdal_csv.dms export_all "%ResultDir%\unit\storage\Write_gdal_csv.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\write_gdal_csv.dms test_log "%ResultDir%\unit\storage\Write_gdal_csv.txt" %flag1% %flag2% %flag3%

Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\Write_NL_tiff_gdal_grid.dms export "%ResultDir%\unit\storage\WriteNLTiff_gdal.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\Write_NL_tiff_gdal_grid.dms test_log "%ResultDir%\unit\storage\WriteNLTiff_gdal.txt" %flag1% %flag2% %flag3%

Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\fss_one_record.dms write_data "%ResultDir%\unit\storage\fss_one_record.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\fss_one_record.dms test_log "%ResultDir%\unit\storage\fss_one_record.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\fss_zero_records.dms write_data "%ResultDir%\unit\storage\fss_zero_record.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\fss_zero_records.dms test_log "%ResultDir%\unit\storage\fss_zero_record.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\csv_with_euro.dms test_log "%ResultDir%\unit\storage\csv_with_euro.txt" %flag1% %flag2% %flag3%

REM SECTION TEMPLATE 
Call Unit\Instance.bat %TstDir%\Unit\Template\cfg\read_full.dms test_log "%ResultDir%\unit\Template\ReadFullTemplate.txt" %flag1% %flag2% %flag3%

REM SECTION GRID 
Call Unit\Instance.bat %TstDir%\Unit\grid\cfg\spoint_nrElements.dms test_log "%ResultDir%\unit\grid\spoint_nrElements.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\grid\cfg\spoint_ZeroElements.dms test_log "%ResultDir%\unit\grid\spoint_ZeroElements.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\grid\cfg\spoint_ZeroElements.dms test_log_to_tiff "%ResultDir%\unit\grid\spoint_ZeroElementsToTiff.txt" %flag1% %flag2% %flag3%

REM SECTION CRS 
Call Unit\Instance.bat %TstDir%\Unit\CRS\cfg\reproject.dms test_log "%ResultDir%\unit\crs\reproject.txt" %flag1% %flag2% %flag3%

REM SECTION OTHER 
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\DoubleInstantiation.dms test_log "%ResultDir%\unit\other\DoubleInstantiation.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\DoubleInheritance.dms test_log "%ResultDir%\unit\other\DoubleInheritance.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\ComplexNamespaces.dms test_log "%ResultDir%\unit\other\ComplexNamespaces.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\Kentallen.dms test_log "%ResultDir%\unit\other\Kentallen.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\Overrule.dms test_log "%ResultDir%\unit\other\Overrule.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\CombineRangeAndExprTest.dms test_log "%ResultDir%\unit\other\CombineRangeAndExprTest.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\TemplateInstAsArg.dms test_log "%ResultDir%\unit\other\TemplateInstAsArg.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\InstantiateDataBlock.dms test_log "%ResultDir%\unit\other\InstantiateDataBlock.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\GridFromTemplate.dms test_log "%ResultDir%\unit\other\GridFromTemplate.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Namespaces\cfg\TemplDefinition.dms test_log "%ResultDir%\unit\Namespaces\TemplDefinition.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\CombineDefinedRange.dms test_log "%ResultDir%\unit\other\CombineDefinedRange.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\select_with_attr_by_org_rel_nested.dms test_log "%ResultDir%\unit\other\select_with_attr_by_org_rel_nested.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\propvalue_inherited_no_subitems.dms test_log "%ResultDir%\unit\other\propvalue_inherited_no_subitems.txt" %flag1% %flag2% %flag3%

Call Unit\Instance.bat %TstDir%\Unit\other\cfg\CloseGUIIssue1.dms test_log "%ResultDir%\unit\other\CloseGUIIssue1.txt" %flag1% %flag2% %flag3%
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\other\cfg\item_names_equal.dms test_log "%ResultDir%\unit\other\item_names_equal.txt" %flag1% %flag2% %flag3%
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\other\cfg\issue_327_IndirectNullCalcRule.dms test_log "%ResultDir%\unit\other\issue_327_IndirectNullCalcRule.txt" %flag1% %flag2% %flag3%

Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\other\cfg\unbalanced_placeholder_crash.dms test_log "%ResultDir%\unit\other\unbalanced_placeholder_crash.txt" %flag1% %flag2% %flag3%

REM SECTION INTEGRITY CHECKS
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\this.dms test_log "%ResultDir%\unit\integrity_check\this.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\container.dms test_log "%ResultDir%\unit\integrity_check\container.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\primary_key_unique.dms test_log "%ResultDir%\unit\integrity_check\primary_key_unique.txt" %flag1% %flag2% %flag3%
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\Integrity_check\cfg\primary_key_not_unique.dms test_log "%ResultDir%\unit\integrity_check\primary_key_not_unique.txt" %flag1% %flag2% %flag3%

REM SECTION Integrity Check for writing results that should or should not be written, in two steps, first to write and second to read the resulting data
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\must_write.dms export "%ResultDir%\unit\integrity_check\must_write.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\must_write.dms test_log "%ResultDir%\unit\integrity_check\must_write.txt" %flag1% %flag2% %flag3%
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\Integrity_check\cfg\must_not_write.dms export "%ResultDir%\unit\integrity_check\must_not_write.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\must_not_write.dms test_log "%ResultDir%\unit\integrity_check\must_not_write.txt" %flag1% %flag2% %flag3%
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\Integrity_check\cfg\CompareFloat64WithInteger.dms test_log "%ResultDir%\unit\Integrity_check\CompareFloat64WithInteger.txt" %flag1% %flag2% %flag3%

REM SECTION WriteStorageIndirect in two steps, first export results, second read exported results
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\WriteStorageIndirect.dms export "%ResultDir%\unit\other\WriteStorageIndirect.txt" %flag1% %flag2% %flag3%
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\WriteStorageIndirect.dms test_log "%ResultDir%\unit\other\CloseGUIIssue1.txt" %flag1% %flag2% %flag3%

REM SECTION STATISTICS
Call Unit\Statistics.bat

REM IF %ERRORLEVEL% NEQ 0 Echo "%GeoDmsGuiQtPath%" FAILED >> %ResultFileName%

REM SECTION MAKE FINAL RESULT FILE AND PRESENT IN NOTEPAD ++
Set Sequence=%date:/=-%_%time::=-%
SET ResultFileFinalName=v%1_%Sequence%.txt
RENAME "%ResultFileName%" "%ResultFileFinalName%"

START "" "%ProgramFiles%\Notepad++\Notepad++.exe"  "%ResultDir%\unit\%ResultFileFinalName%"
