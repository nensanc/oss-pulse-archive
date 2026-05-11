{{
    config(
        materialized='table',
        unique_key='date_key'
    )
}}

with date_spine as (
    -- Generate dates from 2024-01-01 to 2026-12-31
    select
        dateadd(day, seq4(), '2024-01-01'::date) as date_day
    from table(generator(rowcount => 1096))  -- 3 years = ~1096 days
),

final as (
    select
        to_number(to_char(date_day, 'YYYYMMDD')) as date_key,
        date_day as date,
        year(date_day) as year,
        quarter(date_day) as quarter,
        month(date_day) as month,
        monthname(date_day) as month_name,
        day(date_day) as day,
        dayofweek(date_day) as day_of_week,
        dayname(date_day) as day_name,
        week(date_day) as week_of_year,
        case 
            when dayofweek(date_day) in (0, 6) then true 
            else false 
        end as is_weekend
    from date_spine
)

select * from final
