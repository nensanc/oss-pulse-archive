# ADR 002 — Snowflake RBAC: Functional + Access Roles

## Status
Accepted

## Context
Snowflake roles can be granted privileges in two common patterns:
1. Privileges granted directly to roles assigned to users (simple but unscalable).
2. Functional + Access role pattern: object-level privileges live on access
   roles; users get functional roles that inherit access roles.

Pattern (2) is the Snowflake-recommended approach for any environment beyond
toy projects.

## Decision
Implement the functional + access role pattern from day one.

**Access roles** (named `AR_OSS_PULSE_<scope>_<R|RW>`) hold privileges on
schemas and objects:
- `AR_OSS_PULSE_RAW_RW`     — read/write on RAW, UTIL.
- `AR_OSS_PULSE_STAGING_RW` — read RAW; read/write on STAGING, INTERMEDIATE, SNAPSHOTS.
- `AR_OSS_PULSE_MARTS_RW`   — read/write on MARTS.
- `AR_OSS_PULSE_MARTS_R`    — read-only on MARTS.

**Functional roles** are granted to users/services:
- `LOADER`      → ingestion jobs (Airflow COPY INTO).
- `TRANSFORMER` → dbt runs.
- `REPORTER`    → Streamlit app, analyst queries.

A single service user `SVC_OSS_PULSE` is granted all three roles for now.
In a production setup, each role would have its own user.

## Consequences

**Positive**
- Onboarding new users/services means granting one functional role, not
  rewiring object privileges.
- Future grants (e.g., a new schema) only need to update access roles.
- `FUTURE GRANTS` ensure new tables inherit the right permissions
  automatically.

**Negative**
- More objects to manage on day one (4 access roles + 3 functional roles).
- Slightly more verbose setup script.

## Alternatives considered
- Direct grants to functional roles: rejected (doesn't scale, hard to audit).
- Single super-role per user: rejected (violates least privilege).
