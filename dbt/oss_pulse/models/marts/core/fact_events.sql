{{
    config(
        materialized='table',
        unique_key='event_key',
        cluster_by=['created_at', 'event_type']
    )
}}

with events as (
    select * from {{ ref('stg_events') }}
),

users as (
    select * from {{ ref('dim_users') }}
),

repos as (
    select * from {{ ref('dim_repos') }}
),

orgs as (
    select * from {{ ref('dim_orgs') }}
),

time_dim as (
    select * from {{ ref('dim_time') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['e.event_id']) }} as event_key,
        
        -- Foreign keys to dimensions
        u.user_key,
        r.repo_key,
        o.org_key,
        t.date_key,
        
        -- Event attributes
        e.event_id,
        e.event_type,
        e.created_at,
        e.is_public,
        
        -- Keep payload for detailed analysis
        e.payload,
        
        -- Metadata
        e.source_file,
        e.source_row_number,
        e.loaded_at
        
    from events e
    left join users u on e.actor_id = u.user_id
    left join repos r on e.repo_id = r.repo_id
    left join orgs o on e.org_id = o.org_id
    left join time_dim t on to_number(to_char(e.created_at, 'YYYYMMDD')) = t.date_key
)

select * from final
