Echo off
CLS

set version=%1
if (%2)==() ( Echo off ) else ( Echo %2 )
if (%1)==() ( Echo Usage: UNIT.BAT ^[D32^|R32^|D64^|R64^|^<versionNr^>]
			  GoTo End)

REM SECTION SET RELEVANT DIRS
Call generic\SetLocalDataDir.bat
Set ResultDir=%LocalDataDir%\GeoDMSTestResults
Set ResultFileName=%ResultDir%\unit\result.txt
Call generic\SetGeoDMSPlatform.bat %version%

Set GeoDmsRunCmdBase="%GeoDmsRunPath%" 

set BatchDir=%CD%
cd ..
set TstDir=%CD%
cd %BatchDir%

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
del %ResultDir%\unit\operator\*.txt 2>nul
del %ResultDir%\unit\storage\*.txt 2>nul
del %ResultDir%\unit\storage\*.dbf 2>nul
del %ResultDir%\unit\storage\*.tif 2>nul
del %ResultDir%\unit\storage\*.tfw 2>nul
del %ResultDir%\unit\storage\OneRecord.fss\*.dmsdata 2>nul
del %ResultDir%\unit\storage\OneRecord.fss\*.fss 2>nul
del %ResultDir%\unit\storage\ZeroRecord.fss\*.dmsdata 2>nul
del %ResultDir%\unit\storage\ZeroRecord.fss\*.fss 2>nul

pause

del %ResultDir%\unit\integrity_check\*.txt 2>nul
del %ResultDir%\unit\Namespaces\*.txt 2>nul
del %ResultDir%\unit\other\*.txt 2>nul

del %ResultFileName% 2>nul

rem pause

Echo Unit Test Results (specific operators, all operators, storage read, other) for: %GeoDmsRunCmdBase% >> %ResultFileName%
Echo.>> %ResultFileName%

REM SECTION OPERATOR 
Call Unit\Instance.bat %TstDir%\Unit\operator\cfg\subitem.dms   test_log %ResultDir%\unit\operator\subitem.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\operator\cfg\connect.dms   test_log %ResultDir%\unit\operator\connect_point_arc.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\operator\cfg\xml_parse.dms test_log %ResultDir%\unit\operator\parse_xml_pand.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\operator\cfg\select_orgrel.dms test_log %ResultDir%\unit\operator\select_orgrel.txt S1 S2
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\operator\cfg\argmax_different_valuetypes.dms test_log %ResultDir%\unit\operator\argmax_different_valuetypes.txt  S1 S2
Call Unit\Instance.bat %TstDir%\Unit\operator\cfg\select_orgrel.dms test_log %ResultDir%\unit\operator\select_orgrel.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\points2sequence.dms test_log %ResultDir%\unit\operator\points2sequence.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\reg_count.dms test_log %ResultDir%\unit\operator\reg_count.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\reverse.dms test_log %ResultDir%\unit\operator\reverse.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\reverse_uint8.dms test_log %ResultDir%\unit\operator\reverse_uint8.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\centroid_or_mid_complex.dms test_log %ResultDir%\unit\operator\centroid_or_mid_complex.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\subitem_of_unit.dms test_log %ResultDir%\unit\operator\subitem_of_unit.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\subset.dms test_log %ResultDir%\unit\operator\subset.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\merge_indirect_domainunit.dms test_log %ResultDir%\unit\operator\merge_indirect_domainunit.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\ReadElems_flag1.dms test_log %ResultDir%\unit\operator\ReadElems_flag1.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Operator\cfg\ReadElems_flag24.dms test_log %ResultDir%\unit\operator\ReadElems_flag24.txt S1 S2

Call Unit\Instance.bat %TstDir%\Operator\cfg\operator.dms results/unit_test_log %ResultDir%\unit\operator\operator.txt S1 S2

REM SECTION STORAGE READ
Call Unit\Instance.bat %TstDir%\storage\cfg\regression.dms results/unit_test_log                %ResultDir%\unit\storage\read_geodms_formats.txt S1 S2
Call Unit\instance.bat %TstDir%\storage_gdal\cfg\regression.dms results/unit_test_vect_read_log %ResultDir%\unit\storage\read_gdal_vect_formats.txt S1 S2
Call Unit\instance.bat %TstDir%\storage_gdal\cfg\regression.dms results/unit_test_grid_read_log %ResultDir%\unit\storage\read_gdal_grid_formats.txt S1 S2
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\storage\cfg\src_indirect.dms test_log             %ResultDir%\unit\storage\src_indirect_check_file.txt S1 S2
Call Unit\instance.bat %TstDir%\Unit\storage\cfg\src_indirect.dms test_log_file_is_written      %ResultDir%\unit\storage\src_indirect.txt S1 S2


REM SECTION STORAGE WRITE IN TWO STEPS, FIRST EXPORT RESULTS, SECOND READ EXPORTED RESULTS
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\write_dbf.dms export %ResultDir%\unit\storage\WriteDbf.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\write_dbf.dms test_log %ResultDir%\unit\storage\WriteDbf.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\Write_tiff_pal.dms export %ResultDir%\unit\storage\WriteTiff_pal.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\Write_tiff_pal.dms test_log %ResultDir%\unit\storage\WriteTiff_pal.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\fss_one_record.dms write_data %ResultDir%\unit\storage\fss_one_record.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\fss_one_record.dms test_log %ResultDir%\unit\storage\fss_one_record.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\fss_zero_records.dms write_data %ResultDir%\unit\storage\fss_zero_record.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Storage\cfg\fss_zero_records.dms test_log %ResultDir%\unit\storage\fss_zero_record.txt S1 S2



REM SECTION GRID 
Call Unit\Instance.bat %TstDir%\Unit\grid\cfg\spoint_nrElements.dms test_log %ResultDir%\unit\grid\spoint_nrElements.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\grid\cfg\spoint_ZeroElements.dms test_log %ResultDir%\unit\grid\spoint_ZeroElements.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\grid\cfg\spoint_ZeroElements.dms test_log_to_tiff %ResultDir%\unit\grid\spoint_ZeroElementsToTiff.txt S1 S2

REM SECTION CRS 
Call Unit\Instance.bat %TstDir%\Unit\CRS\cfg\reproject.dms test_log %ResultDir%\unit\crs\reproject.txt S1 S2

REM SECTION OTHER 
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\DoubleInstantiation.dms test_log %ResultDir%\unit\other\DoubleInstantiation.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\DoubleInheritance.dms test_log %ResultDir%\unit\other\DoubleInheritance.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\ComplexNamespaces.dms test_log %ResultDir%\unit\other\ComplexNamespaces.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\Kentallen.dms test_log %ResultDir%\unit\other\Kentallen.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\Overrule.dms test_log %ResultDir%\unit\other\Overrule.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\CombineRangeAndExprTest.dms test_log %ResultDir%\unit\other\CombineRangeAndExprTest.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\TemplateInstAsArg.dms test_log %ResultDir%\unit\other\TemplateInstAsArg.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\InstantiateDataBlock.dms test_log %ResultDir%\unit\other\InstantiateDataBlock.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\GridFromTemplate.dms test_log %ResultDir%\unit\other\GridFromTemplate.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Namespaces\cfg\TemplDefinition.dms test_log %ResultDir%\unit\Namespaces\TemplDefinition.txt S1 S2

Call Unit\Instance.bat %TstDir%\Unit\other\cfg\CloseGUIIssue1.dms test_log %ResultDir%\unit\other\CloseGUIIssue1.txt S1 S2

REM SECTION INTEGRITY CHECKS
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\this.dms test_log %ResultDir%\unit\integrity_check\this.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\container.dms test_log %ResultDir%\unit\integrity_check\container.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\primary_key_unique.dms test_log %ResultDir%\unit\integrity_check\primary_key_unique.txt S1 S2
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\Integrity_check\cfg\primary_key_not_unique.dms test_log %ResultDir%\unit\integrity_check\primary_key_not_unique.txt S1 S2

REM Integrity Check Section for writing results that should or should not be written, in two steps, first to write and second to read the resulting data
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\must_write.dms export %ResultDir%\unit\integrity_check\must_write.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\must_write.dms test_log %ResultDir%\unit\integrity_check\must_write.txt S1 S2
Call Unit\InstanceErrorIsOk.bat %TstDir%\Unit\Integrity_check\cfg\must_not_write.dms export %ResultDir%\unit\integrity_check\must_not_write.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\Integrity_check\cfg\must_not_write.dms test_log %ResultDir%\unit\integrity_check\must_not_write.txt S1 S2


REM WriteStorageIndirect in two steps, first export results, second read exported results
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\WriteStorageIndirect.dms export %ResultDir%\unit\other\WriteStorageIndirect.txt S1 S2
Call Unit\Instance.bat %TstDir%\Unit\other\cfg\WriteStorageIndirect.dms test_log %ResultDir%\unit\other\CloseGUIIssue1.txt S1 S2


REM SECTION MAKE FINAL RESULT FILE AND PRESENT IN NOTEPAD ++
Set Sequence=%date:/=-%_%time::=-%
SET ResultFileFinalName=v%1_%Sequence%.txt
RENAME "%ResultFileName%" "%ResultFileFinalName%"

CALL "%ProgramFiles%\Notepad++\Notepad++.exe"  "%ResultDir%\unit\%ResultFileFinalName%"
