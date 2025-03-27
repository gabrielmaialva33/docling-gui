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
