{{
    config(
        materialized='incremental',
        unique_key='pr_key',
        incremental_strategy='merge',
        on_schema_change='append_new_columns'
    )
}}

with pull_request_events as (
    select * from {{ ref('stg_events') }}
    where event_type = 'PullRequestEvent'
    
    {% if is_incremental() %}
    and loaded_at > (select max(loaded_at) from {{ this }})
    {% endif %}
),

parsed as (
    select
        -- Unique identifier (event_id + PR number)
        {{ dbt_utils.generate_surrogate_key(['event_id', 'payload:pull_request.number']) }} as pr_key,
        
        -- Event metadata
        event_id,
        created_at,
        
        -- Actor (person who performed the action)
        actor_id,
        actor_login,
        
        -- Repository
        repo_id,
        repo_name,
        
        -- Organization
        org_id,
        org_login,
        
        -- Pull Request details
        payload:pull_request.id::number as pr_id,
        payload:pull_request.number::number as pr_number,
        payload:pull_request.state::varchar as pr_state,
        payload:action::varchar as pr_action,
        payload:pull_request.title::varchar as pr_title,
        payload:pull_request.user.login::varchar as pr_author,
        payload:pull_request.created_at::timestamp_ntz as pr_created_at,
        payload:pull_request.updated_at::timestamp_ntz as pr_updated_at,
        payload:pull_request.closed_at::timestamp_ntz as pr_closed_at,
        payload:pull_request.merged_at::timestamp_ntz as pr_merged_at,
        payload:pull_request.merged::boolean as pr_merged,
        payload:pull_request.mergeable::boolean as pr_mergeable,
        payload:pull_request.comments::number as pr_comments,
        payload:pull_request.commits::number as pr_commits,
        payload:pull_request.additions::number as pr_additions,
        payload:pull_request.deletions::number as pr_deletions,
        payload:pull_request.changed_files::number as pr_changed_files,
        
        -- Base and Head branches
        payload:pull_request.base.ref::varchar as base_branch,
        payload:pull_request.head.ref::varchar as head_branch,
        
        -- Labels
        payload:pull_request.labels as pr_labels,
        
        -- Metadata
        source_file,
        loaded_at
        
    from pull_request_events
)

select * from parsed
