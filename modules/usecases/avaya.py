
import os
from suds.transport.http import HttpTransport
from suds.client import Client

class TransportWithCert(HttpTransport):

    def __init__(self, cert):
        super().__init__()
        self.cert = cert

    def u2open(self, u2request):
        import ssl
        return self.options._create_connection(
            ssl.create_default_context(cafile=None, capath=None, cadata=None),
            u2request
        )

    def send(self, request):
        request.headers["Authorization"] = None
        self.add_certificate_to_request(request)
        return super().send(request)

    def add_certificate_to_request(self, request):
        cert = os.path.expanduser(self.cert)
        if os.path.isfile(cert):
            request.headers["X-Client-Cert"] = open(cert, "rb").read().decode("ascii")
