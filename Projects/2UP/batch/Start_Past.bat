Call path/set.bat

"%exe_path%" /L"%log_dir%\Start_Past_Pop.txt"                       "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/tpop
"%exe_path%" /L"%log_dir%\Start_Past_Pop_Classification.txt"        "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/Generic/gtopo/tpop_classification
"%exe_path%" /L"%log_dir%\Start_Past_UrbanPop.txt"                  "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/Generic/gtopo/UPop
"%exe_path%" /L"%log_dir%\Start_Past_RuralPop.txt"                  "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/Generic/gtopo/RPop
"%exe_path%" /L"%log_dir%\Start_Past_IsUrban.txt"                   "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/Generic/gtopo/IsUrban
"%exe_path%" /L"%log_dir%\Start_Past_IsUrban_Classification.txt"    "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/Generic/gtopo/IsUrbanClassification
"%exe_path%" /L"%log_dir%\Start_Past_UrbCountry.txt"                "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/Generic/gtopo/UrbCountry
"%exe_path%" /L"%log_dir%\Start_Past_UrbCountryTable.txt"           "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/UrbCountryCombine/export_UrbCountryTable_csv/Result
"%exe_path%" /L"%log_dir%\Start_Past_Builtuparea.txt"               "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/Generic/gtopo/bua_fraction
"%exe_path%" /L"%log_dir%\Start_Past_Builtupareakm2.txt"            "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/Generic/gtopo/buakm2
"%exe_path%" /L"%log_dir%\Start_Past_PopDensity.txt"                "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/Generic/gtopo/popd
"%exe_path%" /L"%log_dir%\Start_Past_PopDensity_Classification.txt" "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/Generic/gtopo/popd_classification
"%exe_path%" /L"%log_dir%\Start_Past_SMOD.txt"                      "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/Start/Generic/gtopo/SMOD


