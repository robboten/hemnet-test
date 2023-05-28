import json

from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from pathlib import Path
import requests
import yaml

# Create a folder for all the files

# Parent directory path
parent_dir_path = "./data/stockholms_kommun/"

# Current utc, yeat, month and day
# utcnow = datetime.utcnow().strftime("%Y%m%d_%H%M")
dateoftoday = datetime.utcnow().strftime("%Y%m%d")
year = datetime.utcnow().strftime("%Y")
month = datetime.utcnow().strftime("%m")
day = datetime.utcnow().strftime("%d")

# Directory path
directory_path = f"{parent_dir_path}{year}/{month}/{day}/"

# Create the directory path in os
Path(directory_path).mkdir(parents=True, exist_ok=True)

# Read the areas and their hemnet area code from config
with open("./configs/stockholms_kommun_ids.yaml", "r") as stream:
    area_info = yaml.safe_load(stream)

# Varible to keep the count of the listings.
listings_count = 0

# Loop thruogh all the areas one by one
for area in area_info:
    area_code = area_info[area]["area_code"]

    # Start the process of scaring
    url = "https://www.hemnet.se/bostader"
    params= {
        #"housing_form_groups":"apartments",
        "location_ids":area_code,
        #"item_types":"bostadsratt",
        "rooms_min":0,
        "living_area_min":0,
        "new_construction":"include"
    }
    payload={}
    headers = {"User-Agent": "Mozilla/5.0"
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        data=payload,
        params=params
    )

    soup = BeautifulSoup(response.content, "html.parser")
    map_results=soup.find(id="results-map")
    initial_data=map_results.attrs["data-initial-data"]
    json_data=json.loads(initial_data)

    url = "https://www.hemnet.se/bostader/search/"+json_data["search_key"]

    params= {}
    payload={}

    headers = {"User-Agent": "Mozilla/5.0"}

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

    print(f"{area:35} {df.shape}")

    # Enrich the df with info about internal area naming and date
    df["area"] = area
    df["date"] = dateoftoday

    # Update the listings_count
    listings_count += df.shape[0]

    #Update the area_info dictionary
    area_info[area]["listings"] = df.shape[0]

    # Save the dataframe inside directory
    df.to_parquet(f"{directory_path}{area}.parquet.gzip", compression="gzip")

print(f"\n{listings_count} listings in Stockholms kommun today! \n")

# area_info["listings_in_stockholms_lan"] = listings_count

# with open(f"{directory_path}stockholms_kommun_{dateoftoday}.yml", "w") as outfile:
#     yaml.dump(area_info, outfile, default_flow_style=False, sort_keys=False)

# with open(f"{directory_path}stockholms_kommun_{dateoftoday}.json", "w") as outfile:
#     outfile.write(json.dumps(area_info, sort_keys=False))

# with open(f"{directory_path}stockholms_kommun_{dateoftoday}.txt", "w") as outfile:
#     outfile.write(json.dumps(area_info, sort_keys=False))