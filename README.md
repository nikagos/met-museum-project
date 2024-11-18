# The Met Museum data pipeline

## About the Met Museum
The Metropolitan Museum of Art a.k.a. Met Museum is one of the most popular museums in the world and is based in New York City. They offer an [API](https://metmuseum.github.io/) endpoint that people can use to access and explore their museum exhibition data digitally.

## Purpose of the project
In the context of the [Data Engineering Zoomcamp](https://datatalks.club/), which teaches all about building pipelines, I decided to put this knowledge into practice and implement this pipeline. Note that we are skipping the visualization part of the data lifecycle, as we want to purely focus on the ELT part and not the consumption.

## Pipeline architecture
The pipeline utilizes a wide range of tools that are nowadays part of the modern data engineering stack. More specifically:
1. **Terraform** as the Infrastructure as Code tool to spin up the compute and storage resources of GCP
2. **Docker** to containerize the Python ingestion processes
3. **Postgres** for storage
4. **pgAdmin** as the client to surface the data and write SQL against it
5. **Docker Compose** to stitch the Postgres and pgAdmin Docker containers together
6. **Prefect** as the job orchestrator
7. **dbt** for the transformations

<img src="https://github.com/nikagos/met-museum-project/blob/master/images/pipeline_architecture.png" width="1000">

## Setting up the environment

## Prerequisites to run the pipeline
1. Postgres credentials need to be stored in a Prefect Block (Prefect > Blocks > Create > Select "SQLAlchemy Connector")
  * Note that we used the option SyncDriver > "postgresql+psycopg2"
2. Prefect Server is running (command “prefect server start”)
3. Docker-compose is running (command  “docker-compose up --build” or “docker-compose up -d”)
4. Ports 5432 (Postgres), 8080 (pgAdmin), 4200 (Prefect) have been forwarded. I use VS Code for this and the Ports > Forward option available.

## Run the pipeline
1. Open up your terminal and clone the repo locally
2. Navigate to `/met-museum-project/ingestion_flows` directory and run:
```
python git-deploy-museum-web-to-postgres.py
```
  * This will create and deploy the Docker Image of your ingestion process
  * The deployment should appear in your list of Deployments on Prefect UI
  * Make sure the output of this command has the instructions about how to start the Worker and execute the new Deployment (see next steps)
3. In a different terminal tab start the Prefect Worker:
```
prefect worker start --pool 'my-work-pool'
```
  * Please refer to the Prefect [documentation](https://docs.prefect.io/3.0/deploy/infrastructure-concepts/workers) for more information on Workers
4. In a different terminal tab run the Prefect Deployment:
```
prefect deployment run 'etl-web-to-postgres/etl-met-museum-web-to-postgres-flow-deployment'
```
5. In the Prefect Workers tab check the progress of the ingestion. It should finish error-free and with a message:
```
19:04:18.696 | INFO    | prefect.worker.docker.dockerworker a2212102-69f5-4471-b742-c9229c432d55 - Docker container 'petite-turkey' has status 'exited'
```
6. If everything has finished without issues, navigate to the dbt folder of this repo and run:
```
dbt duild
```
  * This will build and run tests against all the new dbt models: `departments_base`,`objects_base`,`object_measurements`, and `constituents`. These should appear under Views in pgAdmin.
7. 
    
