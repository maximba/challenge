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
            bytes(f"Client connection from {self.client_address} to Gideon {self.server.sni}", "utf-8"))


class MxGideon(ThreadingHTTPServer):
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

    if "MX_certspath" in os.environ:
        prefix = os.environ["MX_certspath"] 
        keyfile = f'{prefix}/{domain_name}/key.pem'
        certfile = f'{prefix}/{domain_name}/cert.pem'
    else:
        prefix = SECRET_PREFIX
        keyfile = f'{prefix}/key.pem'
        certfile = f'{prefix}/cert.pem'

    ca_root_file = f'{prefix}/root-ca.pem'

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
    https = MxGideon(key, cert, HttpsHandler, bind_port=8443, is_tls=True)
    http = MxGideon(key, cert, HttpHandler, bind_port=8080, is_tls=False, caroot=ca_root)
    print(f"Gideon started at https://{https.bind_address}:{https.bind_port}")
    print(f"Gideon started at http://{http.bind_address}:{http.bind_port}")

    try:
        run(http, https)
    except KeyboardInterrupt:
        pass

    https.server_close()
    http.server_close()
    print("Gideon stopped.")
