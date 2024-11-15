from museum_objects import MuseumObjects
from museum_departments import MuseumDepartments
import requests
import pandas as pd
from prefect import flow, task
from prefect_sqlalchemy import SqlAlchemyConnector
from sqlalchemy.engine import Engine
from sqlalchemy import text
from sqlalchemy import create_engine



# Base URLs for the API
BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1/"
OBJECTS_URL = f"{BASE_URL}objects" # list of all valid objects
DEPARTMENTS_URL = f"{BASE_URL}departments" # list of all valid departments


# # @task(log_prints=True)
# def fetch_department_data(md: MuseumDepartments) -> list:
#     """Fetch object data"""
#     print("Inside fetch_department_data function")
#     print(f"Getting data for departments url: {md.departments_url}")
#     department_response = requests.get(md.departments_url)
    
#     if department_response.status_code == 200:

#         # Get all keys from dictionary "department_data"
#         department_data = department_response.json()
#         # key "departments" contains all the valid departments that we want to parse
#         filtered_key = [key for key in department_data if key == "departments"]

#         # Use the .get() method on the data dictionary to retrieve the value associated with the key "departments"
#         departments_list = department_data.get(filtered_key[0], [])
#         print("Finished with fetch_department_data function")
#         return departments_list
#     else:
#         return None


# # @task(log_prints=True)
# def generate_department_data_df(results: list) -> pd.DataFrame:
#     """# Convert list of dictionaries to DataFrame"""
#     print("Inside generate_department_data_df function")
#     df = pd.DataFrame(results)
#     # Rename column
#     print("Finished with generate_department_data_df function")
#     return df.rename(columns={"displayName": "departmentName"})


@task(log_prints=True)
def get_objects(mo: MuseumObjects) -> pd.DataFrame:
    """Get all museum object data"""

    object_ids = mo.get_object_ids()
    # Sample a smaller subset if necessary
    sample_object_ids = object_ids[:100]  # Adjust sample size as needed

    print("Getting all Object data.")
    results = mo.get_object_data(sample_object_ids)
    print("Generating Object data df.")
    object_data_df = mo.generate_object_data_df(results)
    return object_data_df


@task(log_prints=True)
def get_departments(md: MuseumDepartments) -> pd.DataFrame:
    """Get all museum department data"""
    print("Inside get_departments function")
    results = md.fetch_department_data()
    results_filtered = [res for res in results if res is not None]
    # print(results_filtered)

    department_data_df = md.generate_department_data_df(results_filtered)
    print("Finished with get_departments function")
    return department_data_df


@task(log_prints=True)
def ingest_into_postgres(df: pd.DataFrame, engine: Engine, table_name: str) -> None:
    """Create Postgres table and ingest the data"""

    # # Check connection to metmuseum
    # print("Checking connection...")
    # result = engine.execute(text("SELECT current_database()")).fetchone()
    # print(f"Connected to database: {result[0]}")  # Should print "metmuseum"

    print(f"Creating {table_name} table in the database.")
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace', index=False)
    print(df.head())
    print("Table created.")
    df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
    print("Data was ingested.")


@flow()
def etl_web_to_postgres() -> None:
    """The main ETL function"""

    # user = "root"
    # password = "root"
    # host = "localhost"
    # port = 5432
    # db = "metmuseum"
    # engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    
    mo = MuseumObjects(OBJECTS_URL)
    md = MuseumDepartments(DEPARTMENTS_URL)
    dfs = []

    # Get all museum object data
    object_data_df = get_objects(mo)
    print(object_data_df.head())
    object_data_df.name = "objects"
    dfs.append(object_data_df)

    # Get all museum department data
    department_data_df = get_departments(md)
    print(department_data_df.head())
    department_data_df.name = "departments"
    dfs.append(department_data_df)
    
    # print(object_data_df.head())
    # print(dfs)
    # print(department_data_df.head())

    # Import the metmuseum-postgres-connector built in Prefect as the database engine
    database_block = SqlAlchemyConnector.load("metmuseum-postgres-connector")

    # Utilize Prefect Block to create an engine and ingest the data
    with database_block.get_connection(begin=False) as engine:
        # Ingest data
        for df in dfs:
            # Drop table with all dependencies
            # engine.execute(text(f"DROP TABLE IF EXISTS {department_data_df.name} CASCADE"))
            print(f"Ingesting {df.name} dataframe...")
            ingest_into_postgres(df, engine, df.name)


if __name__ == "__main__":
    etl_web_to_postgres()