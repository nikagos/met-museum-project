from museum_objects import MuseumObjects
from museum_departments import MuseumDepartments
import pandas as pd
from prefect import flow, task
from prefect_sqlalchemy import SqlAlchemyConnector
from sqlalchemy.engine import Engine
from sqlalchemy import text



# Base URLs for the API
BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1/"
OBJECTS_URL = f"{BASE_URL}objects" # list of all valid objects
DEPARTMENTS_URL = f"{BASE_URL}departments" # list of all valid departments
OBJECT_COUNT = 5000 # Adjust sample size as needed


@task(log_prints=True)
def get_objects(mo: MuseumObjects) -> pd.DataFrame:
    """Get all museum object data. Out of ~500K objects we pull just a sample (5K), as this is a process for pipeline demo purposes"""

    object_ids = mo.get_object_ids()
    # Sample a smaller subset if necessary
    sample_object_ids = object_ids[:OBJECT_COUNT]

    print(f"Getting data for {OBJECT_COUNT} objects.")
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
def check_if_table_exists(table_name: str) -> bool:
    """
    Function to check if the target table exists in the database.
    """
    check_table_exists_query = text(f"""
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = '{table_name}'
    );
    """)
    print(f"Checking if table '{table_name}' exists...")

    # Create separate SqlAlchemyConnector object via Prefect. For some reason SQLAlchemy causes issues if reusing other database_blocks created elsewhere
    database_block = SqlAlchemyConnector.load("metmuseum-postgres-connector")

    with database_block.get_connection() as connection:  # Use the engine as the context manager
        result = connection.execute(check_table_exists_query, {'table_name': table_name}).fetchone()
        table_exists = result[0] if result else False
        print(f"Table {table_name} exists: {table_exists}")
        
    return table_exists


@task(log_prints=True)
def truncate_table(table_name: str) -> None:
    """Truncate a table if it exists."""
    print(f"Truncating table {table_name}...")
    truncate_table_query = text(f"TRUNCATE TABLE {table_name};")

    # Create separate SqlAlchemyConnector object via Prefect. For some reason SQLAlchemy causes issues if reusing other database_blocks created elsewhere
    database_block = SqlAlchemyConnector.load("metmuseum-postgres-connector")

    with database_block.get_connection() as connection:
        connection.execute(truncate_table_query)
    print(f"Table {table_name} truncated successfully.")


@task(log_prints=True)
def ingest_into_postgres(df: pd.DataFrame, table_name: str) -> None:
    """Create Postgres table and ingest the data"""
    
    # Check if table exists before truncating. If it doesn't, create it
    # Create separate SqlAlchemyConnector object via Prefect. For some reason SQLAlchemy causes issues if reusing other database_blocks created elsewhere
    database_block = SqlAlchemyConnector.load("metmuseum-postgres-connector")

    with database_block.get_connection() as connection:
        table_exists = check_if_table_exists(table_name)

        if table_exists:
            truncate_table(table_name)
            df.to_sql(name=table_name, con=connection, if_exists='append', index=False)
            print("Data was ingested.")
        else:
            print(f"Table {table_name} does not exist. Skipped truncating and creating it in the database.")
            df.head(n=0).to_sql(name=table_name, con=connection, if_exists='replace', index=False)
            print("Table created.")
            df.to_sql(name=table_name, con=connection, if_exists='append', index=False)
            print("Data was ingested.")


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

    # Ingest data
    for df in dfs:
        print(f"Ingesting {df.name} dataframe...")
        ingest_into_postgres(df, df.name)


if __name__ == "__main__":
    etl_web_to_postgres()