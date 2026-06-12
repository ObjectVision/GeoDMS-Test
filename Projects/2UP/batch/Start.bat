Call path/set.bat

"%exe_path%" /L"%log_dir%\Start_Pop.txt"                       "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/tpop
"%exe_path%" /L"%log_dir%\Start_Pop_Classification.txt"        "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/Generic/gtopo/tpop_classification
"%exe_path%" /L"%log_dir%\Start_UrbanPop.txt"                  "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/Generic/gtopo/UPop
"%exe_path%" /L"%log_dir%\Start_RuralPop.txt"                  "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/Generic/gtopo/RPop
"%exe_path%" /L"%log_dir%\Start_IsUrban.txt"                   "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/Generic/gtopo/IsUrban
"%exe_path%" /L"%log_dir%\Start_IsUrban_Classification.txt"    "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/Generic/gtopo/IsUrbanClassification
"%exe_path%" /L"%log_dir%\Start_UrbCountry.txt"                "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/Generic/gtopo/UrbCountry
"%exe_path%" /L"%log_dir%\Start_UrbCountryTable.txt"           "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/UrbCountryCombine/export_UrbCountryTable_csv/Result
"%exe_path%" /L"%log_dir%\Start_Builtuparea.txt"               "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/Generic/gtopo/bua_fraction
"%exe_path%" /L"%log_dir%\Start_Builtupareakm2.txt"            "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/Generic/gtopo/buakm2
"%exe_path%" /L"%log_dir%\Start_PopDensity.txt"                "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/Generic/gtopo/popd
"%exe_path%" /L"%log_dir%\Start_PopDensity_Classification.txt" "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/Generic/gtopo/popd_classification
"%exe_path%" /L"%log_dir%\Start_SMOD.txt"                      "%prj_dir%\cfg\stam.dms" /Scenarios/SSPs/SSP1/Export/Start/Generic/gtopo/SMOD


