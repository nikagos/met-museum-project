import requests
import pandas as pd
from prefect import flow, task
from prefect_sqlalchemy import SqlAlchemyConnector
from sqlalchemy.engine import Engine
from sqlalchemy import text



class MuseumDepartments:


    def __init__(self, departments_url: str) -> list:
        self.departments_url = departments_url


    @task(log_prints=True)
    def fetch_department_data(self) -> list:
        """Fetch object data"""
        print("Inside fetch_department_data function")
        print(f"Getting data for departments url: {self.departments_url}")
        department_response = requests.get(self.departments_url)
        
        if department_response.status_code == 200:

            # Get all keys from dictionary "department_data"
            department_data = department_response.json()
            # key "departments" contains all the valid departments that we want to parse
            filtered_key = [key for key in department_data if key == "departments"]

            # Use the .get() method on the data dictionary to retrieve the value associated with the key "departments"
            departments_list = department_data.get(filtered_key[0], [])
            print("Finished with fetch_department_data function")
            return departments_list
        else:
            return None


    @task(log_prints=True)
    def generate_department_data_df(self, results: list) -> pd.DataFrame:
        """# Convert list of dictionaries to DataFrame"""
        print("Inside generate_department_data_df function")
        df = pd.DataFrame(results)
        # Rename column
        print("Finished with generate_department_data_df function")
        return df.rename(columns={"displayName": "departmentName"})