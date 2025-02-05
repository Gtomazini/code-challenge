# Indicium Tech Code Challenge

Code challenge for Software Developer with focus in data projects.


# Instructions

docker compose build

cd ./meltano_etl_docker
docker build -t meu-meltano .

cd ..

cd ./docker-socket-proxy
docker build -t docker-socket-proxy:latest .

cd ..

Para ativar o projeto
docker-compose up -d

Para desativar o projeto
docker compose down

# Dúvidas
No processo não disse aonde inserir o video do google drive se era no relatorio, no e-mail ou no repositório.
