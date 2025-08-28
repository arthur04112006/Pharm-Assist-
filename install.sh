#!/bin/bash

# Sistema de Triagem Farmacêutica - Script de Instalação
# Este script instala todas as dependências e configura o sistema

echo "🏥 Sistema de Triagem Farmacêutica - Instalação"
echo "================================================"

# Verificar se Python 3.8+ está instalado
echo "🔍 Verificando versão do Python..."
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detectado"

# Verificar se pip está instalado
echo "🔍 Verificando pip..."
python3 -m pip --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ pip não encontrado. Instale pip primeiro."
    exit 1
fi
echo "✅ pip detectado"

# Criar ambiente virtual (opcional)
echo "🔍 Criando ambiente virtual..."
python3 -m venv venv
if [ $? -eq 0 ]; then
    echo "✅ Ambiente virtual criado"
    echo "🔧 Ativando ambiente virtual..."
    source venv/bin/activate
    echo "✅ Ambiente virtual ativado"
else
    echo "⚠️  Não foi possível criar ambiente virtual, continuando com instalação global"
fi

# Instalar dependências
echo "📦 Instalando dependências Python..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# Verificar MySQL
echo "🔍 Verificando MySQL..."
mysql --version > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ MySQL detectado"
    echo "🔧 Configurando banco MySQL..."
    
    # Tentar conectar ao MySQL
    mysql -u root -e "SELECT 1" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Conectado ao MySQL como root"
        echo "🔧 Criando banco de dados..."
        mysql -u root < database/schema.sql
        if [ $? -eq 0 ]; then
            echo "✅ Banco MySQL configurado com sucesso"
        else
            echo "⚠️  Erro ao configurar MySQL, o sistema usará SQLite"
        fi
    else
        echo "⚠️  Não foi possível conectar ao MySQL como root"
        echo "   O sistema usará SQLite como alternativa"
    fi
else
    echo "⚠️  MySQL não detectado, o sistema usará SQLite"
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p uploads reports templates
echo "✅ Diretórios criados"

# Configurar arquivo .env
echo "⚙️  Configurando variáveis de ambiente..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ Arquivo .env criado (ajuste as configurações se necessário)"
else
    echo "✅ Arquivo .env já existe"
fi

# Dar permissões de execução
echo "🔧 Configurando permissões..."
chmod +x run.py
chmod +x install.sh
echo "✅ Permissões configuradas"

echo ""
echo "🎉 Instalação concluída com sucesso!"
echo ""
echo "📱 Para executar o sistema:"
echo "   python3 run.py"
echo ""
echo "🌐 O sistema abrirá automaticamente em: http://localhost:5000"
echo ""
echo "📚 Para mais informações, consulte o README.md"
echo ""
echo "================================================"
