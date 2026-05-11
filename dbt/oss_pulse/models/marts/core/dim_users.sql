{{
    config(
        materialized='table',
        unique_key='user_key'
    )
}}

with users_dedup as (
    select
        actor_id,
        actor_login,
        actor_display_login,
        actor_url,
        row_number() over (partition by actor_id order by loaded_at desc) as rn
    from {{ ref('stg_events') }}
    where actor_id is not null
),

users_latest as (
    select
        actor_id,
        actor_login,
        actor_display_login,
        actor_url
    from users_dedup
    where rn = 1
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['actor_id']) }} as user_key,
        actor_id as user_id,
        actor_login as login,
        actor_display_login as display_login,
        actor_url as url,
        current_timestamp() as created_at,
        current_timestamp() as updated_at
    from users_latest
)

select * from final
