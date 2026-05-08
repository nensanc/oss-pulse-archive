-- Create RAW.EVENTS table for GitHub Archive data
USE ROLE LOADER;
USE WAREHOUSE WH_LOADING;
USE DATABASE OSS_PULSE;
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS EVENTS (
    -- Raw JSON storage with metadata
    event_data VARIANT,
    file_name VARCHAR(500),
    file_row_number INTEGER,
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create a simple view to parse the JSON (we'll expand this in Sprint 2 with dbt)
CREATE OR REPLACE VIEW RAW.EVENTS_PARSED AS
SELECT
    event_data:id::VARCHAR AS event_id,
    event_data:type::VARCHAR AS event_type,
    event_data:actor::VARIANT AS actor,
    event_data:repo::VARIANT AS repo,
    event_data:payload::VARIANT AS payload,
    event_data:public::BOOLEAN AS is_public,
    event_data:created_at::TIMESTAMP_NTZ AS created_at,
    file_name,
    loaded_at
FROM RAW.EVENTS;
