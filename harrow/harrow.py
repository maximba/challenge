import requests
from random import randrange
import os
import time


def random_server(prefix):
    return f"house{randrange(1, 9)}.{prefix}"


def init_vars():
    if "MX_domain" in os.environ:
        domain_name = os.environ["MX_domain"]
    else:
        domain_name = "home.arpa"

    ca_root_file = "root-ca.pem"
    return domain_name, ca_root_file


def create_session(ca_file):
    s = requests.Session()
    s.verify = ca_file
    return s


def client(session, domain, ca_file):
    url = random_server(domain)
    retcode = False
    try:
        response = session.get(f'https://{url}:8443/')
    except (requests.exceptions.SSLError, OSError) as err:
        print(f'Error. {err}')
        get_ca(url, ca_file)
    else:
        print(response.text)

def get_ca(url, ca_file):
    try:
        response = requests.get(f'http://{url}:8080/root_ca')
        if response.ok:
            custom_ca = response.content
            with open(ca_file, 'wb') as outfile:
                outfile.write(custom_ca)
    except requests.exceptions.RequestException as err:
        print(f'Request Error. {err}')

def run(session, domain, ca):
    while True:
        client(session, domain, ca)
        time.sleep(3)


if __name__ == "__main__":
    dom, caroot = init_vars()
    sess = create_session(caroot)
    try:
        run(sess, dom, caroot)
    except KeyboardInterrupt:
        sess.close()
        print("Harrow Stopped")
