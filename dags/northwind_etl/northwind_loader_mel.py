from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
dag_name = "northwind_loader"

args = {
    'owner': 'gabriel',
    'start_date': datetime(2025, 2, 2),
}

dag = DAG(dag_name, schedule_interval="@daily", default_args=args)

with dag:
    
   load_postgres = DockerOperator(
    task_id='load_postgres',
    image='meu-meltano',
    command='''bash -c '
        set -x
        set -e
        
        cd /meltano/demo-project &&
        
        # Instala postgresql-client
        apt-get update && apt-get install -y postgresql-client jq &&
        
        # Cria a tabela final com os tipos corretos
        echo "Criando tabela final..." &&
        PGPASSWORD=thewindisblowing psql -h northwind_db -U northwind_user -d northwind -c "
            DROP TABLE IF EXISTS order_details;
            CREATE TABLE order_details (
                order_id SMALLINT,
                product_id SMALLINT,
                unit_price REAL,
                quantity SMALLINT,
                discount REAL
            );" &&
        
        # Processa o JSON e carrega no PostgreSQL usando COPY
        echo "Carregando dados..." &&
        cat /meltano/demo-project/input/csv/2025-02-05/order_details.json | \\
        jq -r "select(.type == \\"RECORD\\") | .record | [(.order_id|tonumber), (.product_id|tonumber), (.unit_price|tonumber), (.quantity|tonumber), (.discount|tonumber)] | @csv" | \\
        PGPASSWORD=thewindisblowing psql -h northwind_db -U northwind_user -d northwind -c "COPY order_details FROM STDIN WITH (FORMAT csv)" &&
        
        echo "Verificando dados carregados:" &&
        PGPASSWORD=thewindisblowing psql -h northwind_db -U northwind_user -d northwind -c "
            SELECT 
                pg_typeof(order_id) as order_id_type,
                pg_typeof(product_id) as product_id_type,
                pg_typeof(unit_price) as unit_price_type,
                pg_typeof(quantity) as quantity_type,
                pg_typeof(discount) as discount_type
            FROM order_details 
            LIMIT 1;
            
            SELECT COUNT(*) as total_records FROM order_details;
        "
    '
    ''',
    docker_url='tcp://docker-socket-proxy:2375',
    mounts=[
        Mount(
            target="/meltano/demo-project/input",
            source="/g/DataEngineering/code-challenge/data",
            type="bind"
        )
    ],
    mount_tmp_dir=False,
    network_mode='code-challenge_default',
    auto_remove=False
)