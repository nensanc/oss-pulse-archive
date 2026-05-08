"""
GitHub Archive S3 Cleanup DAG
Deletes files older than 30 days from S3 Bronze bucket.

Schedule: Daily at 2 AM UTC
Author: OSS Pulse
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

default_args = {
    'owner': 'oss-pulse',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def cleanup_old_s3_files(**context):
    """Delete S3 files older than 30 days from Bronze bucket."""
    s3_hook = S3Hook(aws_conn_id='aws_default')
    bucket_name = 'oss-pulse-bronze-2026'
    prefix = 'raw/'
    
    # Calculate cutoff date (30 days ago)
    cutoff_date = datetime.now() - timedelta(days=30)
    
    print(f"Deleting files older than {cutoff_date.strftime('%Y-%m-%d')} from s3://{bucket_name}/{prefix}")
    
    # List all objects
    keys = s3_hook.list_keys(bucket_name=bucket_name, prefix=prefix)
    
    if not keys:
        print("No files found in bucket")
        return
    
    deleted_count = 0
    skipped_count = 0
    
    for key in keys:
        # Get object metadata
        obj = s3_hook.get_key(key, bucket_name=bucket_name)
        last_modified = obj.last_modified
        
        # Delete if older than cutoff
        if last_modified < cutoff_date.replace(tzinfo=last_modified.tzinfo):
            s3_hook.delete_objects(bucket=bucket_name, keys=key)
            deleted_count += 1
            print(f"Deleted: {key} (modified: {last_modified})")
        else:
            skipped_count += 1
    
    print(f"✅ Cleanup complete: {deleted_count} files deleted, {skipped_count} files kept")

with DAG(
    'gh_archive_cleanup',
    default_args=default_args,
    description='Delete S3 files older than 30 days',
    schedule='0 2 * * *',  # Daily at 2 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['github-archive', 'maintenance', 'cleanup'],
) as dag:
    
    cleanup_task = PythonOperator(
        task_id='cleanup_old_files',
        python_callable=cleanup_old_s3_files,
    )
