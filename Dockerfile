FROM ubuntu:24.04

# Evitar prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive

# Adicionar arquitetura i386 e instalar o Wine estável do repositório oficial do Ubuntu
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    wine \
    wine32 \
    wine64 \
    && rm -rf /var/lib/apt/lists/*

# Definir a pasta de trabalho dentro do container
WORKDIR /app

# Definir a variável de ambiente para o display (X11)
ENV DISPLAY=:0

# Escala da interface (96 = 100%, 144 = 150%, 192 = 200%)
ENV WINE_DPI=144

CMD ["sh", "-c", "wine reg add 'HKCU\\Control Panel\\Desktop' /v LogPixels /t REG_DWORD /d $WINE_DPI /f && wine DigitalWorks.exe"]
