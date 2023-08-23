#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from .src.framework import cli
from .src.framework import functions
# Custom Imports
import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor

# Disable Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.adapters.DEFAULT_RETRIES = 100


# Enumerate Host
def request_target(target, timeout, headers, verbose, include_filter, exclude_filter, follow_redirect):
    sesh = requests.session()
    sesh.keep_alive = False
    try:
        r = sesh.get(target, allow_redirects=follow_redirect, verify=False, timeout=timeout, headers=headers)
        filter_out(req=r, include=include_filter, exclude=exclude_filter)
    except requests.exceptions.ConnectTimeout:
        if verbose is True:
            print(f'{cli.red}TIMEOUT{cli.endc} - {target} [{cli.red}after {timeout}/s {cli.endc}]')
        return None
    except Exception as E:
        if verbose is True:
            print(f'{cli.red}ERROR{cli.endc} - {target} [{cli.red}{E}{cli.endc}]')
        return None


# Filter and output
def filter_out(req, exclude, include):
    if 'server' in req.headers:
        srv = f"({req.headers['server']})"
    else:
        srv = ""
    # Include
    if include is not None:
        if include == 'INFO' and req.status_code in range(100, 199):
            print(f'{cli.blue}INFO{cli.endc} - {req.url} [{cli.blue}{req.status_code}{cli.endc}] {srv}')
        elif include == 'SUCCESS' and req.status_code in range(200, 299):
            print(f'{cli.green}SUCCESS{cli.endc} - {req.url} [{cli.green}{req.status_code}{cli.endc}] {srv}')
        elif include == 'REDIRECTION' and req.status_code in range(300, 399):
            print(f'{cli.yellow}REDIRECTION{cli.endc} - {req.url} [{cli.yellow}{req.status_code}{cli.endc}] {srv} {cli.yellow}→{cli.endc} {req.headers["location"]}')
        elif include == 'CLIENT_ERROR' and req.status_code in range(400, 499):
            print(f'{cli.purple}CLIENT_ERROR{cli.endc} - {req.url} [{cli.purple}{req.status_code}{cli.endc}] {srv}')
        elif include == 'SERVER_ERROR' and req.status_code in range(500, 599):
            print(f'{cli.red}SERVER_ERROR{cli.endc} - {req.url} [{cli.red}{req.status_code}{cli.endc}] {srv}')
        else:
            pass
    # Exclude
    if include is None:
        if req.status_code in range(100, 199) and exclude != 'INFO':
            print(f'{cli.blue}INFO{cli.endc} - {req.url} [{cli.blue}{req.status_code}{cli.endc}] {srv}')
        elif req.status_code in range(200, 299) and exclude != 'SUCCESS':
            print(f'{cli.green}SUCCESS{cli.endc} - {req.url} [{cli.green}{req.status_code}{cli.endc}] {srv}')
        elif req.status_code in range(300, 399) and exclude != 'REDIRECTION':
            print(f'{cli.yellow}REDIRECTION{cli.endc} - {req.url} [{cli.yellow}{req.status_code}{cli.endc}] {srv} {cli.yellow}→{cli.endc} {req.headers["location"]}')
        elif req.status_code in range(400, 499) and exclude != 'CLIENT_ERROR':
            print(f'{cli.purple}CLIENT_ERROR{cli.endc} - {req.url} [{cli.purple}{req.status_code}{cli.endc}] {srv}')
        elif req.status_code in range(500, 599) and exclude != 'SERVER_ERROR':
            print(f'{cli.red}SERVER_ERROR{cli.endc} - {req.url} [{cli.red}{req.status_code}{cli.endc}] {srv}')
        else:
            pass


# Init
def __init__():
    parser = argparse.ArgumentParser(prog='ReconRaccoon.py resolve', description='Resolve Module')
    parser.add_argument('-t', '--target', dest='target', type=str, required=True, help='Target URLs or IPs (str/file)')
    parser.add_argument('-r', '--request-timeout', dest='timeout', type=float, default=1.0, help='Timeout for all http requests (default=1.0)')
    parser.add_argument('-a', '--active-threads', dest='threads', type=int, default=30, help='Threads for all http requests (default=30)')
    parser.add_argument('-u', '--user-agent', dest='user_agent', default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', type=str, help='Use custom user agent')
    parser.add_argument('-i', '--include-filter', dest='include_filter', type=str, choices=['INFO', 'SUCCESS', 'REDIRECTION', 'CLIENT_ERROR', 'SERVER_ERROR'], help='Include HTTP reponse type')
    parser.add_argument('-x', '--exclude-filter', dest='exclude_filter', type=str, choices=['INFO', 'SUCCESS', 'REDIRECTION', 'CLIENT_ERROR', 'SERVER_ERROR'], help='Exclude HTTP reponse type')
    parser.add_argument('-f', '--follow-redirects', action='store_true', help='Follow redirects')
    parser.add_argument('-c', '--common-ports', action='store_true', help='Check all common webserver ports (seclists)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Display verbose output (timeouts/errors)')
    args, sysargs = parser.parse_known_args()
    # Call main function
    main(args)


# Main
def main(args):
    # Prefix
    target = functions.check_prefix(args.target, args.common_ports)
    # Crawl
    try:
        threads = []
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            for url in target:
                threads.append(executor.submit(request_target, target=url, timeout=args.timeout, headers={'User-Agent': args.user_agent}, verbose=args.verbose, include_filter=args.include_filter, exclude_filter=args.exclude_filter, follow_redirect=args.follow_redirects))
    except KeyboardInterrupt:
        print(f'{cli.red} leaving..{cli.endc}')
        exit()
