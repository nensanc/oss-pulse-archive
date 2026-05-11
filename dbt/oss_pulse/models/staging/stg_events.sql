{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='merge',
        on_schema_change='append_new_columns'
    )
}}

with source as (
    select * from {{ source('raw', 'events') }}
    
    {% if is_incremental() %}
    -- Only process new records on incremental runs
    where loaded_at > (select max(loaded_at) from {{ this }})
    {% endif %}
),

parsed as (
    select
        -- Event identifiers
        event_data:id::varchar as event_id,
        event_data:type::varchar as event_type,
        event_data:created_at::timestamp_ntz as created_at,
        
        -- Actor (user who triggered the event)
        event_data:actor.id::number as actor_id,
        event_data:actor.login::varchar as actor_login,
        event_data:actor.display_login::varchar as actor_display_login,
        event_data:actor.url::varchar as actor_url,
        
        -- Repository
        event_data:repo.id::number as repo_id,
        event_data:repo.name::varchar as repo_name,
        event_data:repo.url::varchar as repo_url,
        
        -- Organization (if exists)
        event_data:org.id::number as org_id,
        event_data:org.login::varchar as org_login,
        event_data:org.url::varchar as org_url,
        
        -- Payload (event-specific data - keeping as variant for now)
        event_data:payload as payload,
        
        -- Metadata
        event_data:public::boolean as is_public,
        
        -- Source tracking
        file_name as source_file,
        file_row_number as source_row_number,
        loaded_at
        
    from source
)

select * from parsed
