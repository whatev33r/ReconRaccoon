#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from src.framework import cli


# Init
def __init__():
    parser = argparse.ArgumentParser(prog='ReconRacoon.py template', description='Module for TEMPLATE')
    parser.add_argument('-t', '--target', required=True)
    args, sysargs = parser.parse_known_args()
    # Call main function
    main(args)


# Main
def main(args):
    print(cli.current_date)
    print(cli.current_time)
    print(args.target)
