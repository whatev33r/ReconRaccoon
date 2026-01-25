#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import requests
import urllib3

from ReconRaccoon.src.framework import cli, functions

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.adapters.DEFAULT_RETRIES = 100


SEC_HEADERS = [
    "X-XSS-Protection",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Permitted-Cross-Domain-Policies",
    "Referrer-Policy",
    "Expect-CT",
    "Permissions-Policy",
    "Cross-Origin-Embedder-Policy",
    "Cross-Origin-Resource-Policy",
    "Cross-Origin-Opener-Policy",
]

INFO_HEADERS = [
    "X-Powered-By",
    "Server",
    "X-AspNet-Version",
    "X-AspNetMvc-Version",
]

CACHE_HEADERS = [
    "Cache-Control",
    "Pragma",
    "Last-Modified",
    "Expires",
    "ETag",
]


# Class for HTTP checks
class ShcheckWorker:
    def __init__(self, timeout, headers, verbose, follow_redirect):
        self.timeout = timeout
        self.headers = headers
        self.verbose = verbose
        self.follow_redirect = follow_redirect

    # Perform HTTP request and return list of output lines
    def request_target(self, target):
        output = []
        missing_sec_headers = []

        sesh = requests.session()
        sesh.keep_alive = False

        try:
            r = sesh.get(
                target,
                allow_redirects=self.follow_redirect,
                verify=False,
                timeout=self.timeout,
                headers=self.headers,
            )

            code = r.status_code

            # Status line
            if 100 <= code < 200:
                output.append(f"{cli.blue}INFO{cli.endc} - {r.url} [{cli.blue}{code}{cli.endc}]")
            elif 200 <= code < 300:
                output.append(f"{cli.green}SUCCESS{cli.endc} - {r.url} [{cli.green}{code}{cli.endc}]")
            elif 300 <= code < 400:
                location = r.headers.get("location", "N/A")
                output.append(f"{cli.yellow}REDIRECTION{cli.endc} - {r.url} [{cli.yellow}{code}{cli.endc}] → {location}")
            elif 400 <= code < 500:
                output.append(f"{cli.purple}CLIENT_ERROR{cli.endc} - {r.url} [{cli.purple}{code}{cli.endc}]")
            elif 500 <= code < 600:
                output.append(f"{cli.red}SERVER_ERROR{cli.endc} - {r.url} [{cli.red}{code}{cli.endc}]")

            # Info headers
            for head in INFO_HEADERS:
                val = r.headers.get(head)
                if val:
                    output.append(f"├─{cli.blue}[*]{cli.endc} {head}: {val}")

            # Security headers
            for head in SEC_HEADERS:
                val = r.headers.get(head)
                if val:
                    output.append(f"├─{cli.green}[+]{cli.endc} Header {cli.green}{head}{cli.endc} is present! (Value: {val})")
                else:
                    missing_sec_headers.append(head)
                    output.append(f"├─{cli.yellow}[!]{cli.endc} Missing security header: {cli.yellow}{head}{cli.endc}")

            # Cache headers
            for head in CACHE_HEADERS:
                val = r.headers.get(head)
                if val:
                    output.append(f"├─{cli.white}[~]{cli.endc} Cache control header {cli.white}{head}{cli.endc} is present! (Value: {val})")

            # Summary of missing security headers
            output.append(f"└─ Missing {cli.bold}{len(missing_sec_headers)}{cli.endc} security headers...\n")

        except requests.exceptions.ConnectTimeout:
            msg = f"{cli.red}TIMEOUT{cli.endc} - {target} [{cli.red}after {self.timeout}/s{cli.endc}]"
            output.append(msg)
            if self.verbose:
                output.append(f"{cli.yellow}[VERBOSE]{cli.endc} Connection timed out.")

        except requests.exceptions.ConnectionError as e:
            msg = f"{cli.red}ERROR{cli.endc} - {target} [{cli.red}ConnectionError{cli.endc}]"
            output.append(msg)
            if self.verbose:
                output.append(f"{cli.yellow}[VERBOSE]{cli.endc} Exception details: {e}")

        except Exception as e:
            msg = f"{cli.red}ERROR{cli.endc} - {target} [{cli.red}{e}{cli.endc}]"
            output.append(msg)
            if self.verbose:
                output.append(f"{cli.yellow}[VERBOSE]{cli.endc} Unexpected exception.")

        return output


# Init
def __init__():
    parser = argparse.ArgumentParser(
        prog="reconraccoon.py shcheck",
        description="Shcheck Module",
    )
    parser.add_argument(
        "-t", "--target",
        dest="target",
        type=str,
        required=True,
        help="Target URLs or IPs (str/file)",
    )
    parser.add_argument(
        "-r", "--request-timeout",
        dest="timeout",
        type=float,
        default=1.0,
        help="Timeout for all HTTP requests (default=1.0)",
    )
    parser.add_argument(
        "-a", "--active-threads",
        dest="threads",
        type=int,
        default=30,
        help="Threads for all HTTP requests (default=30)",
    )
    parser.add_argument(
        "-u", "--user-agent",
        dest="user_agent",
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        type=str,
        help="Custom User-Agent header",
    )
    parser.add_argument(
        "-f", "--follow-redirects",
        action="store_true",
        help="Follow HTTP redirects",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display verbose debugging output (timeouts/errors)",
    )
    # Call main function
    args, sysargs = parser.parse_known_args()
    main(args)


# Main
def main(args):
    targets = functions.check_prefix(args.target, None)

    worker = ShcheckWorker(
        timeout=args.timeout,
        headers={"User-Agent": args.user_agent},
        verbose=args.verbose,
        follow_redirect=args.follow_redirects,
    )

    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(worker.request_target, url) for url in targets]

            with tqdm(total=len(futures), unit=" requests", dynamic_ncols=True, leave=True) as pbar:
                for future in as_completed(futures):
                    for line in future.result():
                        tqdm.write(line)
                    pbar.update(1)
    except KeyboardInterrupt:
        print(f"{cli.red}leaving..{cli.endc}")
        exit(0)

