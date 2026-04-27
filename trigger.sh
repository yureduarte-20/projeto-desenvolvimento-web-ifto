#!/bin/bash

# Caminho absoluto para o seu script de deploy real
DEPLOY_SCRIPT="/home/yure/www/projeto-desenvolvimento-web-ifto/deploy.sh"

# Verifica se o arquivo existe antes de tentar rodar
if [ -f "$DEPLOY_SCRIPT" ]; then
    # --- O TRUQUE MÁGICO ---
    # nohup: Impede que o processo morra quando o webhook fechar a conexão.
    # > /dev/null 2>&1: Joga a saída do terminal no lixo (pois seu script já salva log em arquivo).
    # &: Coloca em background (libera o webhook instantaneamente).
    nohup "$DEPLOY_SCRIPT" > /dev/null 2>&1 &

    echo "Comando de deploy disparado em background com sucesso!"
else
    echo "Erro: Script de deploy não encontrado em $DEPLOY_SCRIPT"
    exit 1
fi