"""
DataMorph Studio - Web Application Server Runner
Starts the pure Python production HTTP server on port 8000.
"""

import sys
import webbrowser
from datamorph.api.app import create_app
from datamorph.utils.logger import get_logger

logger = get_logger("DataMorphServer")
PORT = 8000

def start_server():
    server = create_app(host="0.0.0.0", port=PORT)
    url_local = f"http://localhost:{PORT}"
    url_ip = f"http://127.0.0.1:{PORT}"
    logger.info(f"DataMorph Studio starting on {url_local} and {url_ip}")
    print(f"==================================================")
    print(f"  DATAMORPH STUDIO - ML PREPROCESSING PLATFORM    ")
    print(f"==================================================")
    print(f"  Localhost URL : {url_local}")
    print(f"  Direct IP URL : {url_ip}")
    print(f"  Login Portal  : {url_local}/login.html")
    print(f"  Username      : admin")
    print(f"  Password      : admin123")
    print(f"==================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        server.server_close()

if __name__ == "__main__":
    start_server()
