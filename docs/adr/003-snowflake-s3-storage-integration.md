# ADR 003 — Snowflake-S3 Storage Integration

## Status
Accepted

## Context
Snowflake needs to read files from S3 (bronze layer) and potentially write
back to S3 (external tables, unload). Two approaches exist:

1. **AWS credentials in Snowflake** — store `AWS_KEY_ID` and `AWS_SECRET_KEY`
   in a Snowflake stage definition.
2. **Storage Integration** — Snowflake assumes an IAM role via STS, no
   long-lived credentials stored.

## Decision
Use a Storage Integration with IAM role assumption (approach 2).

Snowflake generates a unique IAM user ARN and External ID. We create an AWS
IAM role (`snowflake-oss-pulse-role`) with a trust policy that allows
Snowflake's user to assume it, gated by the External ID. The role has
permissions limited to the two project buckets.

## Consequences

**Positive**
- No AWS credentials stored in Snowflake (reduced attack surface).
- IAM role can be audited and rotated independently.
- Follows AWS/Snowflake best practices.

**Negative**
- Slightly more complex setup (IAM trust policy + External ID).
- If the integration is dropped and recreated, the External ID changes and
  the trust policy must be updated.

## Alternatives considered
- Hardcoded credentials: rejected (security risk, hard to rotate).
- Separate credentials per stage: rejected (more secrets to manage).
