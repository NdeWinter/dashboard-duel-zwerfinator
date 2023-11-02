import requests
import xlwings as xw
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

def fetch_and_convert_to_dataframe(lat,lon):
     
    url  = f'https://api.pdok.nl/bzk/locatieserver/search/v3_1/reverse?lat={lat}&lon={lon}&type=gemeente&type=postcode&type=wijk&type=buurt&distance=1&rows=50'

    try:
        # Send a GET request to the API URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # If the response contains results, create lists to store the values
            if 'response' in data and 'docs' in data['response']:
                docs = data['response']['docs']
                
                gemeente = []
                buurt = []
                wijk = []

                for doc in docs:
                    if doc['type'] == 'gemeente':
                        gemeente.append(doc['weergavenaam'])
                    elif doc['type'] == 'buurt':
                        buurt.append(doc['weergavenaam'])
                    elif doc['type'] == 'wijk':
                        wijk.append(doc['weergavenaam'])

                # Create a single row in a dictionary
                data_dict = {
                    'gemeente': ', '.join(gemeente),
                    'buurt': ', '.join(buurt),
                    'wijk': ', '.join(wijk)
                }

                # Create a DataFrame from the dictionary
                df = pd.DataFrame([data_dict])
                return df
            else:
                print("No results found in the JSON response.")
        else:
            print(f"Request failed with status code {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return None

# Initialize connecting to workbook
workbook = pd.read_excel("dataset-zwerfinator-incl-sleutels.xlsx", sheet_name="Data")
workbook = workbook[['latitude', 'Longitude']]  # Replace 'Longitude' with the actual column name

# Convert 'latitude' and 'Longitude' to strings
workbook['latitude'] = workbook['latitude'].astype(str)
workbook['Longitude'] = workbook['Longitude'].astype(str)

# Get the first 7 characters from each column
workbook['latitude'] = workbook['latitude'].str[:7]
workbook['Longitude'] = workbook['Longitude'].str[:7]

# Remove duplicates
workbook = workbook.drop_duplicates()
workbook = workbook.iloc[:5000]

locations = pd.DataFrame()

# Define a function to process a single row
def process_row(row):
    latitude = row['latitude']
    longitude = row['Longitude']
    location = fetch_and_convert_to_dataframe(latitude, longitude)
    return location

# Create a ThreadPoolExecutor with a specified number of threads (adjust as needed)
num_threads = 4  # You can adjust this based on your system's capabilities
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [executor.submit(process_row, row) for _, row in workbook.iterrows()]

# Collect the results
for future in futures:
    location = future.result()
    if location is not None:
        locations = pd.concat([locations, location], ignore_index=True)

locations
