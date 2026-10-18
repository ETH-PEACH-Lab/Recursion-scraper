"""Start a local HTTP server for the output/ directory."""
import http.server
import socketserver
import os
import webbrowser

PORT = 8888
os.chdir("output")

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}/")
    print(f"  Review (EN): http://localhost:{PORT}/review.html")
    print(f"  Review (CN): http://localhost:{PORT}/review_cn.html")
    print(f"  Curated (EN): http://localhost:{PORT}/index.html")
    print(f"  Curated (CN): http://localhost:{PORT}/index_cn.html")
    print("Press Ctrl+C to stop.")
    webbrowser.open(f"http://localhost:{PORT}/review_cn.html")
    httpd.serve_forever()
