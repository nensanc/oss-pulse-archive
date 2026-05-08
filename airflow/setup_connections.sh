#!/bin/bash

# Setup AWS connection
docker-compose exec airflow-apiserver airflow connections add 'aws_default' \
    --conn-type 'aws' \
    --conn-extra "{
        \"region_name\": \"us-east-1\"
    }"

# Setup Snowflake connection
docker-compose exec airflow-apiserver airflow connections add 'snowflake_default' \
    --conn-type 'snowflake' \
    --conn-host 'XSGMXJC-LZC01736.snowflakecomputing.com' \
    --conn-login 'SVC_OSS_PULSE' \
    --conn-password 'OssPulsefergwfes-3r34t' \
    --conn-schema 'RAW' \
    --conn-extra "{
        \"account\": \"XSGMXJC-LZC01736\",
        \"warehouse\": \"WH_LOADING\",
        \"database\": \"OSS_PULSE\",
        \"role\": \"LOADER\",
        \"region\": \"us-east-1\"
    }"

echo "✅ Connections configured"
