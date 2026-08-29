"""
DataMorph Studio - Pure Python HTTP REST API Server
Implements HTTP request routing, CORS headers, JSON request/response processing,
and static frontend file serving with zero third-party framework dependencies.
"""

import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datamorph.storage.database import Database
from datamorph.api.auth_router import handle_login
from datamorph.api.dataset_router import handle_upload, handle_get_dataset
from datamorph.api.pipeline_router import handle_execute_pipeline
from datamorph.api.transform_router import handle_transform_preview
from datamorph.api.monitoring_router import handle_drift_analysis
from datamorph.api.export_router import handle_export
from datamorph.pipeline.registry import TransformerRegistry

DB = Database()


class DataMorphHTTPHandler(BaseHTTPRequestHandler):
    """Custom HTTP Request Handler for DataMorph Studio."""

    def _set_headers(self, status_code: int = 200, content_type: str = "application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/health":
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "healthy", "platform": "DataMorph Studio", "version": "2.4.0"}).encode())
        elif path == "/api/transformers":
            self._set_headers(200)
            self.wfile.write(json.dumps({"transformers": TransformerRegistry.list_all()}).encode())
        elif path == "/api/datasets" and "id" in query:
            code, res = handle_get_dataset(DB, query["id"][0])
            self._set_headers(code)
            self.wfile.write(json.dumps(res).encode())
        elif path == "/api/datasets":
            datasets = list(DB.get_all("datasets").values())
            self._set_headers(200)
            self.wfile.write(json.dumps({"datasets": datasets}).encode())
        else:
            # Serve Static Frontend Files
            self._serve_static(path)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_len)
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        if path == "/api/auth/login":
            code, res = handle_login(DB, body)
            self._set_headers(code)
            self.wfile.write(json.dumps(res).encode())
        elif path == "/api/datasets/upload":
            filename = body.get("filename", "upload.csv")
            content_str = body.get("content", "")
            code, res = handle_upload(DB, filename, content_str)
            self._set_headers(code)
            self.wfile.write(json.dumps(res).encode())
        elif path == "/api/pipeline/execute":
            code, res = handle_execute_pipeline(DB, body)
            self._set_headers(code)
            self.wfile.write(json.dumps(res).encode())
        elif path == "/api/transform/preview":
            code, res = handle_transform_preview(body)
            self._set_headers(code)
            self.wfile.write(json.dumps(res).encode())
        elif path == "/api/monitoring/drift":
            code, res = handle_drift_analysis(body)
            self._set_headers(code)
            self.wfile.write(json.dumps(res).encode())
        elif path == "/api/export":
            code, res = handle_export(body)
            self._set_headers(code)
            self.wfile.write(json.dumps(res).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": f"Endpoint '{path}' not found"}).encode())

    def _serve_static(self, path: str):
        if path == "/" or path == "/index.html":
            file_path = os.path.join("frontend", "index.html")
        elif path == "/login" or path == "/login.html":
            file_path = os.path.join("frontend", "login.html")
        else:
            file_path = os.path.join("frontend", path.lstrip("/"))

        if os.path.exists(file_path) and not os.path.isdir(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            mime_map = {
                ".html": "text/html",
                ".css": "text/css",
                ".js": "application/javascript",
                ".json": "application/json",
                ".svg": "image/svg+xml",
                ".png": "image/png"
            }
            content_type = mime_map.get(ext, "text/plain")
            with open(file_path, "rb") as f:
                content = f.read()
            self._set_headers(200, content_type)
            self.wfile.write(content)
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"404 Not Found")


def create_app(port: int = 8000) -> HTTPServer:
    server_address = ("", port)
    httpd = HTTPServer(server_address, DataMorphHTTPHandler)
    return httpd
