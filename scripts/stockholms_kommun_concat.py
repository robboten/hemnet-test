import glob

from datetime import datetime
import pandas as pd
from pathlib import Path

# Open todays folder for Stockholms kommun:

# Parent directory path
stockholms_kommun_parent_dir_path = "./data/stockholms_kommun/"
stockholms_lan_parent_dir_path = "./data/stockholms_lan/"

# Current utc, year, month and day
# utcnow = datetime.utcnow().strftime("%Y%m%d_%H%M")
dateoftoday = datetime.utcnow().strftime("%Y%m%d")
year = datetime.utcnow().strftime("%Y")
month = datetime.utcnow().strftime("%m")
day = datetime.utcnow().strftime("%d")

# Directory path
stockholms_kommun_directory_path = f"{stockholms_kommun_parent_dir_path}{year}/{month}/{day}/"
stockholms_lan_directory_path = f"{stockholms_lan_parent_dir_path}{year}/{month}/{day}/"

# Path(stockholms_kommun_directory_path).mkdir(parents=True, exist_ok=True)
Path(stockholms_lan_directory_path).mkdir(parents=True, exist_ok=True)

stockholms_kommun_run_of_the_day_path = f"{stockholms_kommun_directory_path}*.parquet.gzip"
parquet_files = glob.glob(stockholms_kommun_run_of_the_day_path)
stockholms_kommun_df_list = []

for file in parquet_files:
    df = pd.read_parquet(file)
    stockholms_kommun_df_list.append(df)

stockholms_kommun_df_concat = pd.concat(stockholms_kommun_df_list)
stockholms_kommun_df_concat["area"] = "stockholm"

# Save the dataframe inside stockholms län run of the day directory
stockholms_kommun_df_concat.to_parquet(
    f"{stockholms_lan_directory_path}stockholm.parquet.gzip",
    compression="gzip")