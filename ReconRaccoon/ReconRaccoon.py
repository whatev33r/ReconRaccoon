#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import importlib
import sys
import subprocess
import os
from .src.framework import cli


def main():
    # Print banner
    print(cli.raccoon)
    # Get working dir
    working_dir = os.path.dirname(os.path.realpath(__file__))
    # Parse modules
    modules = [f for f in os.listdir(f'{working_dir}/src/modules')]
    # Args
    parser = argparse.ArgumentParser(prog='ReconRaccoon.py', description='Web Security Testing Framework', add_help=False)
    parser.add_argument('module', choices=modules, nargs='?', help='')
    args, unknown = parser.parse_known_args()
    # Execute Module
    try:
        if args.module:
            print(f"{cli.green}[+]{cli.endc} Executing: {args.module}")
            init = getattr(importlib.import_module(f'src.modules.{args.module}.main'), '__init__')
            init()
        else:
            parser.print_help()
    except Exception as E:
        exit(f'{cli.red}[x]{cli.endc} Error: {E}')


# Main
if __name__ == '__main__':
    main()
