from google.cloud import bigquery

def copy_tables(source_project_id, source_dataset_id, destination_project_id, destination_dataset_id):
    # Initialize a BigQuery client
    client = bigquery.Client()

    # Construct a BigQuery client to source dataset reference
    source_dataset_ref = client.dataset(source_dataset_id, project=source_project_id)

    # List all tables in the source dataset
    tables = client.list_tables(source_dataset_ref)

    # Iterate over each table in the source dataset
    for table in tables:
        source_table_id = f"{source_project_id}.{source_dataset_id}.{table.table_id}"
        destination_table_id = f"{destination_project_id}.{destination_dataset_id}.{table.table_id}"

        # Copy table
        job = client.copy_table(source_table_id, destination_table_id)

        # Wait for the job to complete
        job.result()
        print(f"Table {table.table_id} copied successfully to {destination_dataset_id} in {destination_project_id}.")

# Replace with your source and destination details
source_project_id = 'your-source-project-id'
source_dataset_id = 'your-source-dataset-id'
destination_project_id = 'your-destination-project-id'
destination_dataset_id = 'your-destination-dataset-id'

copy_tables(source_project_id, source_dataset_id, destination_project_id, destination_dataset_id)
