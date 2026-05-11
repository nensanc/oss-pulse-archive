{{
    config(
        materialized='incremental',
        unique_key='commit_event_key',
        incremental_strategy='merge',
        on_schema_change='append_new_columns'
    )
}}

with push_events as (
    select * from {{ ref('stg_events') }}
    where event_type = 'PushEvent'
    
    {% if is_incremental() %}
    and loaded_at > (select max(loaded_at) from {{ this }})
    {% endif %}
),

commits_flattened as (
    select
        event_id,
        created_at,
        actor_id,
        actor_login,
        repo_id,
        repo_name,
        org_id,
        org_login,
        commit.value:sha::varchar as commit_sha,
        commit.value:author.name::varchar as commit_author_name,
        commit.value:author.email::varchar as commit_author_email,
        commit.value:message::varchar as commit_message,
        commit.value:distinct::boolean as commit_distinct,
        payload:ref::varchar as branch_ref,
        payload:size::number as push_size,
        source_file,
        loaded_at
    from push_events,
    lateral flatten(input => payload:commits) commit
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['event_id', 'commit_sha']) }} as commit_event_key,
        commit_sha,
        event_id,
        created_at,
        actor_id,
        actor_login,
        repo_id,
        repo_name,
        org_id,
        org_login,
        commit_author_name,
        commit_author_email,
        commit_message,
        commit_distinct,
        branch_ref,
        push_size,
        source_file,
        loaded_at
    from commits_flattened
)

select * from final
