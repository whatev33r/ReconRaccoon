#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import importlib
from os import listdir
from os.path import isfile, join
from src.framework import cli

# Print Banner
print(cli.racoon)
# Parse modules
modules = [f.strip(".py") for f in listdir('src/modules') if f.endswith('.py') and isfile(join('src/modules', f))]
# Args
parser = argparse.ArgumentParser(prog='ReconRacoon.py', description='Web Security Testing Framework')
parser.add_argument('module', choices=modules)
# parser.add_argument('-L', '--list-modules', action='store_true')
args = parser.parse_args()

# Main
if __name__ == '__main__':
    try:
        print(f"{cli.green}[+]{cli.endc} Selected: {args.module}")
        init = getattr(importlib.import_module(f'src.modules.{args.module}'), '__init__')
        init()
    except Exception as E:
        exit(E)
