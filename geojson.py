import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import box


# Pagination identificators
count = 1000
startindex = 0

# Initiliazing empty GeoPandas DataFrame to store the results
geodata = pd.DataFrame()

# Making request and appending results in dataframe
while True:
    geojson_url = f'https://service.pdok.nl/cbs/gebiedsindelingen/2022/wfs/v1_0?request=GetFeature&service=WFS&version=2.0.0&typeName=buurt_gegeneraliseerd&outputFormat=json&count={count}&startIndex={startindex}&srsName=EPSG:4326'
    response = requests.get(geojson_url)
    
    if response.status_code == 200:
        data = response.json()
        features = data.get("features", [])
       
        # Extract the bbox and other attributes into lists
        bbox_list = [feature['bbox'] for feature in features]       
        statcode_list = [feature['properties']['statcode'] for feature in features]

        statdata = pd.DataFrame({'statcode': statcode_list, 'bbox': bbox_list})  

        # Append data to geodata 
        geodata = pd.concat([geodata,statdata], ignore_index=True)

        # Check for latest response and break after
        if len(features) < count:          
            break

        # Update the startIndex for the next request
        startindex += len(features)
    else:        
        break


# Adding BBOX columns
geodata[['minx', 'miny', 'maxx', 'maxy']] = geodata['bbox'].apply(lambda x: pd.Series({'minx': x[0], 'miny': x[1], 'maxx': x[2], 'maxy': x[3]}))
geodata['geometry'] = [box(minx, miny, maxx, maxy) for minx, miny, maxx, maxy in zip(geodata['minx'], geodata['miny'], geodata['maxx'], geodata['maxy'])]

# Getting data from from workbook dataset and cleaning dataset
file_path = "C:\Users\niels\OneDrive\7. Portfolio Data Analytics\Challenges\Innergy\Zwerfinator\Project/dataset-zwerfinator-incl-sleutels.xlsx"
workbook = pd.read_excel(file_path,sheet_name="Data")
workbook


workbook = pd.read_excel("dataset-zwerfinator-incl-sleutels.xlsx", sheet_name="Data")
workbook.columns = workbook.columns.str.lower()
workbook = workbook[['latitude', 'longitude']] 
workbook.drop_duplicates(subset=['latitude', 'longitude'], inplace=True)

# Creating seperate GeoData dataframes
workbook_gdf = gpd.GeoDataFrame(workbook, geometry=gpd.points_from_xy(workbook['longitude'], workbook['latitude']))
geodata_gdf = gpd.GeoDataFrame(geodata)
geodata_gdf['polygon'] = geodata_gdf['geometry']
geodata_gdf.set_geometry('geometry', inplace=True)

# Perform a spatial join to find points that fall within the bboxes
neighbourhood_statcodes = gpd.sjoin(workbook_gdf, geodata_gdf, how="left", predicate="intersects")


# Filtering columns
neighbourhood_statcodes = neighbourhood_statcodes[['latitude', 'longitude', 'statcode', 'polygon']] 
neighbourhood_statcodes.drop_duplicates(subset=['latitude', 'longitude'], inplace=True)

neighbourhood_statcodes = pd.DataFrame(neighbourhood_statcodes)
neighbourhood_statcodes['latitude'] = round(neighbourhood_statcodes['latitude'],13)
neighbourhood_statcodes['longitude'] = neighbourhood_statcodes['longitude'].apply(lambda x: round(x, 14))


