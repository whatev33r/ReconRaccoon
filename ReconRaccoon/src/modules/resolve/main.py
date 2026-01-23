#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import requests
import urllib3
from collections import Counter

from ReconRaccoon.src.framework import cli, functions

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.adapters.DEFAULT_RETRIES = 100


class ResolveWorker:
    # Initialize the worker with request settings
    def __init__(self, timeout, headers, verbose, include_filter, exclude_filter, follow_redirect):
        self.timeout = timeout
        self.headers = headers
        self.verbose = verbose
        self.include_filter = include_filter
        self.exclude_filter = exclude_filter
        self.follow_redirect = follow_redirect
        self.counts = Counter()

    # Send request to a target and filter response
    def request_target(self, target):
        output = []

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
            lines, code_category = self.filter_response(r)
            output.extend(lines)
            if code_category:
                self.counts[code_category] += 1

        except requests.exceptions.ConnectTimeout:
            if self.verbose:
                output.append(
                    f"{cli.red}TIMEOUT{cli.endc} - {target} "
                    f"[{cli.red}after {self.timeout}/s{cli.endc}]"
                )

        except Exception as e:
            if self.verbose:
                output.append(
                    f"{cli.red}ERROR{cli.endc} - {target} "
                    f"[{cli.red}{e}{cli.endc}]"
                )

        return output

    # Filter the response based on include/exclude filters
    def filter_response(self, req):
        lines = []
        srv = f"({req.headers['server']})" if "server" in req.headers else ""
        code = req.status_code
        code_category = None

        def emit(label, color):
            lines.append(f"{color}{label}{cli.endc} - {req.url} [{color}{code}{cli.endc}] {srv}")

        # INCLUDE FILTER MODE
        if self.include_filter:
            if self.include_filter == "INFO" and 100 <= code < 200:
                emit("INFO", cli.blue)
                code_category = "INFO"
            elif self.include_filter == "SUCCESS" and 200 <= code < 300:
                emit("SUCCESS", cli.green)
                code_category = "SUCCESS"
            elif self.include_filter == "REDIRECTION" and 300 <= code < 400:
                location = req.headers.get("location", "N/A")
                lines.append(f"{cli.yellow}REDIRECTION{cli.endc} - {req.url} [{cli.yellow}{code}{cli.endc}] {srv} {cli.yellow}→{cli.endc} {location}")
                code_category = "REDIRECTION"
            elif self.include_filter == "CLIENT_ERROR" and 400 <= code < 500:
                emit("CLIENT_ERROR", cli.purple)
                code_category = "CLIENT_ERROR"
            elif self.include_filter == "SERVER_ERROR" and 500 <= code < 600:
                emit("SERVER_ERROR", cli.red)
                code_category = "SERVER_ERROR"
            return lines, code_category

        # EXCLUDE FILTER MODE
        if 100 <= code < 200 and self.exclude_filter != "INFO":
            emit("INFO", cli.blue)
            code_category = "INFO"
        elif 200 <= code < 300 and self.exclude_filter != "SUCCESS":
            emit("SUCCESS", cli.green)
            code_category = "SUCCESS"
        elif 300 <= code < 400 and self.exclude_filter != "REDIRECTION":
            location = req.headers.get("location", "N/A")
            lines.append(f"{cli.yellow}REDIRECTION{cli.endc} - {req.url} [{cli.yellow}{code}{cli.endc}] {srv} {cli.yellow}→{cli.endc} {location}")
            code_category = "REDIRECTION"
        elif 400 <= code < 500 and self.exclude_filter != "CLIENT_ERROR":
            emit("CLIENT_ERROR", cli.purple)
            code_category = "CLIENT_ERROR"
        elif 500 <= code < 600 and self.exclude_filter != "SERVER_ERROR":
            emit("SERVER_ERROR", cli.red)
            code_category = "SERVER_ERROR"

        return lines, code_category


# Init
def __init__():
    parser = argparse.ArgumentParser(
        prog="reconraccoon.py resolve",
        description="Resolve Module",
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
        help="Timeout for all http requests (default=1.0)",
    )
    parser.add_argument(
        "-a", "--active-threads",
        dest="threads",
        type=int,
        default=30,
        help="Threads for all http requests (default=30)",
    )
    parser.add_argument(
        "-u", "--user-agent",
        dest="user_agent",
        type=str,
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/109.0.0.0 Safari/537.36",
        help="Use custom user agent",
    )
    parser.add_argument(
        "-i", "--include-filter",
        dest="include_filter",
        choices=["INFO","SUCCESS","REDIRECTION","CLIENT_ERROR","SERVER_ERROR"],
        help="Include HTTP response type",
    )
    parser.add_argument(
        "-x", "--exclude-filter",
        dest="exclude_filter",
        choices=["INFO","SUCCESS","REDIRECTION","CLIENT_ERROR","SERVER_ERROR"],
        help="Exclude HTTP response type",
    )
    parser.add_argument(
        "-f", "--follow-redirects",
        action="store_true",
        help="Follow redirects",
    )
    parser.add_argument(
        "-c", "--common-ports",
        action="store_true",
        help="Check all common webserver ports (seclists)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
    )
    # Call main function
    args, sysargs = parser.parse_known_args()
    main(args)


# Main
def main(args):
    targets = functions.check_prefix(args.target, args.common_ports)
    worker = ResolveWorker(
        timeout=args.timeout,
        headers={"User-Agent": args.user_agent},
        verbose=args.verbose,
        include_filter=args.include_filter,
        exclude_filter=args.exclude_filter,
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
        # Print summary
        tqdm.write(f"\n{cli.bold}[SUMMARY]{cli.endc}")
        for cat in ["INFO", "SUCCESS", "REDIRECTION", "CLIENT_ERROR", "SERVER_ERROR"]:
            count = worker.counts.get(cat, 0)
            if count:
                tqdm.write(f"{cli.green}[+]{cli.endc} {cat}: {count}")
            else:
                tqdm.write(f"{cli.blue}[*]{cli.endc} {cat}: {count}")
    except KeyboardInterrupt:
        print(f"{cli.red} leaving..{cli.endc}")
        exit(0)

