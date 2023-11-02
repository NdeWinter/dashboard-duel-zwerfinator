import requests
import pandas as pd
import geopandas as gpd

# Initiliazing empty GeoPandas DataFrame to store the response data
geodata = pd.DataFrame()

"""Making the API request, and clean and prepare response data"""

# Setting pagination identificators
count = 1000  # Number of rows in request
startindex = 0  # Start rownumber

# Making request and appending results to dataframe
while True:
    geojson_url = f"https://service.pdok.nl/cbs/gebiedsindelingen/2022/wfs/v1_0?request=GetFeature&service=WFS&version=2.0.0&typeName=wijk_gegeneraliseerd&outputFormat=json&count={count}&startIndex={startindex}&srsName=EPSG:4326"

    # Executing request
    response = requests.get(geojson_url)

    # Handling response
    if response.status_code == 200:
        data = response.json()
        features = data.get(
            "features", []
        )  # All geographic information is stored in the features part of JSON response

        # Store features in temporary GeoPandas dataframe
        gd_batch = gpd.GeoDataFrame.from_features(features)

        # Convert the GeoPandas DataFrame to Pandas DataFrame
        df_batch = pd.DataFrame(gd_batch)

        # Append data to geodata dataframe
        geodata = pd.concat([geodata, df_batch], ignore_index=True)

        # Check for amount of rows in latest response and break when smaller then amount of rows requested in count
        if len(features) < count:
            break

        # Update the startindex for the next request
        startindex += len(features)
    else:
        # Break when responsecode is not 200
        break

# Return dataframe as output
geodata
