import http.server
import socketserver
import os

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):

        if self.path.endswith(".m3u8"):
            self.send_header('Content-Type', 'application/vnd.apple.mpegurl')
        elif self.path.endswith(".ts"):
            self.send_header('Content-Type', 'video/MP2T')

        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

os.chdir("C:/GIT/PUC/projeto-micro/frontend/stream")  # Change to your folder containing .m3u8
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving HLS at http://localhost:{PORT}/")
    httpd.serve_forever()