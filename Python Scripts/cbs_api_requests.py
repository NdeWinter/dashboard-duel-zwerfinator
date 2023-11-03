import requests
import pandas as pd
import geopandas as gpd

from shapely.geometry import box

class CbsLocationData:
    def __init__(self):
        pass

    @staticmethod
    def get_cbs_location_data(type, years=2023):
        """Make API request to pdok service based on location level / type to obtain general geographic information about The Netherlands from the Central Bureau of Statistics,
        Returns a Pandas DataFrame.
        
        Args:
            type (string): Location type
                provincie: Province
                gemeente: Municipality
                wijk: District
                buurt: Neighorhood 
            
            years (int, optional): Year of dataset. Defaults to 2023.
                Multiple years should be provided as list
                Minimum year is 2016

        Returns:
            bbox: Polygon geometric values for area
            id: Unique identifier
            statcode: CBS statcode 
            statnaam: Location Name
            jrstatcode: CBS statcode with year identifier
            rubriek: Type name
            
        More information can be found on: https://www.pdok.nl/ogc-webservices/-/article/cbs-gebiedsindelingen#1dd45ad87a8113e6e3ddf0723696c627
        """ """"""

        # Initiliazing empty GeoPandas DataFrame to store the response data
        geodata = pd.DataFrame()

        """Making the API request, and clean and prepare response data"""

        # Parameters

        if not isinstance(years, list):
            years = [years]  # If multiple lists are given, a list is returned

        # Remove years before 2016 because no dataset available
        years = [year for year in years if year >= 2016]

        if type == "provincie":
            type_name = "provincie_gegeneraliseerd"
        elif type == "gemeente":
            type_name = "gemeente_gegeneraliseerd"
        elif type == "wijk":
            type_name = "wijk_gegeneraliseerd"
        elif type == "buurt":
            type_name = "buurt_gegeneraliseerd"
        else:
            print("Type not valid")

        # Making request and appending results to dataframe
        for year in years:
            row_count = 1000  # Number of rows in request
            row_startindex = 0  # Start rownumber

            while True:
                url = f"https://service.pdok.nl/cbs/gebiedsindelingen/{year}/wfs/v1_0?request=GetFeature&service=WFS&version=2.0.0&outputFormat=json&srsName=EPSG:4326"

                typename = f"&typeName={type_name}"
                count = f"&count={row_count}"
                startindex = f"&startIndex={row_startindex}"

                # Executing request
                response = requests.get(f"{url}{typename}{count}{startindex}")

                # Handling response
                if response.status_code == 200:
                    data = response.json()
                    features = data.get(
                        "features", []
                    )  # All geographic information is stored in the features part of JSON response

                    # Create separate lists for each bbox and properties feature
                    bbox_list = [feature["bbox"] for feature in features]

                    properties_list = [
                        {key: feature["properties"][key] for key in feature["properties"]}
                        for feature in features
                    ]
                    property_keys = list(properties_list[0].keys())

                    # Combine lists
                    data = {
                        "bbox": bbox_list,
                        **{
                            key: [properties[key] for properties in properties_list]
                            for key in property_keys
                        },
                    }

                    # Store data in temporary dataFrame
                    statdata = pd.DataFrame(data)

                    # Append temporary data to geodata dataframe
                    geodata = pd.concat([geodata, statdata], ignore_index=True)

                    # Check for amount of rows in latest response and break when smaller then amount of rows requested in count
                    if len(features) < row_count:
                        break

                    # Update the startindex for the next request
                    startindex += len(features)
                else:
                    # Break when responsecode is not 200
                    print(response)
                    break

        # Return dataframe as output
        return geodata

    @staticmethod   
    def map_cbs_location(workbookname, sheetname, cbs_type, cbs_year=2023):
        """Create a table containing cbs stat information from pdok and geometry information (point and polygon) based on longitude and latitude values in table. 
        The output can be used as mapping table in Power BI when exported as a dataframe or transformed to a Topo JSON file when exported as JSON. 

        Args:
            workbookname (string): Name of excel workbook including extension .xlsx 
            sheetname (string): Name of the sheet with dataset
            cbs_type (string): CBS location type
            cbs_year (int): Year of CBS Data (multiple values not allowed)

        Returns:
            latitude: Latitude value
            longitude: Longitude value
            geometry: Geographic Point (longitude,latitude)
            bbox: Polygon values for CBS location
            statcode: CBS statcode 
            statnaam: Location Name
            jrstatcode: CBS statcode with year identifier
            rubriek: Type name        
        """ """"""

        # Connect to workbook and extract latitde and longitude values
        workbook = pd.read_excel(workbookname, sheet_name=sheetname)
        workbook.columns = workbook.columns.str.lower()
        workbook = workbook[["latitude", "longitude"]]
        workbook.drop_duplicates(subset=["latitude", "longitude"], inplace=True)    
        
        # Make API call for CBS data and prepare data
        cbs_data = CbsLocationData.get_cbs_location_data(cbs_type, cbs_year)

        # Adding separate columns for longitude and latitude values in BBOX
        cbs_data[["minx", "miny", "maxx", "maxy"]] = cbs_data["bbox"].apply(
            lambda x: pd.Series({"minx": x[0], "miny": x[1], "maxx": x[2], "maxy": x[3]})
        )

        # Create geometry column for GeoPandas
        cbs_data["geometry"] = [
            box(minx, miny, maxx, maxy)
            for minx, miny, maxx, maxy in zip(
                cbs_data["minx"], cbs_data["miny"], cbs_data["maxx"], cbs_data["maxy"]
            )
        ]

        # Creating seperate GeoData dataframes for combining the dataset and geodata
        workbook_gdf = gpd.GeoDataFrame(
            workbook,
            geometry=gpd.points_from_xy(workbook["longitude"], workbook["latitude"]),
        )

        cbs_data_gdf = gpd.GeoDataFrame(cbs_data)
        cbs_data_gdf.set_geometry("geometry", inplace=True)

        # Creating new GeoData Dataframe based on spatial join between geometric point from the dataset and the bbox area coordinates
        combined_data = gpd.sjoin(
            workbook_gdf, cbs_data_gdf, how="left", predicate="intersects"
        )

        # Removing duplicate values
        combined_data.drop_duplicates(subset=["latitude", "longitude"], inplace=True)

        # Converting GeoPandas Dataframe to Pandas dataframe for Power Bi compatibility
        combined_data = pd.DataFrame(combined_data)

        """ Because Power Query applies an automatic rounding when the type decimal is used, I experienced an issue with
            merging on the longitude and latitude values between the output of the script and the dataset. 
            
            To fix this issue I had to round all values are rounded to 13 and 14 decimals in Python and in Power Query on the dataset.
            """

        # Performing rounding
        combined_data["latitude"] = round(combined_data["latitude"], 13)
        combined_data["longitude"] = combined_data["longitude"].apply(
            lambda x: round(x, 14)
        )

        # Filter dataframe
        combined_data = combined_data[
            [
                "latitude",
                "longitude",
                "geometry",
                "bbox",
                "statcode",
                "jrstatcode",
                "statnaam",
                "rubriek",
            ]
        ]
        # Return dataframe as output
        return combined_data

if __name__ == "__main__":
    cbs_data = CbsLocationData()
    cbs_data.get_location_data("provincie", [2023, 2022])
    cbs_data.map_location_data("workbook.xlsx", "sheet_name", "provincie", 2023)