from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
dag_name = "northwind_meltano"

args = {
    'owner': 'gabriel',
    'start_date': datetime(2025, 2, 2)
}

dag = DAG(dag_name, schedule_interval="0 8 * * *", default_args=args)

with dag:
    
    #Task do postgre
    northwind_postgres = DockerOperator(
    task_id='northwind_postgres',
    image='meu-meltano',
    command='''bash -c "
        cd /meltano/demo-project &&
        if [ ! -f meltano.yml ]; then
            meltano init .
        fi &&
        
        # Capturar a data atual
        CURRENT_DATE=$(date +%Y-%m-%d) &&
        
        # Configurar o extrator
        meltano add extractor tap-postgres --variant meltanolabs &&
        meltano --environment=dev config tap-postgres set host northwind_db &&
        meltano --environment=dev config tap-postgres set port 5432 &&
        meltano --environment=dev config tap-postgres set user northwind_user &&
        meltano --environment=dev config tap-postgres set password thewindisblowing &&
        meltano --environment=dev config tap-postgres set database northwind &&
        meltano --environment=dev config tap-postgres set filter_schemas '[\\"public\\"]' &&
        
        # Descobrir e salvar o catálogo
        meltano invoke tap-postgres --discover > catalog.json &&
        
        # Criar diretórios apenas para as tabelas existentes
        mkdir -p output/postgres/orders/$CURRENT_DATE &&
        mkdir -p output/postgres/employees/$CURRENT_DATE &&
        mkdir -p output/postgres/customers/$CURRENT_DATE &&
        mkdir -p output/postgres/shippers/$CURRENT_DATE &&
        
        # Selecionar e extrair dados apenas das tabelas existentes
        meltano select tap-postgres public-orders &&
        meltano --environment=dev invoke tap-postgres > output/postgres/orders/$CURRENT_DATE/orders.json &&
        
        meltano select tap-postgres public-employees &&
        meltano --environment=dev invoke tap-postgres > output/postgres/employees/$CURRENT_DATE/employees.json &&
        
        meltano select tap-postgres public-customers &&
        meltano --environment=dev invoke tap-postgres > output/postgres/customers/$CURRENT_DATE/customers.json &&
        
        meltano select tap-postgres public-shippers &&
        meltano --environment=dev invoke tap-postgres > output/postgres/shippers/$CURRENT_DATE/shippers.json"
    ''',
    docker_url='tcp://docker-socket-proxy:2375',
    mounts=[
        Mount(
            target="/meltano/demo-project/output",
            source="/g/DataEngineering/code-challenge/data",
            type="bind"
        )
    ],
    mount_tmp_dir=False,
    network_mode='code-challenge_default',
    auto_remove=False
)
    # task do csv
    extract_csv = DockerOperator(
    task_id='extract_csv',
    image='meu-meltano',
    command='''bash -c "
        cd /meltano/demo-project &&
        if [ ! -f meltano.yml ]; then
            meltano init .
        fi &&
        
        # Adicionar extrator CSV
        meltano add extractor tap-csv --variant meltanolabs &&
        
        # Debug: Tentar ler o arquivo CSV primeiro
        echo 'Verificando primeiras linhas do CSV:' &&
        head -n 5 /meltano/demo-project/input/order_details.csv &&
        
        # Configurar o tap-csv com as colunas exatas do arquivo
        meltano config tap-csv set files '[{
            \\"entity\\": \\"order_details\\",
            \\"path\\": \\"/meltano/demo-project/input/order_details.csv\\",
            \\"keys\\": [\\"order_id\\", \\"product_id\\", \\"unit_price\\", \\"quantity\\", \\"discount\\"]
        }]' &&
        
        # Criar diretório do dia atual
        mkdir -p output/csv/$(date +%Y-%m-%d) &&
        
        # Extrair dados do CSV para JSON
        meltano invoke tap-csv > output/csv/$(date +%Y-%m-%d)/order_details.json"
    ''',
    docker_url='tcp://docker-socket-proxy:2375',
    mounts=[
        Mount(
            target="/meltano/demo-project/output",
            source="/g/DataEngineering/code-challenge/data",
            type="bind"
        ),
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
# série
northwind_postgres >> extract_csv
