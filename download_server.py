#!/usr/bin/env python3
"""Servidor HTTP simples para descarregar os projetos guardados no DigitalWorks.

Lista os ficheiros de PROJECTS_DIR, permite descarregar cada um e
descarregar uma pasta inteira em ZIP (?zip). Se VNC_PASSWORD estiver
definida, pede autenticação básica (qualquer utilizador, essa senha).
"""
import base64
import html
import io
import os
import zipfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, unquote, urlsplit

ROOT = os.path.realpath(os.environ.get("PROJECTS_DIR", "/projetos"))
PORT = int(os.environ.get("DOWNLOAD_PORT", "6081"))
PASSWORD = os.environ.get("VNC_PASSWORD", "")


def inside_root(path):
    path = os.path.realpath(path)
    return path == ROOT or path.startswith(ROOT + os.sep)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def _authorized(self):
        if not PASSWORD:
            return True
        header = self.headers.get("Authorization", "")
        if header.startswith("Basic "):
            try:
                _, _, given = base64.b64decode(header[6:]).decode().partition(":")
                if given == PASSWORD:
                    return True
            except ValueError:
                pass
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Projetos"')
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def _real_path(self):
        """Caminho real pedido, ou None se sair de ROOT (ex.: via symlink)."""
        path = self.translate_path(self.path)
        return os.path.realpath(path) if inside_root(path) else None

    def do_HEAD(self):
        if self._authorized():
            super().do_HEAD()

    def do_GET(self):
        if not self._authorized():
            return
        path = self._real_path()
        if path is None:
            self.send_error(404)
            return
        if urlsplit(self.path).query == "zip" and os.path.isdir(path):
            self._send_zip(path)
            return
        super().do_GET()

    def _send_zip(self, folder):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, _, files in os.walk(folder):
                for name in files:
                    full = os.path.join(dirpath, name)
                    if not inside_root(full):
                        continue
                    zf.write(full, os.path.relpath(full, folder))
        data = buf.getvalue()
        name = os.path.basename(folder) if folder != ROOT else "projetos"
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition",
                         f"attachment; filename*=UTF-8''{quote(name)}.zip")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def list_directory(self, path):
        try:
            entries = sorted((n for n in os.listdir(path)
                              if inside_root(os.path.join(path, n))),
                             key=str.lower)
        except OSError:
            self.send_error(404)
            return None
        url_path = unquote(urlsplit(self.path).path)
        title = html.escape(url_path)
        rows = []
        if url_path != "/":
            rows.append('<li><a href="../">..</a></li>')
        for name in entries:
            full = os.path.join(path, name)
            is_dir = os.path.isdir(full)
            link = quote(name) + ("/" if is_dir else "")
            label = html.escape(name) + ("/" if is_dir else "")
            if is_dir:
                extra = f' &middot; <a href="{link}?zip">ZIP</a>'
            else:
                extra = f" <small>({os.path.getsize(full):,} bytes)</small>"
            rows.append(f'<li><a href="{link}">{label}</a>{extra}</li>')
        if not entries:
            rows.append("<li><em>(vazia)</em></li>")
        body = f"""<!doctype html>
<html lang="pt"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Projetos {title}</title>
<style>body{{font-family:sans-serif;max-width:50rem;margin:2rem auto;padding:0 1rem}}
li{{margin:.3rem 0}}</style></head>
<body><h1>Projetos {title}</h1>
<p><a href="?zip">Descarregar esta pasta em ZIP</a></p>
<ul>{''.join(rows)}</ul></body></html>""".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        return io.BytesIO(body)


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
