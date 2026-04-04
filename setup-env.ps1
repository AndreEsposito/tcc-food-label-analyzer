# Script para configurar arquivos .env a partir dos templates
# Uso: .\setup-env.ps1

$BackendDir = "apps\backend"

Write-Host "🔧 Configurando arquivos .env a partir dos templates..." -ForegroundColor Cyan
Write-Host ""

# Setup .env.local
$envLocalPath = "$BackendDir\.env.local"
$envLocalTemplatePath = "$BackendDir\.env.local.template"

if (-not (Test-Path $envLocalPath)) {
    if (Test-Path $envLocalTemplatePath) {
        Copy-Item $envLocalTemplatePath $envLocalPath
        Write-Host "✅ .env.local criado a partir do template" -ForegroundColor Green
        Write-Host "⚠️  Edite $envLocalPath e configure as credenciais" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Arquivo .env.local.template não encontrado" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "ℹ️  $envLocalPath já existe" -ForegroundColor Blue
}

# Setup .env.production (opcional)
$envProdPath = "$BackendDir\.env.production"
$envProdTemplatePath = "$BackendDir\.env.production.template"

if (-not (Test-Path $envProdPath)) {
    Write-Host "ℹ️  $envProdPath não configurado" -ForegroundColor Blue
    Write-Host "   Para configurar: Copy-Item $envProdTemplatePath $envProdPath" -ForegroundColor Gray
} else {
    Write-Host "✅ $envProdPath já existe" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Setup concluído!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Configure as credenciais em $envLocalPath"
Write-Host "2. Adicione o arquivo google-credentials.json em $BackendDir\"
Write-Host "3. Execute: python -m uvicorn app.main:app"
