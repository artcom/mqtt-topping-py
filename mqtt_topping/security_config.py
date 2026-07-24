import ssl


class SecurityConfig:

    def __init__(self, username: str, password: str, use_tls: bool = False, certfile: str = None, keyfile: str = None, cert_reqs: ssl.VerifyMode = ssl.CERT_NONE):
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.certfile = certfile
        self.keyfile = keyfile
        self.cert_reqs = cert_reqs
