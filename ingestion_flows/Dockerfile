FROM prefecthq/prefect:2-latest

# Set working directory
WORKDIR /opt/prefect/flows

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the flow scripts to the container
COPY main_ingest.py .
# COPY museum_objects.py .
# COPY museum_departments.py .

# Set the entry point to start the flow using Prefect
ENTRYPOINT [ "python", "main_ingest.py" ]