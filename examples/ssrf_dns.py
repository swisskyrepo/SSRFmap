# NOTE example script heavily inspired from FCSC CTF 2024
# use this example to test the AXFR module
# dig @127.0.0.1 -p 53 example.lab AXFR

from dnslib.server import DNSServer, BaseResolver
from dnslib import RR, QTYPE, RCODE, A
from dns import resolver
import threading

DOMAINS = {
    "frontend.example.lab.": "10.10.10.10",
    "backend.example.lab.": "10.10.10.11",
    "secret_flag.example.lab.": "10.10.10.12",
    "test.example.lab.": "10.10.10.12"
}

class LocalDNS(BaseResolver):
    def resolve(self, request, handler):
        reply = request.reply()
        q = request.q

        print('', flush=True)

        if q.qtype == QTYPE.A and str(q.qname) in DOMAINS:
            reply.add_answer(RR(q.qname, QTYPE.A, rdata=A(DOMAINS[str(q.qname)])))
        elif q.qtype == QTYPE.A:
            default_resolver = resolver.Resolver()
            try:
                answers = default_resolver.resolve(str(q.qname), "A")
                for answer in answers:
                    reply.add_answer(RR(q.qname, QTYPE.A, rdata=A(answer.address)))
            except:
                reply.header.rcode = RCODE.NXDOMAIN
        elif q.qtype == QTYPE.AXFR and str(q.qname) == "example.lab.":
            for domain, ip in DOMAINS.items():
                reply.add_answer(RR(domain, QTYPE.A, rdata=A(ip)))
        else:
            reply.header.rcode = RCODE.NXDOMAIN

        return reply

def run_server(protocol):
    print(f"Server is running - {protocol}")
    resolver = LocalDNS()
    server = DNSServer(resolver, address="0.0.0.0", port=53, tcp=(protocol == "TCP"))
    server.start()

if __name__ == "__main__":
    threading.Thread(target=run_server, args=("TCP",)).start()
    threading.Thread(target=run_server, args=("UDP",)).start()
