FROM apache/airflow:3.0.4-python3.11

# Install FAB provider and other providers
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
