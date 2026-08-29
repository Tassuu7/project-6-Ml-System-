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
    server = create_app(port=PORT)
    url = f"http://localhost:{PORT}"
    logger.info(f"DataMorph Studio starting on {url}")
    print(f"==================================================")
    print(f"  DATAMORPH STUDIO - ML PREPROCESSING PLATFORM    ")
    print(f"==================================================")
    print(f"  Local URL  : {url}")
    print(f"  Login URL  : {url}/login.html")
    print(f"  Username   : admin")
    print(f"  Password   : admin123")
    print(f"==================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        server.server_close()

if __name__ == "__main__":
    start_server()
