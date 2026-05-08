## Sprint 1 - Pipeline Core ✅ COMPLETED (May 7, 2026)
 
**Estimated Time**: 8-10 hours | **Actual Time**: ~10 hours
 
### Objectives
- ✅ Set up Airflow 3.0.4 with Docker
- ✅ Create GitHub Archive ingestion DAG
- ✅ Create S3 cleanup DAG
- ✅ Test end-to-end data flow
### Deliverables
 
**Airflow Setup**
- Docker Compose with Airflow 3.0.4, PostgreSQL backend, LocalExecutor
- Custom Docker image with FAB auth provider + AWS + Snowflake providers
- Connections configured: `aws_default`, `snowflake_default`
- Services: api-server (port 8080), scheduler, postgres
- Authentication: FAB (Flask-AppBuilder) with user `airflow` / `airflow`
**DAGs Created**
1. `gh_archive_ingest` - Hourly ingestion pipeline
   - Downloads GitHub Archive `.json.gz` files
   - Uploads to `s3://oss-pulse-bronze-2026/raw/YYYY/MM/DD/HH.json.gz`
   - Loads into `OSS_PULSE.RAW.EVENTS` via `COPY INTO`
   - Cleans up temp files
   - **Status**: ✅ Tested successfully with 117MB file (Jan 15, 2024 17:00)
2. `gh_archive_cleanup` - Daily S3 cleanup
   - Deletes files >30 days old from Bronze bucket
   - Schedule: Daily at 2 AM UTC
   - **Status**: ✅ Created, not yet tested
**Data Verification**
- ✅ Successfully loaded GitHub events into Snowflake
- ✅ Verified JSON parsing with VARIANT column
- ✅ Confirmed S3-Snowflake integration working
### Challenges & Solutions
 
**Challenge 1**: Airflow 3.x auth migration
- **Issue**: Default auth changed from FAB to Simple Auth Manager (no username/password)
- **Solution**: Installed `apache-airflow-providers-fab==2.4.4` and set `AIRFLOW__CORE__AUTH_MANAGER`
**Challenge 2**: Provider version compatibility
- **Issue**: Amazon provider had breaking changes, Snowflake version mismatch
- **Solution**: Used Airflow constraints file for 3.0.4 to get tested provider versions
**Challenge 3**: Snowflake connection 404 error
- **Issue**: Hostname included region suffix incorrectly
- **Solution**: Removed `.us-east-1` from hostname, used `XSGMXJC-LZC01736.snowflakecomputing.com`
**Challenge 4**: Stage permissions
- **Issue**: `LOADER` role couldn't access `UTIL.STAGE_S3_BRONZE`
- **Solution**: Granted `USAGE` on schema and stage to `LOADER` role
### Files Created
```
airflow/
├── docker-compose.yml      # Airflow 3.0.4 services
├── Dockerfile              # Custom image with providers
├── .env                    # Credentials
├── airflow.cfg             # FAB auth config
├── setup_connections.sh    # Connection setup script
└── dags/
    ├── gh_archive_ingest.py    # Main ingestion DAG
    └── gh_archive_cleanup.py   # S3 cleanup DAG
```
 
### Next Steps → Sprint 2
- Create dbt star schema models
- Implement SCD Type 2 for repositories
- Add data quality tests
- Document dimensional model
**Sprint 1 Status**: ✅ **COMPLETE**
