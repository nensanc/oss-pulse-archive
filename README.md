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

_(See `docs/architecture.md` — coming in Sprint 0.)_

## Status

🚧 In active development. See [ADRs](./docs/adr/) for design decisions.

## License

MIT
