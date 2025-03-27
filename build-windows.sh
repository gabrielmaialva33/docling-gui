#!/bin/bash

echo "===== Criando executável Windows do Docling GUI usando Docker ====="
echo

# Verificar se o Docker está instalado e em execução
if ! command -v docker &> /dev/null; then
    echo "ERRO: Docker não encontrado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Criar o arquivo Dockerfile
echo "Criando Dockerfile..."
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

# Instalar dependências necessárias
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    wine \
    wine64 \
    && rm -rf /var/lib/apt/lists/*

# Definir variáveis de ambiente
ENV WINEARCH=win64
ENV WINEDEBUG=-all

# Instalar Python para Windows
RUN wget https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe && \
    wine python-3.10.11-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 && \
    rm python-3.10.11-amd64.exe

# Atualizar pip e instalar PyInstaller no Windows
RUN wine pip install --upgrade pip pyinstaller

# Diretório de trabalho
WORKDIR /app

# Criar um script para processar o build
RUN echo '#!/bin/bash\n\
echo "Copiando arquivos do projeto..."\n\
cp -r /src/* /app/\n\
\n\
echo "Verificando arquivos..."\n\
ls -la\n\
\n\
echo "Editando pyproject.toml para compatibilidade com PyInstaller..."\n\
sed -i "s/requires-python = \\">=3.9\\"/requires-python = \\">=3.9,<3.14\\"/g" pyproject.toml\n\
sed -i "s/python = \\">=3.10,<4.0\\"/python = \\">=3.10,<3.14\\"/g" pyproject.toml\n\
\n\
echo "Instalando dependências do projeto no Windows..."\n\
wine pip install -e .\n\
wine pip install docling\n\
\n\
echo "Criando executável com PyInstaller..."\n\
wine pyinstaller --name "Docling_GUI" --windowed --onefile \\\n\
  --hidden-import=docling \\\n\
  --hidden-import=docling.document_converter \\\n\
  --hidden-import=tkinter \\\n\
  docling-gui.py\n\
\n\
echo "Build completo. O executável está em /app/dist/"\n\
' > /build.sh && chmod +x /build.sh

# Comando padrão
CMD ["/build.sh"]
EOF

echo "Construindo a imagem Docker (isso pode levar alguns minutos)..."
docker build -t docling-windows-builder .

if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao construir a imagem Docker."
    exit 1
fi

echo "Executando o contêiner para criar o executável..."
docker run --rm -v "$(pwd):/src" docling-windows-builder

if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao executar o contêiner Docker."
    exit 1
fi

echo "Copiando o executável do contêiner..."
mkdir -p windows_exe
docker run --rm -v "$(pwd)/windows_exe:/output" docling-windows-builder cp -r /app/dist/* /output/

echo
echo "O executável Windows foi criado na pasta 'windows_exe'."
echo

# Limpar recursos temporários
read -p "Deseja remover a imagem Docker criada? (s/n): " resposta
if [[ $resposta == "s" || $resposta == "S" ]]; then
    docker rmi docling-windows-builder
    echo "Imagem Docker removida."
fi