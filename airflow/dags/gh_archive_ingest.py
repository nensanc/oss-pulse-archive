"""
GitHub Archive Ingestion DAG
Downloads hourly GitHub Archive data and loads it into Snowflake via S3.

Schedule: Hourly
Author: OSS Pulse
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
import requests
import gzip
import os
import tempfile

# Default arguments
default_args = {
    'owner': 'oss-pulse',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def download_gh_archive(**context):
    """Download GitHub Archive file for the given execution date."""
    # Get the execution date (data interval start in Airflow 3.x)
    logical_date = context['logical_date']
    
    # Format: 2024-01-15-13 (YYYY-MM-DD-HH)
    date_hour = logical_date.strftime('%Y-%m-%d-%-H')
    url = f"https://data.gharchive.org/{date_hour}.json.gz"
    
    print(f"Downloading from: {url}")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    local_path = os.path.join(temp_dir, f"{date_hour}.json.gz")
    
    # Download file
    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()
    
    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    file_size_mb = os.path.getsize(local_path) / (1024 * 1024)
    print(f"✅ Downloaded {file_size_mb:.2f} MB to {local_path}")
    
    # Push to XCom for next task
    context['task_instance'].xcom_push(key='local_path', value=local_path)
    context['task_instance'].xcom_push(key='date_hour', value=date_hour)
    context['task_instance'].xcom_push(key='file_size_mb', value=file_size_mb)

def upload_to_s3(**context):
    """Upload the downloaded file to S3 Bronze bucket."""
    # Pull from XCom
    ti = context['task_instance']
    local_path = ti.xcom_pull(task_ids='download_gh_archive', key='local_path')
    date_hour = ti.xcom_pull(task_ids='download_gh_archive', key='date_hour')
    
    # Parse date parts for S3 path: s3://bucket/raw/YYYY/MM/DD/HH.json.gz
    dt = datetime.strptime(date_hour, '%Y-%m-%d-%H')
    s3_key = f"raw/{dt.year:04d}/{dt.month:02d}/{dt.day:02d}/{dt.hour:02d}.json.gz"
    
    print(f"Uploading to s3://oss-pulse-bronze-2026/{s3_key}")
    
    # Upload using S3Hook
    s3_hook = S3Hook(aws_conn_id='aws_default')
    s3_hook.load_file(
        filename=local_path,
        key=s3_key,
        bucket_name='oss-pulse-bronze-2026',
        replace=True
    )
    
    print(f"✅ Uploaded to S3: s3://oss-pulse-bronze-2026/{s3_key}")
    
    # Push S3 path for next task
    ti.xcom_push(key='s3_key', value=s3_key)

def load_to_snowflake(**context):
    """Load data from S3 into Snowflake using COPY INTO."""
    # Pull from XCom
    ti = context['task_instance']
    s3_key = ti.xcom_pull(task_ids='upload_to_s3', key='s3_key')
    date_hour = ti.xcom_pull(task_ids='download_gh_archive', key='date_hour')
    
    print(f"Loading s3://oss-pulse-bronze-2026/{s3_key} into Snowflake...")
    
    # COPY INTO command - using UTIL schema for the stage
    copy_sql = f"""
    COPY INTO OSS_PULSE.RAW.EVENTS (event_data, file_name, file_row_number)
    FROM (
        SELECT 
            $1 as event_data,
            METADATA$FILENAME as file_name,
            METADATA$FILE_ROW_NUMBER as file_row_number
        FROM @OSS_PULSE.UTIL.STAGE_S3_BRONZE/{s3_key}
    )
    FILE_FORMAT = (TYPE = 'JSON' COMPRESSION = 'GZIP')
    ON_ERROR = 'CONTINUE';
    """
    
    # Execute using SnowflakeHook
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    result = snowflake_hook.run(copy_sql)
    
    print(f"✅ Loaded data for {date_hour} into Snowflake")
    print(f"Result: {result}")

def cleanup_temp_files(**context):
    """Clean up temporary local files."""
    ti = context['task_instance']
    local_path = ti.xcom_pull(task_ids='download_gh_archive', key='local_path')
    
    if local_path and os.path.exists(local_path):
        # Remove file and parent temp directory
        temp_dir = os.path.dirname(local_path)
        os.remove(local_path)
        os.rmdir(temp_dir)
        print(f"✅ Cleaned up temp file: {local_path}")
    else:
        print("No temp file to clean up")

# Define the DAG
with DAG(
    'gh_archive_ingest',
    default_args=default_args,
    description='Ingest hourly GitHub Archive data into Snowflake via S3',
    schedule='@hourly',
    start_date=datetime(2024, 1, 1, 0),  # Start from Jan 1, 2024
    catchup=False,  # Don't backfill historical data automatically
    max_active_runs=3,
    tags=['github-archive', 'ingestion', 'bronze'],
) as dag:
    
    # Task 1: Download from GitHub Archive
    download_task = PythonOperator(
        task_id='download_gh_archive',
        python_callable=download_gh_archive,
    )
    
    # Task 2: Upload to S3
    upload_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3,
    )
    
    # Task 3: Load to Snowflake
    load_task = PythonOperator(
        task_id='load_to_snowflake',
        python_callable=load_to_snowflake,
    )
    
    # Task 4: Cleanup
    cleanup_task = PythonOperator(
        task_id='cleanup_temp_files',
        python_callable=cleanup_temp_files,
        trigger_rule='all_done',  # Run even if previous tasks fail
    )
    
    # Define task dependencies
    download_task >> upload_task >> load_task >> cleanup_task
