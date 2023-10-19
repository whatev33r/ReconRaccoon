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


class SubEnum:
    def __init__(self, target: str, wordlist: str, output: str, verbose: bool):
        self.target = target
        self.wordlist = self.filter_wordlist(wordlist)
        self.wildcard = self.get_wildcard()
        self.output = output
        self.verbose = verbose
        self.ips = []
        self.subs = []

    def filter_wordlist(self, wordlist: str):
        with open(wordlist) as file:
            lst = file.readlines()
        new_worlist = list(map(str.strip, lst))
        new_worlist = list(dict.fromkeys(new_worlist))
        new_worlist = [x.lower() for x in new_worlist]
        return new_worlist

    def get_wildcard(self):
        wildcard = socket.gethostbyname(self.target)
        return wildcard

    def enumerate_subdomains(self):
        print(
            f'\r{cli.blue}[$]{cli.endc} Wildcard: {cli.blue}*{cli.endc}.{cli.bold}{self.target}{cli.endc}\t IP: {self.wildcard}')

        for subdom in self.wordlist:
            try:
                dns = f'{subdom}.{self.target}'
                ip = socket.gethostbyname(dns)

                if ip != self.wildcard:
                    print(
                        f'\r{cli.green}[+]{cli.endc} Hostname: {subdom}.{self.target}\t IP: {ip}')
                    self.ips.append(ip)
                    self.subs.append(f'{subdom}.{self.target}')
            except Exception as e:
                if self.verbose:
                    print(
                        f'\r{cli.red}[-]{cli.endc} Hostname: {dns}\t Response: {e}')

    def output_files(self):
        if self.output:
            with open('subs.txt', 'w') as f:
                for line in self.subs:
                    f.write(f'{line}\n')
            with open('ips.txt', 'w') as f:
                for line in self.ips:
                    f.write(f'{line}\n')


def main(args):
    sub_enum = SubEnum(args.target, args.wordlist, args.output, args.verbose)
    sub_enum.enumerate_subdomains()
    sub_enum.output_files()
