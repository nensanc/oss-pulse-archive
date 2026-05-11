{{
    config(
        materialized='table',
        unique_key='repo_key'
    )
}}

with repos_dedup as (
    select 
        repo_id,
        repo_name,
        repo_url,
        row_number() over (partition by repo_id order by loaded_at desc) as rn
    from {{ ref('stg_events') }}
    where repo_id is not null
),

repos_latest as (
    select 
        repo_id,
        repo_name,
        repo_url
    from repos_dedup
    where rn = 1
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['repo_id']) }} as repo_key,
        repo_id,
        repo_name,
        repo_url,
        current_timestamp() as created_at,
        current_timestamp() as updated_at
    from repos_latest
)

select * from final
