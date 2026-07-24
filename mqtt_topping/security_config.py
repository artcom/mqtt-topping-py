import ssl


class SecurityConfig:

    def __init__(self, use_tls: bool, username: str, password: str, certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE):
        self.use_tls = use_tls
        self.username = username
        self.password = password
        self.certfile = certfile
        self.keyfile = keyfile
        self.cert_reqs = cert_reqs
