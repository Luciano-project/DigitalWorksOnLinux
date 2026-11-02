FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Wine + ecrã virtual + gestor de janelas + servidor VNC + noVNC
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    wine wine32 wine64 \
    xvfb xfonts-base openbox \
    x11vnc novnc websockify python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY start.sh download_server.py /usr/local/bin/
RUN chmod +x /usr/local/bin/start.sh /usr/local/bin/download_server.py

# Valores ajustáveis no docker run
ENV RESOLUTION=1280x800x24 \
    WINE_DPI=96 \
    PROJECTS_DIR=/projetos \
    DOWNLOAD_PORT=6081

EXPOSE 6080 6081

CMD ["/usr/local/bin/start.sh"]