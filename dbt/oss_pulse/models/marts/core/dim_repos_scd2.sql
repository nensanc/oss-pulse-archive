{{
    config(
        materialized='table',
        unique_key='repo_key'
    )
}}

with repos_current as (
    select 
        repo_id,
        repo_name,
        repo_url,
        loaded_at as snapshot_date
    from {{ ref('stg_events') }}
    where repo_id is not null
    qualify row_number() over (partition by repo_id order by loaded_at desc) = 1
),

repos_historical as (
    -- Get existing historical records if table exists
    {% if is_incremental() %}
    select * from {{ this }}
    where is_current = false
    {% else %}
    select 
        null::varchar as repo_key,
        null::number as repo_id,
        null::varchar as repo_name,
        null::varchar as repo_url,
        null::timestamp_ntz as valid_from,
        null::timestamp_ntz as valid_to,
        null::boolean as is_current
    where 1=0
    {% endif %}
),

repos_with_scd as (
    select
        repo_id,
        repo_name,
        repo_url,
        snapshot_date as valid_from,
        '9999-12-31'::timestamp_ntz as valid_to,
        true as is_current
    from repos_current
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['repo_id', 'valid_from']) }} as repo_key,
        repo_id,
        repo_name,
        repo_url,
        valid_from,
        valid_to,
        is_current
    from repos_with_scd
    
    union all
    
    select * from repos_historical
)

select * from final
