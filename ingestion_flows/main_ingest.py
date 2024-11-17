from museum_objects import MuseumObjects
from museum_departments import MuseumDepartments
import requests
import pandas as pd
from prefect import flow, task
from prefect_sqlalchemy import SqlAlchemyConnector
from sqlalchemy.engine import Engine
from sqlalchemy import text



# Base URLs for the API
BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1/"
OBJECTS_URL = f"{BASE_URL}objects" # list of all valid objects
DEPARTMENTS_URL = f"{BASE_URL}departments" # list of all valid departments


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

    department_data_df = md.generate_department_data_df(results_filtered)
    print("Finished with get_departments function")
    return department_data_df


@task(log_prints=True)
def ingest_into_postgres(df: pd.DataFrame, engine: Engine, table_name: str) -> None:
    """Create Postgres table and ingest the data"""

    check_table_exists_query = text(f"""
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = '{table_name}'
    );
    """)
    print(check_table_exists_query)

    truncate_table_query = text(f"TRUNCATE TABLE {table_name};")
    
    result = engine.execute(check_table_exists_query).fetchone()
    print(f"Result: {result}")
    table_exists = result[0] if result else False
    print(table_exists)

    # Check if table exists before truncating
    if table_exists:
        print(f"Table {table_name}. Truncating first...")
        engine.execute(truncate_table_query)
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        print("Data was ingested.")
    else:
        print(f"Table {table_name} does not exist. Skipped truncating and creating it in the database.")
        df.head(n=0).to_sql(name=table_name, con=engine, index=False) # if_exists='replace', 
        print("Table created.")
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        print("Data was ingested.")

    # # Check if the table exists
    # result = engine.execute(check_table_exists_query, {'table_name': table_name}).fetchone()
    # table_exists = result[0] if result else False
    # print(f"Table exists: {table_exists}")

    # # If the table exists, truncate and insert data
    # if table_exists:
    #     print(f"Table {table_name} exists. Truncating and inserting new data...")
    #     engine.execute(truncate_table_query)
    #     df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
    #     print("Data was ingested.")
    # else:
    #     # If table doesn't exist, create the table and then insert data
    #     print(f"Table {table_name} does not exist. Creating the table and inserting data...")
    #     df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
    #     print("Table created and data was ingested.")


    # print(f"Creating {table_name} table in the database.")
    # df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace', index=False)
    # print(df.head())
    # print("Table created.")
    # df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
    # print("Data was ingested.")


@flow()
def etl_web_to_postgres() -> None:
    """The main ETL function"""
    
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