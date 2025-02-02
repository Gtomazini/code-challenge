from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

dag_name = "northwind_meltano"

args = {
    'owner': 'gabriel',
    'start_date': datetime(2024, 1, 1)
}

dag = DAG(dag_name, schedule_interval="0 8 * * *", default_args=args)

with dag:
    
    extract_postgres = BashOperator(
        task_id='extract_postgres',
        bash_command='cd /opt/airflow/northwind-etl && meltano run tap-postgress target-parquet'
    )

    extract_csv = BashOperator(
        task_id='extract_csv',
        bash_command='cd /opt/airflow/northwind-etl && meltano run tap-csv target-parquet',
    )

    extract_postgres >> extract_csv