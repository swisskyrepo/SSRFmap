# NOTE: Do not try this at home - highly vulnerable ! (SSRF and RCE)
# NOTE: SSRF examples script
# FLASK_APP=example.py flask run

import re
import subprocess
import urllib.parse

from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def hello():
    return "SSRF Example!"


# curl -i -X POST -d 'url=http://example.com' http://localhost:5000/ssrf
@app.route("/ssrf", methods=["POST"])
def ssrf():
    data = request.values
    content = command(f"curl {data.get('url')}")
    return content


# curl -i -H "Content-Type: application/json" -X POST -d '{"url": "http://example.com"}' http://localhost:5000/ssrf2
@app.route("/ssrf2", methods=["POST"])
def ssrf2():
    data = request.json
    print(data)
    print(data.get("url"))
    content = command(f"curl {data.get('url')}")
    return content


# curl -v "http://127.0.0.1:5000/ssrf3?url=http://example.com"
@app.route("/ssrf3", methods=["GET"])
def ssrf3():
    data = request.values
    content = command(f"curl {data.get('url')}")
    return content


# curl -X POST -H "Content-Type: application/xml" -d '<run><log encoding="hexBinary">4142430A</log><result>0</result><url>http://google.com</url></run>' http://127.0.0.1:5000/ssrf4
@app.route("/ssrf4", methods=["POST"])
def ssrf4():
    data = request.data
    regex = re.compile("url>(.*?)</url")
    try:
        data = urllib.parse.unquote(data)
        url = regex.findall(data)[0]
        print(url)
        content = command(f"curl {url}")
        return content

    except Exception as e:
        print(e)


# curl -v "http://127.0.0.1:5000/ssrf5" -H 'X-Custom-Header: http://example.com'
@app.route("/ssrf5", methods=["GET"])
def ssrf5():
    data = request.headers.get("X-Custom-Header")
    content = command(f"curl {data}")
    return content


# curl -F 'url=http://example.com' -F 'proof=@README.md' http://127.0.0.1:5000/ssrf6
@app.route("/ssrf6", methods=["POST"])
def ssrf6():
    # Deliberately vulnerable: this endpoint exists only to reproduce SSRF
    # when the target URL is carried in a multipart/form-data field.
    url = request.form.get("url")
    content = command(f"curl {url}")
    return content


def command(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return out


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
