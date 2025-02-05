# Imagem base leve
FROM python:3.10-slim

# Diretório principal
WORKDIR /meltano

# Instala dependências básicas
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instala o Meltano
RUN pip install --no-cache-dir meltano

# Define variável de ambiente para evitar problemas de reconhecimento do projeto
ENV MELTANO_PROJECT_ROOT=/meltano/demo-project

# Inicializa o projeto (se necessário)
RUN meltano init demo-project --force

# Define diretório do projeto
WORKDIR $MELTANO_PROJECT_ROOT

# Comando padrão: shell interativo
CMD ["bash"]