# NOTE: do not try this at home - highly vulnerable ! (SSRF and RCE)
# NOTE: this file should become a simple ssrf example in order to test SSRFmap
# FLASK_APP=example.py flask run

from flask import Flask, abort, request 
import json
import re
import subprocess

app = Flask(__name__)

@app.route("/")
def hello():
    return "SSRF Example!"

# curl -i -X POST -d 'url=http://example.com' http://localhost:5000/ssrf
@app.route("/ssrf", methods=['POST'])
def ssrf():
    data = request.values
    content = command("curl {}".format(data.get('url')))
    return content

# curl -i -H "Content-Type: application/json" -X POST -d '{"url": "http://example.com"}' http://localhost:5000/ssrf2
@app.route("/ssrf2", methods=['POST'])
def ssrf2():
    data = request.json
    print(data)
    print(data.get('url'))
    content = command("curl {}".format(data.get('url')))
    return content

# curl -v "http://127.0.0.1:5000/ssrf3?url=http://example.com" 
@app.route("/ssrf3", methods=['GET'])
def ssrf3():
    data = request.values
    content = command("curl {}".format(data.get('url')))
    return content

# curl -X POST -H "Content-Type: application/xml" -d '<run><log encoding="hexBinary">4142430A</log><result>0</result><url>http://google.com</url></run>' http://127.0.0.1:5000/ssrf4
@app.route("/ssrf4", methods=['POST'])
def ssrf4():
    data = request.data
    print(data.decode())
    regex = re.compile("url>(.*?)</url")
    try:
        url = regex.findall(data.decode())[0]
        content = command("curl {}".format(url))
        return content
    except Exception as e:
        return e

def command(cmd):
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	return out

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
