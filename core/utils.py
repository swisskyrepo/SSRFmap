def wrapper_file(data):
    return "file://{}".format(data)

def wrapper_gopher(data, ip, port):
    return "gopher://{}:{}/_{}".format(ip, port, data)

def wrapper_dict(data, ip, port):
    return "dict://{}:{}/{}".format(ip, port, data)

def wrapper_http(data, ip, port):
    return "http://{}:{}/{}".format(ip, port, data)

def wrapper_https(data, ip, port):
    return "http://{}:{}/{}".format(ip, port, data)


def diff_text(text1, text2):
    diff = ""
    for line in text1.split("\n"):
        if not line in text2:
            diff += line + "\n"
    return diff