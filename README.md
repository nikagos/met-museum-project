# The Met Museum data pipeline

## About the Met Museum
The Metropolitan Museum of Art a.k.a. Met Museum is one of the most popular museums in the world, and it's based in New York City. They offer an API endpoint that people can use to access and explore their museum exhibition data digitally. 

## Purpose of the project
In the context of the [Data Engineering Zoomcamp] (https://datatalks.club/), which teaches all about building pipelines, I decided to put this knowledge into practice and implement this pipeline. 

## Pipeline architecture
The pipeline utilizes a wide range of tools that are nowdays part of the modern data engineering stach. More specifically:
1. **Terraform** as the Infrastructure as Code tool to spin up the compute and storage resources of GCP
2. **Docker** to containerize the Python ingestion processes
3. **Postgres** for storage
4. **pgAdmin** as the client to surface the data and write SQL against it
5. **Docker Compose** to stitch the Postgres and pgAdmin Docker containers together
6. **Prefect** as the job orchestrator
7. **dbt** for the transformations

