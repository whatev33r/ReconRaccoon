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
    # Initialize class with target, wordlist, verbosity, concurrency, and output flag
    def __init__(self, target, wordlist, verbose, threads=500, write_output=False):
        self.target = target
        self.wordlist = self.filter_wordlist(wordlist)
        self.verbose = verbose
        self.threads = threads
        self.write_output_flag = write_output

        self.resolver = None
        self.wildcard_ips = set()
        self.subs = []
        self.ips = []

    # Load and clean wordlist
    def filter_wordlist(self, wordlist):
        with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
            words = {line.strip().lower() for line in f if line.strip()}
        return list(words)

    # Initialize async DNS resolver
    async def init_resolver(self):
        loop = asyncio.get_running_loop()
        self.resolver = aiodns.DNSResolver(loop=loop)

    # Detect wildcard DNS using multiple fake subdomains
    async def detect_wildcard(self):
        fake_count = 6
        threshold = 2  # Must appear ≥ threshold times to be considered wildcard

        fake_subs = [
            f"{uuid.uuid4().hex[:10]}.{self.target}" for _ in range(fake_count)
        ]

        ips = []

        for fake in fake_subs:
            try:
                result = await self.resolver.query(fake, "A")
                resolved_ips = [r.host for r in result]
                ips.extend(resolved_ips)
                tqdm.write(f"{cli.yellow}[~]{cli.endc} Wildcard probe {fake} → {', '.join(resolved_ips)}")
            except Exception as e:
                tqdm.write(f"{cli.yellow}[~]{cli.endc} Wildcard probe {fake} → NXDOMAIN / failed ({e})")

        if not ips:
            tqdm.write(f"{cli.green}[+]{cli.endc} No wildcard DNS detected for {self.target}")
            return

        counts = Counter(ips)
        self.wildcard_ips = {ip for ip, c in counts.items() if c >= threshold}

        if self.wildcard_ips:
            tqdm.write(f"{cli.yellow}[!]{cli.endc} Wildcard DNS detected for {self.target} → {', '.join(self.wildcard_ips)}")
        else:
            tqdm.write(f"{cli.green}[+]{cli.endc} No wildcard DNS detected for {self.target}")

    # Resolve a single subdomain
    async def resolve_subdomain(self, sem, sub):
        dns = f"{sub}.{self.target}"

        async with sem:
            try:
                result = await self.resolver.query(dns, "A")
                for r in result:
                    ip = r.host
                    is_wildcard = ip in self.wildcard_ips
                    return {"host": dns, "ip": ip, "wildcard": is_wildcard}
            except Exception as e:
                if self.verbose:
                    tqdm.write(f"{cli.red}[VERBOSE]{cli.endc} {dns} failed: {e}")
                return None

    # Main async runner
    async def run(self):
        await self.init_resolver()
        await self.detect_wildcard()

        sem = asyncio.Semaphore(self.threads)
        tasks = [self.resolve_subdomain(sem, sub) for sub in self.wordlist]

        for coro in tqdm(asyncio.as_completed(tasks),
                         total=len(tasks),
                         unit=" requests",
                         dynamic_ncols=True,
                         leave=True):
            result = await coro
            if result:
                host = result["host"]
                ip = result["ip"]
                wildcard = result["wildcard"]

                if wildcard:
                    if self.verbose:
                        tqdm.write(f"{cli.yellow}[WILDCARD]{cli.endc} {host}\tIP: {ip}")
                    continue  # skip normal output

                # Normal non-wildcard output
                tqdm.write(f"{cli.green}[+]{cli.endc} Hostname: {host}\tIP: {ip}")
                self.subs.append(host)
                self.ips.append(ip)

        if self.write_output_flag:
            self.write_outputs()
        self.print_summary()

    # Write results to output files
    def write_outputs(self):
        with open("subs.txt", "w") as f:
            for line in self.subs:
                f.write(f"{line}\n")

        with open("ips.txt", "w") as f:
            for line in self.ips:
                f.write(f"{line}\n")

    # Print summary at the end
    def print_summary(self):
        tqdm.write(f"\n{cli.bold}[SUMMARY]{cli.endc}")
        tqdm.write(f"{cli.green}[+]{cli.endc} Total real subdomains: {len(self.subs)}")
        if self.wildcard_ips:
            tqdm.write(f"{cli.yellow}[!]{cli.endc} Wildcard IPs detected: {', '.join(self.wildcard_ips)}")
        else:
            tqdm.write(f"{cli.green}[+]{cli.endc} No wildcard IPs detected")


# Init
def __init__():
    parser = argparse.ArgumentParser(
        prog="reconraccoon.py subenum",
        description="Subdomain Enumeration Module",
    )
    parser.add_argument(
        "-t", "--target",
        required=True,
    )
    parser.add_argument(
        "-w", "--wordlist",
        default="resources/subdomains-top1million-20000.txt",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
    )
    parser.add_argument(
        "-a", "--active-threads",
        type=int,
        default=500,
        help="Concurrent DNS queries",
    )
    parser.add_argument(
        "-o", "--output",
        action="store_true",
        help="Write results to output files (subs.txt / ips.txt)",
    )
    # Call main function
    args, sysargs = parser.parse_known_args()
    main(args)


# Main
def main(args):
    try:
        targets = functions.check_prefix(args.target, None)
        target = targets[0].replace("http://", "").replace("https://", "").strip("/")
        sub_enum = SubEnum(
            target=target,
            wordlist=args.wordlist,
            verbose=args.verbose,
            threads=args.active_threads,
            write_output=args.output,
        )
        asyncio.run(sub_enum.run())
    except KeyboardInterrupt:
        print(f"{cli.red}leaving..{cli.endc}")
        exit(0)

