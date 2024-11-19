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

Note that we built a virtual machine in GCP because they provide 90-day/$300 credit to access their tools.

## Setting up the environment
All the tools in the diagram above need to be installed on your machine. This can be complex and time-consuming to outline here, so I strongly encourage you to watch the following videos. For dbt specifically, we've described the detailed steps below, but there are plenty of resources on the dbt website and online to accomplish this
1. Terraform: [Video 1](https://www.youtube.com/watch?v=s2bOYDCKl_M&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=13), [Video 2](https://www.youtube.com/watch?v=Y2ux7gq3Z0o&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=13), [Video 3](https://www.youtube.com/watch?v=PBi0hHjLftk&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=15)
2. Docker
3. Postgres
4. pgAdmin
5. Docker Compose
6. Prefect
7. dbt
  * Confirm that you have the right Python version installed (3.7 or higher)
```
python --version
```
or
```
python3 --version
``` 
  * Install `dbt-core`. Also, because we are using Postgres, we need to install the `dbt-postgres` connector too along with dbt-core. In your terminal run:
```
python -m pip install dbt-core dbt-postgres
```
  * Install dbt dependencies:
```
dbt deps
```
  * Configure Your dbt Profile. dbt requires a `profiles.yml` file to connect to your database. This file is typically located in the `~/.dbt/` directory. Create or edit the `profiles.yml` file such as:
```
met_museum_dbt_project:
  outputs:
    dev:
      dbname: metmuseum
      host: localhost
      pass: root
      port: 5432
      schema: public
      threads: 1
      type: postgres
      user: root
    prod:
      dbname: metmuseum_prod
      host: localhost
      pass: root
      port: 5432
      schema: public
      threads: 1
      type: postgres
      user: root
  target: dev
```
Notice that we have a **dev** and a **prod** profile.

After completing these steps, your dbt environment is set up and you can use the assets of this repo to create your dbt models too.


## Before you run the pipeline
1. Postgres credentials need to be stored in a Prefect Block (Prefect > Blocks > Create > Select "SQLAlchemy Connector")
  * Note that we used the option SyncDriver > "postgresql+psycopg2"
2. Prefect Server is running (run command `prefect server start`)
3. Docker-compose is running (run command `docker-compose up --build` or `docker-compose up -d`)
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
 * After this, both tables (`departments` and `objects`) should be built and appear in pgAdmin under Servers > (right-click and Register > Server > (click on new Server name) > Databases > metmuseum > Schemas > public > Tables)
6. If everything has finished without issues, navigate to the dbt folder of this repo and run:
```
dbt duild
```
  * This will build and run tests against all the new dbt models in the **dev** environment db name `metmuseum`: `departments_base`, `objects_base`, `object_measurements`, and `constituents`. These should appear under Views in pgAdmin.
7. If you have a production database too (i.e. a copy of the dev database `metmuseum`), you can also run
```
dbt build --target prod
```
* This will build and run tests against all the new dbt models in the **prod** environment (db name `metmuseum_prod`): `departments_base`, `objects_base`, `object_measurements`, and `constituents`. These should appear under Views in pgAdmin.
    
