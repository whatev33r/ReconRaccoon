#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import socket

from ReconRaccoon.src.framework import cli, functions


def __init__():
    parser = argparse.ArgumentParser(
        prog="reconraccoon.py template", description="Module for TEMPLATE"
    )
    parser.add_argument(
        "-t", "--target",
        required=True
    )
    parser.add_argument(
        '-w', '--wordlist',
        required=True)
    parser.add_argument(
        '-o',
        '--output',
        action='store_true'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true'
    )
    args, sysargs = parser.parse_known_args()
    main(args)


def main(args):
    # Target
    target = args.target
    # Lists
    ips = []
    subs = []
    # Filter Wordlist
    f = open(args.wordlist)
    lst = f.readlines()
    new = list(map(str.strip, lst))
    new = list(dict.fromkeys(new))
    new = [x.lower() for x in new]
    wildcard = socket.gethostbyname(target)
    print(f'\r{cli.blue}[$]{cli.endc} Wildcard: {cli.blue}*{cli.endc}.{cli.bold}{target}{cli.endc}\t IP: {wildcard}')
    # Main Loop
    for subdom in new:
        try:
            dns = f'{subdom}.{target}'
            ip = socket.gethostbyname(dns)
            if ip != wildcard:
                print(f'\r{cli.green}[+]{cli.endc} Hostname: {subdom}.{target}\t IP: {ip}')
                ips.append(ip)
                subs.append(f'{subdom}.{target}')
            else:
                pass
        except Exception as E:
            if args.verbose is True:
                print(f'\r{cli.red}[-]{cli.endc} Hostname: {dns}\t Response: {E}')
            else:
                pass
    # Generate Out Files
    if args.output:
        with open('subs.txt', 'w') as f:
            for line in subs:
                f.write(f'{line}\n')
        with open('ips.txt', 'w') as f:
            for line in ips:
                f.write(f'{line}\n')
