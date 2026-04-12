FROM python:3.12-slim

# Argumentos para evitar problemas de permissão com volumes
ARG UID=1000
ARG USER=flaskuser

WORKDIR /app

# Instalar dependências necessárias e criar usuário/grupo correspondente ao host
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/* && \
    groupadd -g $UID $USER || true && \
    useradd -u $UID -g $UID -m $USER || true && \
    chown -R $USER:$USER /app

# Copiar requirements primeiro para aproveitar cache do docker
COPY --chown=$USER:$USER requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto da aplicação com a permissão correta
COPY --chown=$USER:$USER . .

# Expor a porta que o Flask vai rodar
EXPOSE 5000

# Variáveis de ambiente
ENV FLASK_APP=run.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0

# Alternar para o usuário não-root
USER $USER

# Comando para rodar a aplicação
CMD ["python", "run.py"]
