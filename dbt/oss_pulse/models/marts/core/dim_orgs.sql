{{
    config(
        materialized='table',
        unique_key='org_key'
    )
}}

with orgs_distinct as (
    select distinct
        org_id,
        org_login,
        org_url
    from {{ ref('stg_events') }}
    where org_id is not null
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['org_id']) }} as org_key,
        org_id,
        org_login as login,
        org_url as url,
        current_timestamp() as created_at,
        current_timestamp() as updated_at
    from orgs_distinct
)

select * from final
