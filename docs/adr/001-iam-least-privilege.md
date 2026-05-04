# ADR 001 — IAM Least Privilege for Pipeline User

## Status
Accepted

## Context
The pipeline needs an AWS IAM identity to read from and write to S3 buckets
(bronze and silver layers). A common shortcut is to attach the AWS-managed
policy `AmazonS3FullAccess`, which grants access to **all** S3 resources in
the account, including `s3:ListAllMyBuckets`.

## Decision
Create a custom IAM policy `oss-pulse-s3-rw` that grants only:

- `s3:ListBucket` and `s3:GetBucketLocation` on the two project buckets.
- `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` on objects within
  those buckets.

The user `oss-pulse-pipeline` is the only identity attached to this policy.

## Consequences

**Positive**
- Blast radius of leaked credentials is limited to two buckets.
- The user cannot enumerate or read other buckets in the account.
- Permissions are explicit and auditable.

**Negative**
- `aws s3 ls` (without a bucket) returns AccessDenied — operators must
  reference buckets by name. This is acceptable and documented.

## Alternatives considered
- `AmazonS3FullAccess`: rejected (overly broad).
- Per-prefix policies (e.g. `bronze/raw/*`): considered for future hardening
  once the pipeline writes a stable directory structure.
