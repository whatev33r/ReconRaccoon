#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from .src.framework import cli
from .src.framework import functions
# Custom Imports
import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor
import json

# Disable Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.adapters.DEFAULT_RETRIES = 100

# Security headers that should be enabled
sec_headers = [
    'X-XSS-Protection',
    'X-Frame-Options',
    'X-Content-Type-Options',
    'Strict-Transport-Security',
    'Content-Security-Policy',
    'X-Permitted-Cross-Domain-Policies',
    'Referrer-Policy',
    'Expect-CT',
    'Permissions-Policy',
    'Cross-Origin-Embedder-Policy',
    'Cross-Origin-Resource-Policy',
    'Cross-Origin-Opener-Policy'
]

information_headers = [
    'X-Powered-By',
    'Server',
    'X-AspNet-Version',
    'X-AspNetMvc-Version'
]

cache_headers = [
    'Cache-Control',
    'Pragma',
    'Last-Modified'
    'Expires',
    'ETag'
]


# Enumerate Host
def request_target(target, timeout, headers, verbose, follow_redirect):
    # Lists
    missing_sec_headers = []
    # Request sesh
    sesh = requests.session()
    sesh.keep_alive = False
    try:
        r = sesh.get(target, allow_redirects=follow_redirect, verify=False, timeout=timeout, headers=headers)
        if r.status_code in range(100, 199):
            print(f'{cli.blue}INFO{cli.endc} - {r.url} [{cli.blue}{r.status_code}{cli.endc}]')
        elif r.status_code in range(200, 299):
            print(f'{cli.green}SUCCESS{cli.endc} - {r.url} [{cli.green}{r.status_code}{cli.endc}]')
        elif r.status_code in range(300, 399):
            print(f'{cli.yellow}REDIRECTION{cli.endc} - {r.url} [{cli.yellow}{r.status_code}{cli.endc}] {cli.yellow}→{cli.endc} {r.headers["location"]}')
        elif r.status_code in range(400, 499):
            print(f'{cli.purple}CLIENT_ERROR{cli.endc} - {r.url} [{cli.purple}{r.status_code}{cli.endc}]')
        elif r.status_code in range(500, 599):
            print(f'{cli.red}SERVER_ERROR{cli.endc} - {r.url} [{cli.red}{r.status_code}{cli.endc}]')
        else:
            pass
        for head in information_headers:
            resp = r.headers.get(head)
            if resp:
                print(f'├─{cli.blue}[~]{cli.endc} {head}: {resp}')
        for head in sec_headers:
            resp = r.headers.get(head)
            if resp:
                print(f'├─{cli.green}[+]{cli.endc} Header {cli.green}{head}{cli.endc} is present! (Value: {resp})')
            else:
                print(f'├─{cli.yellow}[!]{cli.endc} Missing security header: {cli.yellow}{head}{cli.endc}')
                missing_sec_headers.append(head)
        for head in cache_headers:
            resp = r.headers.get(head)
            if resp:
                print(f'├─{cli.white}[*]{cli.endc} Cache control header {cli.white}{head}{cli.endc} is present! (Value: {resp})')
        print(f'└─ Missing {cli.bold}{len(missing_sec_headers)}{cli.endc} security headers...\n')
    except requests.exceptions.ConnectTimeout:
        if verbose is True:
            print(f'{cli.red}TIMEOUT{cli.endc} - {target} [{cli.red}after {timeout}/s {cli.endc}]')
        return None
    except Exception as E:
        if verbose is True:
            print(f'{cli.red}ERROR{cli.endc} - {target} [{cli.red}{E}{cli.endc}]')
        return None


# Init
def __init__():
    parser = argparse.ArgumentParser(prog='ReconRaccoon.py shcheck', description='Shcheck Module')
    parser.add_argument('-t', '--target', dest='target', type=str, required=True, help='Target URLs or IPs (str/file)')
    parser.add_argument('-r', '--request-timeout', dest='timeout', type=float, default=1.0, help='Timeout for all http requests (default=1.0)')
    parser.add_argument('-a', '--active-threads', dest='threads', type=int, default=30, help='Threads for all http requests (default=30)')
    parser.add_argument('-u', '--user-agent', dest='user_agent', default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', type=str, help='Use custom user agent')
    parser.add_argument('-f', '--follow-redirects', action='store_true', help='Follow redirects')
    parser.add_argument('-v', '--verbose', action='store_true', help='Display verbose output (timeouts/errors)')
    args, sysargs = parser.parse_known_args()
    # Call main function
    main(args)


# Main
def main(args):
    # Prefix
    target = functions.check_prefix(args.target, None)
    # Check header
    try:
        threads = []
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            for url in target:
                threads.append(executor.submit(request_target, target=url, timeout=args.timeout, headers={'User-Agent': args.user_agent}, verbose=args.verbose, follow_redirect=args.follow_redirects))
    except KeyboardInterrupt:
        print(f'{cli.red} leaving..{cli.endc}')
        exit()
