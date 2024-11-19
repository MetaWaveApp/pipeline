FROM apache/airflow:2.7.1-python3.10

ARG AIRFLOW_USER_HOME=/usr/local/airflow

USER root
RUN mkdir -p ${AIRFLOW_USER_HOME}/dags ${AIRFLOW_USER_HOME}/logs ${AIRFLOW_USER_HOME}/plugins \
    && chown -R airflow: ${AIRFLOW_USER_HOME}

USER airflow

COPY . .

# RUN pip install --no-cache-dir pandas boto3

ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME} \
    PYTHONPATH=${AIRFLOW_USER_HOME}:/usr/local/lib/python3.10/site-packages

EXPOSE 8080

CMD ["airflow", "webserver"]