[app]

# Título exibido no celular
title = IngreSense

# Nome do pacote (padrão Android: domínio invertido)
package.name = ingresense
package.domain = br.com.ingresense

# Arquivo principal
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json

# Pastas a incluir no APK
source.include_patterns = assets/*,assets/images/*,layouts/*.kv,config/*.py,screens/*.py,services/*.py,utils/*.py

# Versão do app
version = 1.0.0

# Dependências Python
requirements = python3,kivy==2.3.0,requests,certifi,charset-normalizer,idna,urllib3,plyer

# python-for-android fixado para evitar builds com Python alvo mais novo
# que o Kivy 2.3.0 ainda nao compila corretamente.
p4a.branch = v2024.01.21

# Orientação da tela
orientation = portrait

# Tela cheia (sem barra de status)
fullscreen = 0

# Ícone e splash (coloque os arquivos em assets/images/ e ajuste os caminhos)
# icon.filename = %(source.dir)s/assets/images/icon.png
# presplash.filename = %(source.dir)s/assets/images/presplash.png

# Cor do presplash (enquanto o app carrega)
android.presplash_color = #F0EEEA

# Permissões necessárias
android.permissions = INTERNET,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# API Android mínima e alvo
android.minapi = 21
android.api = 33
android.ndk = 25b

# Arquitetura (cobre a maioria dos Android modernos)
android.archs = arm64-v8a, armeabi-v7a

# Aceitar automaticamente as licenças do SDK Android
android.accept_sdk_license = True

# Dependencias Gradle adicionais.
# Manter comentado enquanto nao houver dependencias Android nativas; uma chave
# vazia gera "implementation ''" e quebra o assembleDebug.
# android.gradle_dependencies =

# Log level do Buildozer (0=erro, 1=info, 2=debug)
log_level = 2

[buildozer]

# Diretório onde o Buildozer armazena o SDK/NDK (não commitar)
android.sdk_path = ~/.buildozer/android/platform/android-sdk
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
