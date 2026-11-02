FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Wine + ecrã virtual + gestor de janelas + servidor VNC + noVNC
# (wget, unzip e ca-certificates servem para descarregar o DigitalWorks)
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    wine wine32 wine64 \
    xvfb xfonts-base openbox \
    x11vnc novnc websockify python3 \
    wget unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Descarrega o DigitalWorks para /app
COPY download_digitalworks_3.0.5.sh /tmp/
RUN sh /tmp/download_digitalworks_3.0.5.sh && rm /tmp/download_digitalworks_3.0.5.sh

COPY start.sh download_server.py /usr/local/bin/
RUN chmod +x /usr/local/bin/start.sh /usr/local/bin/download_server.py

# Valores ajustáveis no docker run
ENV RESOLUTION=1280x800x24 \
    WINE_DPI=96 \
    PROJECTS_DIR=/projetos \
    DOWNLOAD_PORT=6081

EXPOSE 6080 6081

CMD ["/usr/local/bin/start.sh"]