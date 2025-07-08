#!/usr/bin/env bash

# Script de build para o projeto ARQV1
echo "Iniciando build do projeto ARQV1..."

# Garante que o Python está no PATH
export PATH="/usr/local/bin:$PATH"

# Garante que o pip está instalado
echo "Garantindo que pip está instalado..."
python -m ensurepip --upgrade

# Atualiza o pip
echo "Atualizando pip..."
python -m pip install --upgrade pip

# Instala as dependências Python
echo "Instalando dependências..."
python -m pip install -r requirements.txt

# Verifica se as dependências foram instaladas corretamente
echo "Verificando instalação..."
python -c "import flask; import google.generativeai; import supabase; print('Dependências instaladas com sucesso!')"

echo "Build concluído com sucesso!"
