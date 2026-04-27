#!/bin/bash

# ==============================================================================
# SCRIPT DE DEPLOY AUTOMATIZADO COM TELEGRAM E LOGS
# ==============================================================================

# --- 1. CONFIGURAÇÕES ---
BASE_DIR="/home/yure/www/projeto-desenvolvimento-web-ifto"
ENV_FILE="$BASE_DIR/.env.deploy"
LOG_DIR="$BASE_DIR/logs"
LOGFILE="$LOG_DIR/deploy.log"

# Garante que a pasta de logs exista
mkdir -p "$LOG_DIR"

# --- 2. CARREGAR VARIÁVEIS DE AMBIENTE ---
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo "⚠️ Aviso: Arquivo .env.deploy não encontrado. Notificações do Telegram não funcionarão."
fi

# --- 3. FUNÇÕES AUXILIARES ---

# Função para adicionar Timestamp em cada linha do log
timestamp() {
  while read line; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line"
  done
}

# Função para enviar mensagem ao Telegram
send_telegram() {
    local message="$1"
    local type="$2" # pode ser "info" ou "error"

    # Verifica se tem token configurado
    if [[ -z "$TG_BOT_TOKEN" || -z "$TG_CHAT_ID" ]]; then
        return
    fi

    curl -s -X POST "https://api.telegram.org/bot$TG_BOT_TOKEN/sendMessage" \
        -d chat_id="$TG_CHAT_ID" \
        -d text="$message" \
        -d parse_mode="HTML" \
        -d disable_web_page_preview="true" > /dev/null
}

# Função executada em caso de ERRO (Trap)
handle_error() {
    echo "❌ ERRO CRÍTICO: O script foi interrompido."
    send_telegram "🚨 <b>FALHA NO DEPLOY!</b>%0A%0AO processo encontrou um erro e parou.%0A📂 <i>Verifique o log no servidor.</i>" "error"
}

# --- 4. PREPARAÇÃO DO AMBIENTE ---

# Ativa o handler de erro: Se qualquer comando falhar, roda handle_error
trap 'handle_error' ERR

# Redireciona toda a saída (stdout e stderr) para a função timestamp -> log e tela
exec > >(timestamp | tee -a "$LOGFILE") 2>&1

# Garante que o script pare imediatamente se um comando retornar erro
set -e

# --- 5. INÍCIO DO DEPLOY ---

echo "========================================"
echo "INICIANDO DEPLOY AUTOMATIZADO"
echo "========================================"

# Envia notificação de início
send_telegram "🚀 <b>Deploy Iniciado</b>%0A📦 Projeto: EletroService (Flask)" "info"

# Entra no diretório
cd "$BASE_DIR"

echo "⬇️ Puxando alterações do Git..."
git pull origin main

echo "🏗️ Reconstruindo containers do Docker Compose..."
send_telegram "🏗️ <b>Reconstruindo containers...</b>%0A📦 Projeto: EletroService" "info"
docker compose build

echo "🚀 Reiniciando serviços..."
send_telegram "🚀 <b>Reiniciando serviços...</b>%0A📦 Projeto: EletroService" "info"
docker compose up -d

echo "🗄️ Migrando Banco de Dados..."
send_telegram "🗄️ <b>Migrando Banco de Dados...</b>%0A📦 Projeto: EletroService" "info"
docker compose exec web flask db upgrade

echo "========================================"
echo "DEPLOY CONCLUÍDO COM SUCESSO"
echo "========================================"

# --- 6. FINALIZAÇÃO ---

# Remove o trap para não disparar erro na saída normal
trap - ERR

# Envia notificação de sucesso
send_telegram "✅ <b>Deploy Finalizado com Sucesso!</b>%0A✨ Sistema EletroService atualizado." "info"

exit 0