import requests
import pandas as pd
import geopandas as gpd

from shapely.geometry import box


# Initiliazing empty dataframe to store the results
geodata = pd.DataFrame()

"""Making the API request, and clean and prepare response data"""
# Pagination identificators
count = 1000  # Number of rows in request
startindex = 0  # Start rownumber

# Making request and appending results to dataframe
while True:
    geojson_url = f"https://service.pdok.nl/cbs/gebiedsindelingen/2022/wfs/v1_0?request=GetFeature&service=WFS&version=2.0.0&typeName=buurt_gegeneraliseerd&outputFormat=json&count={count}&startIndex={startindex}&srsName=EPSG:4326"

    # Executing request
    response = requests.get(geojson_url)

    # Handling response
    if response.status_code == 200:
        data = response.json()
        features = data.get(
            "features", []
        )  # All geographic information is stored in the features part of JSON response

        # Extract the bbox (geographical coordinates) and other attributes
        bbox_list = [feature["bbox"] for feature in features]
        statcode_list = [feature["properties"]["statcode"] for feature in features]

        # Store data in temporary dataFrame
        statdata = pd.DataFrame({"statcode": statcode_list, "bbox": bbox_list})

        # Append temporary data to geodata dataframe
        geodata = pd.concat([geodata, statdata], ignore_index=True)

        # Check for amount of rows in latest response and break when smaller then amount of rows requested in count
        if len(features) < count:
            break

        # Update the startindex for the next request
        startindex += len(features)
    else:
        # Break when responsecode is not 200
        break

"""Preparing received data and load coordinates from dataset"""

# Adding separate columns for longitude and latitude values in BBOX
geodata[["minx", "miny", "maxx", "maxy"]] = geodata["bbox"].apply(
    lambda x: pd.Series({"minx": x[0], "miny": x[1], "maxx": x[2], "maxy": x[3]})
)

# Create geometry column for GeoPandas
geodata["geometry"] = [
    box(minx, miny, maxx, maxy)
    for minx, miny, maxx, maxy in zip(
        geodata["minx"], geodata["miny"], geodata["maxx"], geodata["maxy"]
    )
]

# Connecting to dataset workbook and extract longitude and latitude values
file_path = r"dataset-zwerfinator-incl-sleutels.xlsx"  # In Power Query I added a paramater manually within the M code string for the filelocation
workbook = pd.read_excel(file_path, sheet_name="Data")
workbook.columns = workbook.columns.str.lower()
workbook = workbook[["latitude", "longitude"]]

workbook.drop_duplicates(subset=["latitude", "longitude"], inplace=True)

# Creating seperate GeoData dataframes for combining the dataset and geodata
workbook_gdf = gpd.GeoDataFrame(
    workbook, geometry=gpd.points_from_xy(workbook["longitude"], workbook["latitude"])
)

geodata_gdf = gpd.GeoDataFrame(geodata)
geodata_gdf.set_geometry("geometry", inplace=True)


# Creating new GeoData Dataframe based on spatial join between geometric point from the dataset and the bbox area coordinates
neighbourhood_statcodes = gpd.sjoin(
    workbook_gdf, geodata_gdf, how="left", predicate="intersects"
)

# Filtering needed columns and removing duplicate values
neighbourhood_statcodes = neighbourhood_statcodes[["latitude", "longitude", "statcode"]]
neighbourhood_statcodes.drop_duplicates(subset=["latitude", "longitude"], inplace=True)

# Converting GeoPandas Dataframe to Pandas dataframe for Power Bi compatibility
neighbourhood_statcodes = pd.DataFrame(neighbourhood_statcodes)

""" Because Power Query applies an automatic rounding when the type decimal is used, I experienced an issue with
    merging on the longitude and latitude values between the output of the script and the dataset. 
    
    To fix this issue I had to round all values are rounded to 13 and 14 decimals in Python and in Power Query on the dataset.
    """

# Performing rounding
neighbourhood_statcodes["latitude"] = round(neighbourhood_statcodes["latitude"], 13)
neighbourhood_statcodes["longitude"] = neighbourhood_statcodes["longitude"].apply(
    lambda x: round(x, 14)
)

# Return dataframe as output
neighbourhood_statcodes
