# OSS Pulse

> AI-powered open source intelligence platform.

A production-grade data platform that ingests [GitHub Archive](https://www.gharchive.org/) events,
models them in a Snowflake star schema, and exposes the data through three AI layers:
**Text-to-SQL agent**, **RAG over READMEs**, and **automated daily summaries**.

## Stack

| Layer | Technology |
|---|---|
| Orchestration | Apache Airflow (Docker) |
| Distributed processing | PySpark |
| Storage (bronze/silver) | AWS S3 |
| Warehouse (gold) | Snowflake |
| Transformation | dbt-core |
| AI – Text-to-SQL | Claude Sonnet 4.5 |
| AI – Routing | Claude Haiku 4.5 |
| AI – Summaries | Gemini 2.0 Flash |
| AI – Embeddings | Voyage AI |
| Vector store | Snowflake Cortex `VECTOR` |
| App | Streamlit |
| IaC | Terraform |
| CI/CD | GitHub Actions |

## Architecture
 
```
GH Archive (JSON.gz per hour)
        ↓
   Airflow DAG (sensor + download)
        ↓
   S3 Bronze (raw JSON)
        ↓
   PySpark (clean, dedup, flatten)
        ↓
   S3 Silver (partitioned Parquet)
        ↓
   Snowflake (COPY INTO from external stage)
        ↓
   dbt (staging → intermediate → marts)
        ↓
   Snowflake Gold (star schema)
        ↓
   AI Layer (Text-to-SQL + RAG + Summaries)
        ↓
   Streamlit Dashboard
```
 
## Progress — Sprint 0 (Setup)
 
✅ **Repo structure** — monorepo with folders for airflow/, spark/, dbt/, app/, infra/  
✅ **AWS S3** — bronze/silver buckets in us-east-1, lifecycle policies (30d/60d), IAM least-privilege  
✅ **Snowflake** — warehouses per workload, OSS_PULSE database with 6 schemas (medallion), functional RBAC with access roles + functional roles, resource monitor  
✅ **S3-Snowflake integration** — storage integration with IAM role assumption (no hardcoded credentials), external stages, file format for JSON.gz  
✅ **ADRs** — 3 architecture decision records documenting IAM least-privilege, RBAC pattern, storage integration
 
**Next**: Airflow setup, first ingestion DAG, dbt setup, dimensional modeling.
 
## Key Decisions (ADRs)
 
- [ADR-001](./docs/adr/001-iam-least-privilege.md) — IAM Least Privilege for Pipeline User
- [ADR-002](./docs/adr/002-snowflake-rbac-pattern.md) — Snowflake RBAC: Functional + Access Roles
- [ADR-003](./docs/adr/003-snowflake-s3-storage-integration.md) — Snowflake-S3 Storage Integration
## Development
 
```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # TBD
 
# Configure environment
cp .env.example .env
# Edit .env with your credentials
 
# Test Snowflake connection
python -c "from dotenv import load_dotenv; import snowflake.connector, os; load_dotenv(); print('Testing...'); conn = snowflake.connector.connect(user=os.getenv('SNOWFLAKE_USER'), password=os.getenv('SNOWFLAKE_PASSWORD'), account=os.getenv('SNOWFLAKE_ACCOUNT')); print('✅ Connected')"
```
 
## License
 
MIT
