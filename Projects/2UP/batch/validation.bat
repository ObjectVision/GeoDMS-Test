Call path/set.bat

"%exe_path%" /L"%log_dir%\Validation_Country.txt" "%prj_dir%\cfg\stam.dms" /Validation/UrbanAccuracy/Country/export_csv/Result
"%exe_path%" /L"%log_dir%\Validation_Continent.txt" "%prj_dir%\cfg\stam.dms" /Validation/UrbanAccuracy/Continent/export_csv/Result
"%exe_path%" /L"%log_dir%\Validation_World.txt" "%prj_dir%\cfg\stam.dms" /Validation/UrbanAccuracy/World/export_csv/Result

"%exe_path%" /L"%log_dir%\Validation_Population_Country.txt" "%prj_dir%\cfg\stam.dms" /Validation/Population_Error_Indicators/Result/export_country_csv/Result
"%exe_path%" /L"%log_dir%\Validation_Population_Continent.txt" "%prj_dir%\cfg\stam.dms" /Validation/Population_Error_Indicators/Result/export_continent_csv/Result
"%exe_path%" /L"%log_dir%\Validation_Population_World.txt" "%prj_dir%\cfg\stam.dms" /Validation/Population_Error_Indicators/Result/export_world_csv/Result

"%exe_path%" /L"%log_dir%\SSPPast_Urb_Observed.txt" "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/ISO3/Urb_Observed_csv/Result
"%exe_path%" /L"%log_dir%\SSPPast_Urban_claim.txt" "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/ISO3/Urban_claim_CSV/Result
"%exe_path%" /L"%log_dir%\SSPPast_Urban_Alloc_km2.txt" "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/ISO3/Urban_Alloc_km2_CSV/Result
"%exe_path%" /L"%log_dir%\SSPPast_Check_ClaimRealisation.txt" "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/ISO3/Check_ClaimRealisation_km2_CSV/Result
"%exe_path%" /L"%log_dir%\SSPPast_PRC_ClaimRealisation.txt" "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/ISO3/PRC_ClaimRealisation_CSV/Result
"%exe_path%" /L"%log_dir%\SSPPast_Report_ClaimRealisation.txt" "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/ISO3/Report_ClaimRealisation_CSV/Result
"%exe_path%" /L"%log_dir%\SSPPast_UrbanCells_Alloc.txt" "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/ISO3/UrbanCells_Alloc_CSV/Result
"%exe_path%" /L"%log_dir%\SSPPast_UrbanShare.txt" "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/ISO3/UrbanShareCSV/Result
"%exe_path%" /L"%log_dir%\SSPPast_UrbanCluster.txt" "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Export/ISO3/UrbanClusterCSV/Result


"%exe_path%" /L"%log_dir%\CombinationUrbNotUrbOccurring_Past.txt" "%prj_dir%\cfg\stam.dms" /Past/SSPs/SSPPast/Analysis_UrbNotUrb_Past/UrbanDif1990_2014_steps/export_csv/Result




