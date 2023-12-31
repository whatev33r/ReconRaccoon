#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Union

import requests
import urllib3

from ReconRaccoon.src.framework import cli, functions
from ReconRaccoon.src.framework.aws_proxy_hob import AWSProxyHob

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.adapters.DEFAULT_RETRIES = 100

USE_PROXIES = False
DEFAULT_REGEX = r'\b(?:https?://|http?://|www\.)[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)?'


def get_response(target, timeout, headers, verbose, follow_redirect) -> Union[requests.Response, None]:
    if USE_PROXIES:
        aws_proxy_hob = AWSProxyHob()
        sesh = aws_proxy_hob.get_proxy_session(target)
    else:
        sesh = requests.Session()
    sesh.keep_alive = False
    try:
        response = sesh.get(
            target,
            allow_redirects=follow_redirect,
            verify=False,
            timeout=timeout,
            headers=headers,
        )
        # Important to shutdown the gateway after each request to avoid charges
        if USE_PROXIES:
            aws_proxy_hob.shutdown_api_gateway()
        return response
    except requests.exceptions.ConnectTimeout:
        if verbose:
            print(
                f"{cli.red}TIMEOUT{cli.endc} - {target} [{cli.red}after {timeout}/s {cli.endc}]"
            )
        return None
    except Exception as e:
        if verbose:
            print(
                f"{cli.red}ERROR{cli.endc} - {target} [{cli.red}{e}{cli.endc}]")
        return None


def extract_links_from_html(response: requests.Response, regex: re.Pattern):
    body = response.content.decode("utf-8")
    return re.findall(regex, body, re.I)


def check_status_code(response: requests.Response):
    if response.status_code in range(100, 199):
        print(
            f"{cli.blue}INFO{cli.endc} - {response.url} [{cli.blue}{response.status_code}{cli.endc}]"
        )
    elif response.status_code in range(200, 299):
        print(
            f"{cli.green}SUCCESS{cli.endc} - {response.url} [{cli.green}{response.status_code}{cli.endc}]"
        )
    elif response.status_code in range(300, 399):
        print(
            f'{cli.yellow}REDIRECTION{cli.endc} - {response.url} [{cli.yellow}{response.status_code}{cli.endc}] {cli.yellow}→{cli.endc} {response.headers["location"]}'
        )
    elif response.status_code in range(400, 499):
        print(
            f"{cli.purple}CLIENT_ERROR{cli.endc} - {response.url} [{cli.purple}{response.status_code}{cli.endc}]"
        )
    elif response.status_code in range(500, 599):
        print(
            f"{cli.red}SERVER_ERROR{cli.endc} - {response.url} [{cli.red}{response.status_code}{cli.endc}]"
        )


def crawl(target, timeout, headers, verbose, follow_redirect, regex, depth=1, current_depth=1):
    if depth != 0 and current_depth > depth:
        return

    response = get_response(target, timeout, headers, verbose, follow_redirect)
    if response is not None:
        check_status_code(response)
        links = extract_links_from_html(response, regex)
        for link in links:
            print(f"├─[{cli.green}{link}{cli.endc}]")
        print(
            f"└─ Fetched {cli.bold}{len(links)}{cli.endc} paths at depth {current_depth} for {cli.bold}{target}{cli.endc}")

        if depth == 0 or current_depth < depth:
            links = extract_links_from_html(response, regex)
            for link in links:
                crawl(link, timeout, headers, verbose,
                      follow_redirect, regex, depth, current_depth + 1)


def __init__():
    parser = argparse.ArgumentParser(
        prog="reconraccoon.py crawl", description="Crawl Module"
    )
    parser.add_argument(
        "-t",
        "--target",
        dest="target",
        type=str,
        required=True,
        help="Target URLs or IPs (str/file)",
    )
    parser.add_argument(
        "-c",
        "--custom-regex",
        dest="regex",
        type=str,
        default=DEFAULT_REGEX,
        help=r"""Crawl request body for custom regex  (default="(?:href|src|action)=([^\s]*[\"|'])")""",
    )
    parser.add_argument(
        "-r",
        "--request-timeout",
        dest="timeout",
        type=float,
        default=1.0,
        help="Timeout for all http requests (default=1.0)",
    )
    parser.add_argument(
        "-a",
        "--active-threads",
        dest="threads",
        type=int,
        default=20,
        help="Threads for all http requests (default=20)",
    )
    parser.add_argument(
        "-u",
        "--user-agent",
        dest="user_agent",
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        type=str,
        help="Use custom user agent",
    )
    parser.add_argument(
        "-f", "--follow-redirects", action="store_true", help="Follow redirects"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display verbose output (timeouts/errors)",
    )
    parser.add_argument(
        "-d",
        "--depth",
        dest="depth",
        type=int,
        default=1,
        help="Depth for crawling (default=1, 0 for unlimited)",
    )
    args, sysargs = parser.parse_known_args()
    main(args)


def main(args):
    print(f"{cli.blue}[*]{cli.endc} Regex: {args.regex}, Depth: {args.depth}")
    target = functions.check_prefix(args.target, None)
    try:
        threads = []
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            for url in target:
                threads.append(
                    executor.submit(
                        crawl,
                        target=url,
                        timeout=args.timeout,
                        headers={"User-Agent": args.user_agent},
                        verbose=args.verbose,
                        follow_redirect=args.follow_redirects,
                        regex=args.regex,
                        depth=args.depth,
                    )
                )
    except KeyboardInterrupt:
        print(f"{cli.red} leaving..{cli.endc}")
        exit()
