#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import asyncio
import uuid
from collections import Counter
from tqdm import tqdm
import aiodns

from ReconRaccoon.src.framework import cli, functions


class SubEnum:
    # Initialize class
    def __init__(self, target, wordlist, verbose, threads):
        self.target = target
        self.wordlist = self.load_wordlist(wordlist)
        self.verbose = verbose
        self.threads = threads

        self.resolver = None
        self.wildcard_ips = set()
        self.subs = []
        self.ips = []

    # Load and clean wordlist
    def load_wordlist(self, path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return list({line.strip().lower() for line in f if line.strip()})

    # Initialize resolver bound to the running loop
    async def init_resolver(self):
        loop = asyncio.get_running_loop()
        self.resolver = aiodns.DNSResolver(loop=loop)

    # Wildcard DNS detection using multiple probes
    async def detect_wildcard(self):
        fake_count = 6
        threshold = 2

        fake_subs = [
            f"{uuid.uuid4().hex[:10]}.{self.target}"
            for _ in range(fake_count)
        ]

        ips = []

        tqdm.write(
            f"{cli.blue}[$]{cli.endc} Running wildcard DNS probes ({fake_count})"
        )

        for fake in fake_subs:
            try:
                result = await self.resolver.query(fake, "A")
                resolved = [r.host for r in result]
                ips.extend(resolved)

                tqdm.write(
                    f"{cli.yellow}[~]{cli.endc} Probe {fake} → {', '.join(resolved)}"
                )
            except aiodns.error.DNSError:
                tqdm.write(
                    f"{cli.yellow}[~]{cli.endc} Probe {fake} → NXDOMAIN"
                )

        if not ips:
            tqdm.write(
                f"{cli.green}[+]{cli.endc} No wildcard DNS detected for {self.target}"
            )
            return

        counts = Counter(ips)
        self.wildcard_ips = {
            ip for ip, c in counts.items() if c >= threshold
        }

        if self.wildcard_ips:
            tqdm.write(
                f"{cli.yellow}[!]{cli.endc} Wildcard DNS detected for {self.target} → "
                f"{', '.join(self.wildcard_ips)}"
            )
        else:
            tqdm.write(
                f"{cli.green}[+]{cli.endc} No wildcard DNS detected for {self.target}"
            )

    # Resolve a single subdomain
    async def resolve_subdomain(self, sem, sub):
        dns = f"{sub}.{self.target}"

        async with sem:
            try:
                result = await self.resolver.query(dns, "A")
                for r in result:
                    return {
                        "host": dns,
                        "ip": r.host,
                        "wildcard": r.host in self.wildcard_ips,
                    }

            except aiodns.error.DNSError as e:
                if self.verbose:
                    tqdm.write(
                        f"{cli.red}[VERBOSE]{cli.endc} {dns} failed: {e}"
                    )
                return None

    # Main async runner
    async def run(self):
        await self.init_resolver()
        await self.detect_wildcard()

        sem = asyncio.Semaphore(self.threads)
        tasks = [
            self.resolve_subdomain(sem, sub)
            for sub in self.wordlist
        ]

        for coro in tqdm(
            asyncio.as_completed(tasks),
            total=len(tasks),
            unit=" requests",
            dynamic_ncols=True,
            leave=True,
        ):
            try:
                result = await coro
            except Exception as E:
                # CRITICAL FIX: consume Future exceptions
                if self.verbose:
                    tqdm.write(
                        f"{cli.red}[VERBOSE]{cli.endc} Task failed unexpectedly: {E}"
                    )
                continue

            if not result:
                continue

            host = result["host"]
            ip = result["ip"]
            wildcard = result["wildcard"]

            if wildcard:
                if self.verbose:
                    tqdm.write(
                        f"{cli.yellow}[WILDCARD]{cli.endc} {host}\tIP: {ip}"
                    )
                continue

            tqdm.write(
                f"{cli.green}[+]{cli.endc} Hostname: {host}\tIP: {ip}"
            )
            self.subs.append(host)
            self.ips.append(ip)

        self.print_summary()

    # Summary output
    def print_summary(self):
        tqdm.write(f"\n{cli.bold}[SUMMARY]{cli.endc}")
        tqdm.write(
            f"{cli.green}[+]{cli.endc} Total real subdomains: {len(self.subs)}"
        )

        if self.wildcard_ips:
            tqdm.write(
                f"{cli.yellow}[!]{cli.endc} Wildcard IPs detected: "
                f"{', '.join(self.wildcard_ips)}"
            )
        else:
            tqdm.write(
                f"{cli.green}[+]{cli.endc} No wildcard IPs detected"
            )


# Init
def __init__():
    parser = argparse.ArgumentParser(
        prog="reconraccoon.py subenum",
        description="Subdomain Enumeration Module",
    )

    parser.add_argument(
        "-t", "--target",
        required=True,
        help="Target Domain (str/file)",
    )
    parser.add_argument(
        "-w", "--wordlist",
        default="resources/subdomains-top1million-20000.txt",
        help="Path to Wordlist (file)"
    )
    parser.add_argument(
        "-a", "--active-threads",
        type=int,
        default=30,
        help="Threads for all DNS requests (default=30)",
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
    try:
        targets = functions.check_prefix(args.target, None)
        target = (
            targets[0]
            .replace("http://", "")
            .replace("https://", "")
            .strip("/")
        )
        sub_enum = SubEnum(
            target=target,
            wordlist=args.wordlist,
            verbose=args.verbose,
            threads=args.active_threads,
        )
        asyncio.run(sub_enum.run())
    except KeyboardInterrupt:
        print(f"{cli.red}leaving..{cli.endc}")
        exit(0)

