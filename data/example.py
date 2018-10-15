from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "SSRF Example!"


@app.route("/ssrf")
def ssrf():
    # get response
    # do a curl
    # return content
    return

# FLASK_APP=hello.py flask run
# NOTE: this file should become a simple ssrf example in order to test SSRFmap