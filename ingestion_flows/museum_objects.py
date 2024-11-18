# import time
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from prefect import flow, task
from prefect_sqlalchemy import SqlAlchemyConnector
from sqlalchemy.engine import Engine
from sqlalchemy import text
import json


class MuseumObjects:


    def __init__(self, objects_url: str) -> list:
        self.objects_url = objects_url


    # @task(log_prints=True)
    def get_object_ids(self) -> list:
        """Get all object IDs"""
        response = requests.get(self.objects_url)

        if response.status_code == 200:
            data = response.json()
            # Get all keys from dictionary "data"
            data_dict_key = list(data.keys())
            # key "objectIDs" contains all the valid object id's that we want to parse
            filtered_key = [key for key in data_dict_key if key == "objectIDs"]

            # Use the .get() method on the data dictionary to retrieve the value associated with the key "objectIDs"
            object_ids = data.get(filtered_key[0], [])
            print(f"Total objects found: {len(object_ids)}")
            return object_ids
        else:
            return None


    def fetch_object_data(self, obj_id:int):
        """Fetch object data"""
        object_url = f"{self.objects_url}/{obj_id}"
        object_response = requests.get(object_url)

        if object_response.status_code == 200:
            try:
                return object_response.json()
            except requests.exceptions.JSONDecodeError:
                print(f"Invalid JSON response for object ID {obj_id}")
                return None  # Handle or log as needed
        else:
            print(f"Request failed with status code {object_response.status_code} for object ID {obj_id}")
            return None  # Handle or log as needed


    # @task(log_prints=True)
    def get_object_data(self, object_ids: list) -> list:
        """Get all object data. Use ThreadPoolExecutor to make concurrent requests. For example, if object_ids = [1, 2, 3], executor.map will call:
        fetch_object_data(1)
        fetch_object_data(2)
        fetch_object_data(3)
        almost simultaneously (up to the thread limit set by max_workers), and store their results in results.
        """
        with ThreadPoolExecutor(max_workers=200) as executor: # Adjust max_workers as needed
            # start_time = time.time()
            
            results = list(executor.map(self.fetch_object_data, object_ids)) # Substitute object_ids with sample_object_ids for testing
            
            # end_time = time.time()
            # print(f"Extracting data from API took {end_time - start_time:.2f} seconds.")

        # Filter out any failed requests (None values)
        return [res for res in results if res is not None]


    # @task(log_prints=True)
    def generate_object_data_df(self, results: list) -> pd.DataFrame:
        """# Convert list of dictionaries to DataFrame"""

        df = pd.DataFrame(results)

        # Convert complex fields to JSON format to avoid error when inserting into the table. See API response definition here: https://metmuseum.github.io/#object
        json_columns = ['additionalImages',
                        'constituents', 
                        'measurements',
                        'tags']
        
        for column in json_columns:
            if column in df.columns:
                df[column] = df[column].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)
            else:
                continue

        return df
