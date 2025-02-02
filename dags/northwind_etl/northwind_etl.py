import pandas as pd
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine


from airflow import DAG
from airflow.operators.python import PythonOperator


dag_name = "northwind_etl";

POSTGRES_CONN = os.getenv('POSTGRES_CONN')

args = {
    'owner' : 'gabriel',
    'start_date': datetime(2024, 1, 1)
}

dag = DAG(dag_name, schedule_interval="0 8 * * *", default_args=args)

def _lab_extrat_table_to_parquet(**kwargs):

    table_name = kwargs['params']['table_name']
    execution_date = kwargs['ds']

    print(f"table: {table_name}, date: {execution_date}")

    # database connect
    engine = create_engine(POSTGRES_CONN)

    # tabela > dataframe
    df = pd.read_sql(f"SELECT * FROM {table_name}", engine)

    print(f"Total records extracted: {len(df)}")
    print(f"Columns present: {', '.join(df.columns)}")

    # output directory
    output_dir = f"/opt/airflow/data/postgres/{table_name}/{execution_date}"
    os.makedirs(output_dir, exist_ok= True)

    # save parquet
    output_file = f"{output_dir}/{table_name}.parquet"
    df.to_parquet(output_file, index=False)

    print(f"Extraction saved successfully at: {output_file}")

    return f"Extracted {len(df)} records from {table_name}"


def _lab_extract_csv_to_parquet(**kwargs):

    execution_date = kwargs['ds']

    print(f"CSV extraction for date: {execution_date}")

    # read csv
    csv_path = "/opt/airflow/data/order_details.csv"
    df = pd.read_csv(csv_path)

    print(f"Total records extracted from CSV: {len(df)}")
    print(f"Columns present: {', '.join(df.columns)}")

    # output directory
    output_dir = f"/opt/airflow/data/csv/order_details/{execution_date}"
    os.makedirs(output_dir, exist_ok=True)

    # Saves parquet file

    output_file = f"{output_dir}/order_details.parquet"
    df.to_parquet(output_file, index=False)

    print(f"CSV data saved successfully at: {output_file}")

    return f"Extracted {len(df)} records from order_details.csv"


with dag:
    lab_extract_orders = PythonOperator(
        task_id='extract_orders',
        python_callable= _lab_extrat_table_to_parquet,
        provide_context = True,
        params = {
        'table_name': 'orders',
        }
    )

    lab_extract_orders_details = PythonOperator(
        task_id='extract_order_details',
        python_callable=_lab_extract_csv_to_parquet,
        provide_context = True
    )

    lab_extract_orders >> lab_extract_orders_details