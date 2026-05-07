# OSS Pulse — Development Progress

## Sprint 0: Setup ✅ (Completado)

**Fecha**: Mayo 2026  
**Objetivo**: Infraestructura base funcional (AWS, Snowflake, integración S3).

### Completado

#### 1. Repo Structure ✅
- Estructura monorepo: `airflow/`, `spark/`, `dbt/`, `app/`, `infra/`, `docs/`
- `.gitignore` configurado para secrets, data files, build artifacts
- `.env.example` como template
- `docs/adr/` para Architecture Decision Records

#### 2. AWS S3 ✅
- **Buckets**:
  - `oss-pulse-bronze-2026` (us-east-1) — raw GH Archive JSON.gz
  - `oss-pulse-silver-2026` (us-east-1) — processed Parquet
- **Lifecycle policies**:
  - Bronze: 30 días
  - Silver: 60 días
- **IAM**:
  - Policy custom `oss-pulse-s3-rw` (least-privilege, solo 2 buckets)
  - User `oss-pulse-pipeline` con access keys
  - Documentado en [ADR-001](./docs/adr/001-iam-least-privilege.md)

#### 3. Snowflake ✅
- **Account**: Standard edition, us-east-1, trial activo ($400 crédito)
- **Warehouses** (3):
  - `WH_LOADING` (XSMALL, auto-suspend 60s)
  - `WH_TRANSFORMING` (XSMALL, auto-suspend 60s)
  - `WH_REPORTING` (XSMALL, auto-suspend 60s)
- **Database**: `OSS_PULSE`
- **Schemas** (6): `RAW`, `STAGING`, `INTERMEDIATE`, `MARTS`, `SNAPSHOTS`, `UTIL`
- **RBAC**:
  - 4 access roles: `AR_OSS_PULSE_RAW_RW`, `AR_OSS_PULSE_STAGING_RW`, `AR_OSS_PULSE_MARTS_RW`, `AR_OSS_PULSE_MARTS_R`
  - 3 functional roles: `LOADER`, `TRANSFORMER`, `REPORTER`
  - Service user: `SVC_OSS_PULSE` con los 3 roles
  - Documentado en [ADR-002](./docs/adr/002-snowflake-rbac-pattern.md)
- **Resource monitor**: `RM_OSS_PULSE` (50 créditos/mes cap)
- **Conexión local verificada**: Python + snowflake-connector-python ✅

#### 4. S3-Snowflake Integration ✅
- **Storage Integration**: `S3_OSS_PULSE_INTEGRATION`
  - IAM role assumption (no hardcoded credentials)
  - AWS IAM role: `snowflake-oss-pulse-role`
  - Trust policy con External ID de Snowflake
  - Permissions limitadas a 2 buckets del proyecto
  - Documentado en [ADR-003](./docs/adr/003-snowflake-s3-storage-integration.md)
- **External Stages**:
  - `STAGE_S3_BRONZE` → `s3://oss-pulse-bronze-2026/`
  - `STAGE_S3_SILVER` → `s3://oss-pulse-silver-2026/`
- **File Format**: `FF_GITHUB_ARCHIVE_JSON` (JSON + GZIP)
- **Verificado**: subida a S3 → lectura desde Snowflake ✅

### Costos acumulados
- AWS: $0 (dentro de free tier)
- Snowflake: ~$0.03 (queries de setup y tests)
- **Total**: ~$0.03 USD

---

## Sprint 1: Pipeline Core (Pendiente)

**Objetivo**: Primer DAG funcional que descarga GH Archive → S3 bronze → Snowflake raw.

### Tareas

- [ ] Setup Airflow local (Docker Compose)
- [ ] Configurar conexiones: AWS (S3), Snowflake
- [ ] DAG `gh_archive_ingest`:
  - [ ] Sensor horario (esperar archivo de GH Archive)
  - [ ] Download `.json.gz` → S3 bronze
  - [ ] COPY INTO Snowflake RAW
- [ ] DAG `gh_archive_retention` (borrar archivos >30 días en S3)
- [ ] Tests básicos de cada DAG

### Siguiente sesión
Arrancamos con Airflow Docker Compose setup.

---

## Sprint 2: Modelado dbt (Pendiente)

**Objetivo**: Star schema funcional en MARTS.

### Tareas

- [ ] Setup dbt-core + dbt-snowflake
- [ ] `profiles.yml` con conexión a Snowflake
- [ ] Modelos staging: `stg_push_events`, `stg_pr_events`, `stg_issue_events`
- [ ] Modelos intermediate: dedup, derived fields
- [ ] Modelos marts:
  - [ ] `fact_events`
  - [ ] `fact_pr_lifecycle`
  - [ ] `dim_repo` (snapshot SCD2)
  - [ ] `dim_user` (snapshot SCD2)
  - [ ] `dim_date`
- [ ] Tests: unique, not_null, relationships, dbt-expectations
- [ ] Documentación + exposures

---

## Sprint 3: AI Layer (Pendiente)

**Objetivo**: Text-to-SQL agent + RAG + resúmenes funcionando.

### Tareas

- [ ] Text-to-SQL agent (Claude Sonnet 4.5)
- [ ] RAG layer (Voyage embeddings + Snowflake VECTOR)
- [ ] Resúmenes diarios (Gemini Flash)
- [ ] Router LLM (Claude Haiku)
- [ ] Streamlit app con chat interface

---

## Sprint 4: Observabilidad + CI/CD (Pendiente)

**Objetivo**: Logging, testing, cost tracking, GitHub Actions.

### Tareas

- [ ] CI/CD: GitHub Actions para dbt tests, SQLFluff, pytest
- [ ] Cost dashboard (Snowflake ACCOUNT_USAGE + LLM API costs)
- [ ] Logging estructurado en Airflow/dbt
- [ ] Alertas (Slack/email)

---

## Notas

- Revisar ADRs antes de tomar decisiones de arquitectura
- Mantener `.env` fuera de Git (verificar con `git check-ignore .env`)
- Documentar decisiones importantes como nuevos ADRs
- Sprint 0 tardó ~3 horas — buen ritmo

