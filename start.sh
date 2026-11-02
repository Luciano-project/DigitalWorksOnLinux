#!/bin/sh

set -e
export DISPLAY=:1

# 1. Ecrã virtual
Xvfb :1 -screen 0 "$RESOLUTION" &
sleep 1

# 2. Gestor de janelas (permite mover e redimensionar as janelas do programa)
openbox &

# 3. Servidor VNC, acessível apenas dentro do container
if [ -n "$VNC_PASSWORD" ]; then
  x11vnc -storepasswd "$VNC_PASSWORD" /root/.vncpass
  AUTH="-rfbauth /root/.vncpass"
else
  AUTH="-nopw"
fi
x11vnc -display :1 -forever -shared -localhost -rfbport 5900 -quiet $AUTH &

# 4. Ponte WebSocket + cliente web noVNC
websockify --web /usr/share/novnc 6080 localhost:5900 &

# 5. Escala do Wine e arranque do programa
wine reg add 'HKCU\Control Panel\Desktop' /v LogPixels /t REG_DWORD /d "$WINE_DPI" /f
exec wine DigitalWorks.exe
