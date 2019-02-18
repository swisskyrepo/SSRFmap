#!/usr/bin/python
from datetime import datetime
from core.ssrf import SSRF
import requests
import argparse
import logging
import re

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
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', action ='store', dest='reqfile', help="SSRF Request file")
    parser.add_argument('-p', action ='store', dest='param',   help="SSRF Parameter to target")
    parser.add_argument('-m', action ='store', dest='modules', help="SSRF Modules to enable")
    parser.add_argument('-l', action ='store', dest='handler', help="Start an handler for a reverse shell")
    parser.add_argument('--lhost', action ='store', dest='lhost',     help="LHOST reverse shell")
    parser.add_argument('--lport', action ='store', dest='lport',     help="LPORT reverse shell")
    parser.add_argument('--uagent',action ='store', dest='useragent', help="User Agent to use")
    parser.add_argument('--ssl',   action ='store', dest='ssl',       help="Use HTTPS without verification", nargs='?', const=True)
    parser.add_argument('--level', action ='store', dest='level',     help="Level of test to perform (1-5, default: 1)", nargs='?', const=1, default=1, type=int)
    results = parser.parse_args() 
    
    if results.reqfile == None:
        parser.print_help()
        exit()

    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s]:%(message)s')
    logging.addLevelName( logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
    display_banner()
    args = parse_args()
    ssrf = SSRF(args)