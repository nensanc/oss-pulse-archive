"""
Database schema context for Claude to generate SQL queries.
This provides the AI with information about available tables and columns.
"""

SCHEMA_CONTEXT = """
# OSS Pulse - Snowflake Database Schema

## Database: OSS_PULSE

### Available Tables:

#### 1. STAGING.STG_EVENTS
Main events table with all GitHub activity.

Columns:
- event_id (VARCHAR) - Unique event identifier
- event_type (VARCHAR) - Type: PushEvent, PullRequestEvent, IssuesEvent, CreateEvent, etc.
- created_at (TIMESTAMP) - When the event occurred
- actor_id (NUMBER) - GitHub user ID who triggered the event
- actor_login (VARCHAR) - GitHub username
- repo_id (NUMBER) - Repository ID
- repo_name (VARCHAR) - Full repository name (owner/repo)
- org_id (NUMBER) - Organization ID (if applicable)
- org_login (VARCHAR) - Organization name
- is_public (BOOLEAN) - Whether the repository is public
- payload (VARIANT) - Full event JSON payload
- loaded_at (TIMESTAMP) - When data was loaded into warehouse

Example query:
SELECT event_type, COUNT(*) as count
FROM OSS_PULSE.STAGING.STG_EVENTS
GROUP BY event_type
ORDER BY count DESC;

---

#### 2. STAGING.STG_PULL_REQUESTS
Pull request events with detailed PR information.

Columns:
- pr_key (VARCHAR) - Surrogate key
- event_id (VARCHAR) - Related event ID
- created_at (TIMESTAMP) - Event timestamp
- actor_login (VARCHAR) - Who performed the action
- repo_name (VARCHAR) - Repository name
- pr_id (NUMBER) - Pull request ID
- pr_number (NUMBER) - PR number within repo
- pr_state (VARCHAR) - open, closed
- pr_action (VARCHAR) - opened, closed, reopened, merged
- pr_title (VARCHAR) - Pull request title
- pr_author (VARCHAR) - PR creator
- pr_created_at (TIMESTAMP) - When PR was created
- pr_merged_at (TIMESTAMP) - When PR was merged (if merged)
- pr_merged (BOOLEAN) - Whether PR was merged
- pr_comments (NUMBER) - Number of comments
- pr_commits (NUMBER) - Number of commits
- pr_additions (NUMBER) - Lines added
- pr_deletions (NUMBER) - Lines deleted
- pr_changed_files (NUMBER) - Files changed

Example query:
SELECT repo_name, COUNT(*) as pr_count
FROM OSS_PULSE.STAGING.STG_PULL_REQUESTS
WHERE pr_merged = true
GROUP BY repo_name
ORDER BY pr_count DESC
LIMIT 10;

---

#### 3. STAGING.STG_COMMITS
Individual commits extracted from push events.

Columns:
- commit_event_key (VARCHAR) - Surrogate key (event + commit)
- commit_sha (VARCHAR) - Git commit hash
- event_id (VARCHAR) - Related push event
- created_at (TIMESTAMP) - Event timestamp
- actor_login (VARCHAR) - Who pushed
- repo_name (VARCHAR) - Repository name
- commit_author_name (VARCHAR) - Commit author name
- commit_author_email (VARCHAR) - Commit author email
- commit_message (VARCHAR) - Commit message
- branch_ref (VARCHAR) - Branch reference (refs/heads/main)
- push_size (NUMBER) - Number of commits in push

Example query:
SELECT repo_name, COUNT(*) as commit_count
FROM OSS_PULSE.STAGING.STG_COMMITS
GROUP BY repo_name
ORDER BY commit_count DESC
LIMIT 10;

---

#### 4. STAGING.DIM_USERS
User dimension table.

Columns:
- user_key (VARCHAR) - Surrogate key (PK)
- user_id (NUMBER) - GitHub user ID
- login (VARCHAR) - GitHub username
- display_login (VARCHAR) - Display name
- url (VARCHAR) - GitHub API URL

---

#### 5. STAGING.DIM_REPOS
Repository dimension table.

Columns:
- repo_key (VARCHAR) - Surrogate key (PK)
- repo_id (NUMBER) - GitHub repository ID
- repo_name (VARCHAR) - Full repository name
- repo_url (VARCHAR) - GitHub API URL

---

#### 6. STAGING.DIM_ORGS
Organization dimension table.

Columns:
- org_key (VARCHAR) - Surrogate key (PK)
- org_id (NUMBER) - GitHub organization ID
- login (VARCHAR) - Organization name
- url (VARCHAR) - GitHub API URL

---

#### 7. STAGING.DIM_TIME
Date dimension table.

Columns:
- date_key (NUMBER) - Date in YYYYMMDD format (PK)
- date (DATE) - Calendar date
- year (NUMBER) - Year
- quarter (NUMBER) - Quarter (1-4)
- month (NUMBER) - Month (1-12)
- month_name (VARCHAR) - Month name (Jan, Feb, etc.)
- day (NUMBER) - Day of month
- day_of_week (NUMBER) - Day of week (0-6, 0=Sunday)
- day_name (VARCHAR) - Day name (Mon, Tue, etc.)
- week_of_year (NUMBER) - Week number (1-52)
- is_weekend (BOOLEAN) - Whether it's weekend

---

#### 8. STAGING.FACT_EVENTS
Main fact table with foreign keys to dimensions.

Columns:
- event_key (VARCHAR) - Surrogate key (PK)
- user_key (VARCHAR) - FK to dim_users
- repo_key (VARCHAR) - FK to dim_repos
- org_key (VARCHAR) - FK to dim_orgs (can be NULL)
- date_key (NUMBER) - FK to dim_time
- event_id (VARCHAR) - GitHub event ID
- event_type (VARCHAR) - Event type
- created_at (TIMESTAMP) - Event timestamp
- is_public (BOOLEAN) - Whether repo is public
- payload (VARIANT) - Full event JSON

Example star schema query:
SELECT 
    t.year,
    t.month_name,
    f.event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT f.user_key) as unique_users,
    COUNT(DISTINCT f.repo_key) as unique_repos
FROM OSS_PULSE.STAGING.FACT_EVENTS f
JOIN OSS_PULSE.STAGING.DIM_TIME t ON f.date_key = t.date_key
WHERE f.event_type IN ('PushEvent', 'PullRequestEvent')
GROUP BY t.year, t.month_name, f.event_type
ORDER BY t.year, t.month_name;

---

## Query Guidelines:

1. **Always use fully qualified table names**: `OSS_PULSE.STAGING.TABLE_NAME`
2. **Use appropriate JOINs** for star schema queries (fact → dimensions)
3. **Filter early** to improve performance
4. **Limit results** when exploring (use LIMIT)
5. **Use date filters** when possible (created_at, date_key)

## Common Query Patterns:

**Top repositories by activity:**
```sql
SELECT repo_name, COUNT(*) as event_count
FROM OSS_PULSE.STAGING.STG_EVENTS
WHERE event_type = 'PushEvent'
GROUP BY repo_name
ORDER BY event_count DESC
LIMIT 10;
```

**User activity over time:**
```sql
SELECT 
    DATE_TRUNC('day', created_at) as day,
    COUNT(*) as events
FROM OSS_PULSE.STAGING.STG_EVENTS
WHERE actor_login = 'username'
GROUP BY day
ORDER BY day;
```

**Pull request metrics:**
```sql
SELECT 
    repo_name,
    COUNT(*) as total_prs,
    SUM(CASE WHEN pr_merged THEN 1 ELSE 0 END) as merged_prs,
    AVG(pr_commits) as avg_commits_per_pr
FROM OSS_PULSE.STAGING.STG_PULL_REQUESTS
GROUP BY repo_name
ORDER BY total_prs DESC
LIMIT 10;
```
"""

def get_schema_context():
    """Return the schema context for Claude."""
    return SCHEMA_CONTEXT
