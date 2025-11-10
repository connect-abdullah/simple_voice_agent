#!/usr/bin/env python3
import http.server
import socketserver
from pathlib import Path

PORT = 3000
DIRECTORY = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Web frontend running at: http://localhost:{PORT}")
        print("Make sure backend is running on port 8000")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
