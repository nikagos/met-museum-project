import os
from prefect import flow
from prefect.deployments.runner import DockerImage
from main_ingest import etl_web_to_postgres

user = os.getenv("USER")
github_user = os.getenv("GITHUB_USER")

@flow(log_prints=True)
def my_flow():
    etl_web_to_postgres()


if __name__ == "__main__":
    """This dockerizes the ingestion script using a Dockerfile and creates a Prefect Deployment"""

    my_flow.from_source(
        source=f"git@github.com:{github_user}/met-museum-project.git",
        entrypoint="ingestion_flows/main_ingest.py:etl_web_to_postgres"
    ).deploy(
        name="etl-met-museum-web-to-postgres-flow-deployment",
        work_pool_name="my-work-pool",
        image=DockerImage(
            name=f"{github_user}/my-met-museum-etl-web-to-postgres-flow-image",
            tag="v001",
            dockerfile=f"/home/{user}/met-museum-project/ingestion_flows/Dockerfile"
        ),
        push=True
    )