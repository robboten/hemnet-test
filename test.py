import json
import os

from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from pathlib import Path
import requests
import yaml

# Create a folder for all the files

# Parent directory path
parent_dir_path = "./data/areas_of_interest/"

# Current utc date and time
utcnow = datetime.utcnow().strftime("%Y%m%d_%H%M")
dateoftoday = datetime.utcnow().strftime("%Y%m%d")

# Directory path
directory_path = f"{parent_dir_path}{utcnow}/"

# Create the directory path in os
Path(directory_path).mkdir(parents=True, exist_ok=True)

# Read the areas and their hemnet area code from config
with open("./configs/area_ids.yaml", "r") as stream:
    area_info = yaml.safe_load(stream)

# Varible to keep the count of the listings.    
listings_count = 0
    
params= {}
payload={}

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Loop thruogh all the areas one by one
for area in area_info:
    area_code = area_info[area]["area_code"]
    
    # Start the process of scaring
    url = "https://www.hemnet.se/bostader"
    params= {
        "housing_form_groups":"apartments",
        "location_ids":area_code,
        "item_types":"bostadsratt",
        "rooms_min":0,
        "living_area_min":0,
        "new_construction":"include"
    }

    soup = BeautifulSoup(response.content, "html.parser")
    map_results=soup.find(id="results-map")
    initial_data=map_results.attrs["data-initial-data"]
    json_data=json.loads(initial_data)

    url = "https://www.hemnet.se/bostader/search/"+json_data["search_key"]

    response = requests.request(
        "GET",
        url,
        headers=headers,
        data=payload,
        params=params
    )

    r_json = response.json()
    r_properties = r_json["properties"]
    
    # Store all the listings in that area as a dataframe
    df = pd.json_normalize(
        r_properties,
        max_level=1
    )

    print(f"{area}:\t\t {df.shape}")

    # Enrich the df with info about internal area naming and date  
    df["area"] = area
    df["date"] = dateoftoday

    # Update the listings_count
    listings_count += df.shape[0]

    #Update the area_info dictionary
    area_info[area]["listings"] = df.shape[0]
    
    # Save the dataframe inside directory
    df.to_parquet(f"{directory_path}{area}.parquet.gzip", compression="gzip")
    
print(f"\n{listings_count} listings in the areas of interest today!")

area_info["total_listings"] = listings_count

with open(f"{directory_path}area_info{dateoftoday}.yml", "w") as outfile:
    yaml.dump(area_info, outfile, default_flow_style=False)
with open(f"{directory_path}area_info{dateoftoday}.txt", "w") as convert_file:
    convert_file.write(json.dumps(area_info))