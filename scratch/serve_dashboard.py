import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8080
DASHBOARD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dashboard'))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

def main():
    print(f"======================================================================")
    print(f"   [AI AGENT OS] VISUAL OPERATIONS CENTER DASHBOARD")
    print(f"======================================================================")
    print(f"  --> Serving dashboard from: '{DASHBOARD_DIR}'")
    print(f"  --> Opening URL: http://localhost:{PORT}")
    print(f"  --> Press Ctrl+C in terminal to stop server.")
    print(f"======================================================================\n")

    webbrowser.open(f"http://localhost:{PORT}")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Dashboard Server] Shutdown cleanly.")
            sys.exit(0)

if __name__ == "__main__":
    main()
