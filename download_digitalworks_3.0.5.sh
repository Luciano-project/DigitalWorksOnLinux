#!/bin/sh
# Descarrega o DigitalWorks 3.0.5 e coloca os ficheiros em $APP_DIR (padrão: /app).
set -e

APP_DIR="${APP_DIR:-/app}"
URL="https://www.mecanique.co.uk/software/digital-works.zip"
TMP="$(mktemp -d)"

wget -q -O "$TMP/dw.zip" "$URL"
unzip -q "$TMP/dw.zip" -d "$TMP"
mkdir -p "$APP_DIR"
cp -a "$TMP/DigitalWorks/." "$APP_DIR/"
rm -rf "$TMP"
