from cbs_api_requests import CbsLocationData as cbs

# Call get cbs location data from class
cbs.get_cbs_location_data("gemeente", [2022,2023])

# Call cbs map function from class
cbs.map_cbs_location(workbookname="dataset-zwerfinator-incl-sleutels.xlsx", sheetname="Data", cbs_type="gemeente", cbs_year=2023)
