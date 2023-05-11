import select
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ssl
import os

SECRET_PREFIX = "/run/secrets/"


class HttpHandler(BaseHTTPRequestHandler):
    def log_request(self, code: int | str = ..., size: int | str = ...) -> None:
        pass

    def do_GET(self):
        if self.path == "/root_ca":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            with open(self.server.caroot) as k:
                self.wfile.write(bytes(k.read(), "utf-8"))
        else:
            self.send_response(400, "Only Request to /root_ca is allowed")
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes(f"Only Request to /root_ca is allowed", "utf-8"))


class HttpsHandler(BaseHTTPRequestHandler):
    def log_request(self, code=..., size=...) -> None:
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(
            bytes(f"Client connection from {self.client_address[0]} to server {self.server.sni}", "utf-8"))


class MxServer(ThreadingHTTPServer):
    def __init__(self, keyfile, certfile, reqh_class, bind_port, is_tls=False, caroot=None):
        self.keyfile = keyfile
        self.certfile = certfile
        self.bind_address = "0.0.0.0"
        self.bind_port = bind_port
        self.sni = None
        self.caroot = caroot
        self.is_https = is_tls
        super().__init__((self.bind_address, self.bind_port), RequestHandlerClass=reqh_class)
        if self.is_https:
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.context.sni_callback = self.sni_callback
            self.context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
            self.socket = self.context.wrap_socket(self.socket)

    def sni_callback(self, _socket: ssl.SSLObject, sni: str, _context: ssl.SSLContext):
        self.sni = sni


def init_vars():
    if "MX_domain" in os.environ:
        domain_name = os.environ["MX_domain"]
    else:
        domain_name = "home.arpa"

    ca_root_file = SECRET_PREFIX
    if "MX_cafile" in os.environ:
        ca_root_file += os.environ["MX_cafile"]
    else:
        ca_root_file += "root-ca.pem"

    keyfile = SECRET_PREFIX
    if "MX_keyfile" in os.environ:
        keyfile += os.environ["MX_keyfile"]
    else:
        keyfile += "key.pem"

    certfile = SECRET_PREFIX
    if "MX_certfile" in os.environ:
        certfile += os.environ["MX_certfile"]
    else:
        certfile += "cert.pem"

    if "MX_certspath" in os.environ:
        if os.environ["MX_certspath"] != "":
            certfile = f'{os.environ["MX_certspath"]}/{certfile}'
            keyfile = f'{os.environ["MX_certspath"]}/{keyfile}'
            ca_root_file = f'{os.environ["MX_certspath"]}/{ca_root_file}'
    return domain_name, ca_root_file, keyfile, certfile


def run(s, ss):
    while True:
        r, w, e = select.select([s, ss], [], [], 0)
        if s in r:
            s.handle_request()
        if ss in r:
            ss.handle_request()


if __name__ == "__main__":
    domain, ca_root, key, cert = init_vars()
    https = MxServer(key, cert, HttpsHandler, bind_port=8443, is_tls=True)
    http = MxServer(key, cert, HttpHandler, bind_port=8080, is_tls=False, caroot=ca_root)
    print(f"Server started at https://{https.bind_address}:{https.bind_port}")
    print(f"Server started at http://{http.bind_address}:{http.bind_port}")

    try:
        run(http, https)
    except KeyboardInterrupt:
        pass

    https.server_close()
    http.server_close()
    print("Server stopped.")
