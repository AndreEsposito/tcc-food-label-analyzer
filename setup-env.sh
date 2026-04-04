#!/bin/bash

# Script para configurar arquivos .env a partir dos templates
# Uso: ./setup-env.sh

BACKEND_DIR="apps/backend"

echo "🔧 Configurando arquivos .env a partir dos templates..."

# Setup .env.local
if [ ! -f "$BACKEND_DIR/.env.local" ]; then
    if [ -f "$BACKEND_DIR/.env.local.template" ]; then
        cp "$BACKEND_DIR/.env.local.template" "$BACKEND_DIR/.env.local"
        echo "✅ .env.local criado a partir do template"
        echo "⚠️  Edite $BACKEND_DIR/.env.local e configure as credenciais"
    else
        echo "❌ Arquivo .env.local.template não encontrado"
        exit 1
    fi
else
    echo "ℹ️  $BACKEND_DIR/.env.local já existe"
fi

# Setup .env.production (opcional)
if ! grep -q "APP_ENV=production" "$BACKEND_DIR/.env.production" 2>/dev/null; then
    echo "ℹ️  .env.production não configurado"
    echo "   Para configurar: cp $BACKEND_DIR/.env.production.template $BACKEND_DIR/.env.production"
fi

echo ""
echo "✅ Setup concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure as credenciais em $BACKEND_DIR/.env.local"
echo "2. Adicione o arquivo google-credentials.json em $BACKEND_DIR/"
echo "3. Execute: python -m uvicorn app.main:app"
