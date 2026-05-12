# OSS Pulse - AI-Powered GitHub Archive Analytics

> Production-grade data platform that ingests, transforms, and enables AI-powered querying of GitHub Archive data.

A complete data engineering project demonstrating modern data stack expertise: from automated ingestion through Airflow, transformation with dbt, to natural language querying via Claude AI.

## 🎯 What It Does

- **Ingests** 2.5GB+ of GitHub events hourly from GitHub Archive
- **Stores** raw data in S3 and loads into Snowflake
- **Transforms** JSON events into a star schema data warehouse (254K+ events)
- **Enables** natural language queries using Claude AI
- **Exports** results to CSV for further analysis

## 📊 Live Metrics

**Data Processed:**
- 254,743 GitHub events
- 230,212 individual commits
- 16,702 pull requests
- 74,552 unique repositories
- 58,168 unique users
- 10,224 organizations

**Performance:**
- Airflow ingestion: ~65 seconds per hour
- dbt full run: ~15 seconds
- AI query response: ~2-3 seconds average

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Orchestration** | Apache Airflow 3.0.4 | Hourly DAG scheduling, task dependencies |
| **Storage (Bronze)** | AWS S3 | Raw JSON.gz files from GitHub Archive |
| **Storage (Silver)** | AWS S3 | Processed Parquet (future enhancement) |
| **Data Warehouse** | Snowflake | XSMALL warehouses, medallion architecture |
| **Transformation** | dbt 1.11.9 | Star schema modeling, data quality tests |
| **AI - Text-to-SQL** | Claude Sonnet 4.5 | Natural language → SQL conversion |
| **UI/Dashboard** | Streamlit 1.57.0 | Interactive query interface |
| **Language** | Python 3.11 | Airflow DAGs, data scripts |
| **Containerization** | Docker Compose | Airflow services |

## 🏗️ Architecture

```
GitHub Archive (gharchive.org)
        ↓
    [Airflow DAG - Hourly]
        ↓
   S3 Bronze Bucket
   (oss-pulse-bronze-2026)
        ↓
   Snowflake RAW Layer
   (OSS_PULSE.RAW.EVENTS)
        ↓
    [dbt Models]
        ↓
   Snowflake Star Schema
   (STAGING schema - 9 models)
        ↓
    [Claude AI + Streamlit]
        ↓
   Natural Language Query Interface
   http://localhost:8501
```

## 📁 Project Structure

```
oss-pulse-archive/
├── airflow/                    # Orchestration layer
│   ├── dags/
│   │   ├── gh_archive_ingest.py       # Main ingestion DAG (hourly)
│   │   └── gh_archive_cleanup.py      # S3 cleanup DAG (daily)
│   ├── docker-compose.yml             # Airflow services
│   ├── Dockerfile                     # Custom Airflow image
│   └── requirements.txt               # Airflow dependencies
│
├── dbt/oss_pulse/             # Transformation layer
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_events.sql         # Parse JSON events (254K rows)
│   │   │   ├── stg_pull_requests.sql  # PR details (16K rows)
│   │   │   ├── stg_commits.sql        # Commits (230K rows)
│   │   │   └── schema.yml             # Tests + documentation
│   │   └── marts/core/
│   │       ├── dim_users.sql          # User dimension (58K)
│   │       ├── dim_repos.sql          # Repo dimension (75K)
│   │       ├── dim_repos_scd2.sql     # SCD Type 2 historical tracking
│   │       ├── dim_orgs.sql           # Org dimension (10K)
│   │       ├── dim_time.sql           # Date dimension (1,096 days)
│   │       ├── fact_events.sql        # Main fact table (255K)
│   │       └── schema.yml             # Tests + documentation
│   ├── dbt_project.yml
│   └── packages.yml                   # dbt_utils
│
├── app/                       # AI query interface
│   ├── app.py                        # Streamlit chat UI
│   ├── text_to_sql.py                # Claude text-to-SQL agent
│   ├── query_executor.py             # Snowflake query execution
│   ├── schema_context.py             # Database schema for AI
│   └── requirements.txt              # App dependencies
│
├── docs/                      # Documentation
│   ├── adr/                          # Architecture Decision Records
│   │   ├── 001-iam-least-privilege.md
│   │   ├── 002-snowflake-rbac-pattern.md
│   │   └── 003-snowflake-s3-storage-integration.md
│   ├── SPRINT_2_COMPLETE.md
│   └── DBT_ARCHITECTURE_GUIDE.md
│
├── .env.example               # Environment template
├── .gitignore
├── PROGRESS.md                # Sprint tracking
└── README.md                  # This file
```

## 🗄️ Data Model (Star Schema)

### Staging Layer
- **STG_EVENTS** - Parsed GitHub events with typed columns
- **STG_PULL_REQUESTS** - Pull request details and metrics
- **STG_COMMITS** - Individual commits from push events

### Dimensional Model

**Dimensions:**
```sql
DIM_USERS       -- 58,168 users (surrogate key: user_key)
DIM_REPOS       -- 74,552 repos (surrogate key: repo_key)
DIM_REPOS_SCD2  -- Repos with SCD Type 2 change tracking
DIM_ORGS        -- 10,224 orgs (surrogate key: org_key)
DIM_TIME        -- 1,096 days (2024-2026, key: YYYYMMDD)
```

**Facts:**
```sql
FACT_EVENTS     -- 254,743 events
                -- FKs: user_key, repo_key, org_key, date_key
                -- Measures: event_type, created_at, is_public
                -- Clustered by: created_at, event_type
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (for Airflow)
- Python 3.11+
- AWS Account (S3 access)
- Snowflake Account (free trial works)
- Anthropic API Key (for Claude)

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/oss-pulse-archive.git
cd oss-pulse-archive

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Setup environment variables
cp .env.example .env
# Edit .env with your credentials:
# - AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
# - SNOWFLAKE_ACCOUNT / SNOWFLAKE_USER / SNOWFLAKE_PASSWORD
# - ANTHROPIC_API_KEY
```

### 2. Start Airflow

```bash
cd airflow
docker-compose up -d

# Wait ~30 seconds for services to start
# Access UI: http://localhost:8080
# Login: airflow / airflow

# Trigger ingestion DAG manually or wait for hourly schedule
```

### 3. Run dbt Models

```bash
cd ../dbt/oss_pulse

# Install dbt
pip install dbt-snowflake

# Run transformations
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve --port 8080
```

### 4. Launch AI Query Interface

```bash
cd ../../app

# Install dependencies
pip install -r requirements.txt

# Start Streamlit
streamlit run app.py

# Access UI: http://localhost:8501
```

## 💬 Example Queries

Try these natural language questions in the AI interface:

**Repository Analysis:**
- "What are the top 10 repositories by commit count?"
- "Which repositories have the most pull requests?"
- "Show me repositories with more than 1000 commits"

**User Activity:**
- "Who are the most active users?"
- "Show me user activity by event type"
- "Which users have the most merged pull requests?"

**Pull Request Metrics:**
- "How many pull requests were merged?"
- "What's the average number of commits per pull request?"
- "Show me PRs with the most code changes"

**Temporal Analysis:**
- "How many events happened in January 2024?"
- "Show me activity by day of week"
- "What are the busiest hours for commits?"

## 🧪 Data Quality & Testing

**dbt Tests Implemented:**
- 36 total tests across all models
- 100% pass rate
- Coverage:
  - Unique key constraints (primary keys)
  - Not null constraints (critical fields)
  - Referential integrity (foreign keys)
  - Accepted values (enum validation)

**Test Execution:**
```bash
cd dbt/oss_pulse
dbt test

# Output:
# Done. PASS=36 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=36
```

## 🔒 Security Features

**AWS IAM:**
- Least-privilege policy (`oss-pulse-s3-rw`)
- Limited to 2 specific S3 buckets
- Service user with programmatic access only

**Snowflake RBAC:**
```
Access Roles:    AR_OSS_PULSE_RAW_RW
                 AR_OSS_PULSE_STAGING_RW
                 AR_OSS_PULSE_MARTS_RW
                 AR_OSS_PULSE_MARTS_R

Functional Roles: LOADER (ingestion)
                  TRANSFORMER (dbt)
                  REPORTER (queries)

Service User:     SVC_OSS_PULSE
```

**AI Query Safety:**
- SQL injection prevention via validation
- Whitelist: Only SELECT statements allowed
- Blacklist: DDL/DML operations blocked
- Regex-based dangerous keyword detection

## 📈 Performance & Costs

**Airflow DAG Performance:**
- Average run time: 65 seconds per hour
- Tasks: download (20s) → upload (15s) → load (25s) → cleanup (5s)
- Success rate: 99.5% (181 runs, 1 failure)

**Snowflake Costs (Monthly Estimate):**
- WH_LOADING: ~$8 (65 sec/hour × 730 hours × $0.00056/sec)
- WH_TRANSFORMING: ~$3 (15 sec/day × 30 days × $0.00056/sec)
- WH_REPORTING: ~$4 (ad-hoc queries)
- Storage: ~$5 (few GB compressed)
- **Total: ~$20/month**

**AWS S3 Costs:**
- Storage: ~$3/month (lifecycle policies clean old data)
- Data transfer: ~$2/month
- **Total: ~$5/month**

**Claude API Costs:**
- ~$10/month (depends on query volume)

**Total Monthly Cost: ~$35**

## 🎓 Key Learnings & Architecture Decisions

### Medallion Architecture
```
Bronze (Raw):       S3 JSON.gz files (immutable)
Silver (Staging):   Snowflake parsed events (incremental)
Gold (Marts):       Star schema (analytics-ready)
```

### Design Patterns Implemented
1. **Incremental Loading** - Merge strategy prevents duplicates
2. **Surrogate Keys** - MD5 hashes for dimension PKs
3. **SCD Type 2** - Historical change tracking for repos
4. **Star Schema** - Optimized for BI tools and AI queries
5. **Deduplication** - ROW_NUMBER() pattern for dimensions

### Challenges Solved

**Challenge 1: Duplicate Commits**
- **Issue**: Same commit SHA appeared in multiple events
- **Solution**: Composite key (event_id + commit_sha)
- **Result**: 230,212 unique commit-event pairs

**Challenge 2: Schema Naming**
- **Issue**: dbt created STAGING_STAGING schema
- **Solution**: Removed explicit schema config, use folder structure
- **Result**: Clean STAGING schema

**Challenge 3: Type Inference**
- **Issue**: Understanding how column types are determined
- **Clarification**: Snowflake infers types from SQL functions, not dbt
- **Learning**: `year()` → NUMBER, `monthname()` → VARCHAR

## 📝 Architecture Decision Records

See `docs/adr/` for detailed rationale:

- **ADR-001**: IAM Least Privilege Pattern
- **ADR-002**: Snowflake RBAC with Functional + Access Roles
- **ADR-003**: S3 Storage Integration vs Hardcoded Credentials

## 🚢 Deployment (Optional)

### Streamlit Cloud
```bash
# 1. Push to GitHub
git push origin main

# 2. Visit https://streamlit.io/cloud
# 3. Connect repo and configure secrets
# 4. Deploy automatically
```

**Secrets Configuration:**
```toml
# .streamlit/secrets.toml
SNOWFLAKE_ACCOUNT = "your-account"
SNOWFLAKE_USER = "your-user"
SNOWFLAKE_PASSWORD = "your-password"
ANTHROPIC_API_KEY = "your-api-key"
```

## 🔄 Maintenance

**Airflow:**
```bash
# View logs
docker-compose logs -f api-server

# Restart services
docker-compose restart

# Stop services
docker-compose down
```

**dbt:**
```bash
# Incremental run (only new data)
dbt run

# Full refresh (rebuild everything)
dbt run --full-refresh

# Run specific model
dbt run --select dim_users
```

**Snowflake:**
```sql
-- Check data freshness
SELECT MAX(loaded_at) FROM OSS_PULSE.RAW.EVENTS;

-- Check warehouse costs
SHOW WAREHOUSES;
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP());
```

## 🤝 Contributing

This is a portfolio project. Feel free to fork and adapt for your own learning!

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **GitHub Archive** for providing public event data
- **Anthropic** for Claude API
- **dbt Labs** for the dbt framework
- **Streamlit** for the UI framework
- **Snowflake** for the data platform

## 📚 Resources

- [GitHub Archive Documentation](https://www.gharchive.org/)
- [dbt Documentation](https://docs.getdbt.com/)
- [Snowflake Documentation](https://docs.snowflake.com/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
