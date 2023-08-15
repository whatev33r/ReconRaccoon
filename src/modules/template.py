#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse


# Init
def __init__():
    parser = argparse.ArgumentParser(prog='reconracoon.py template', description='Module for TEMPLATE')
    parser.add_argument('-t', '--target', required=True)
    args, sysargs = parser.parse_known_args()
    # Call main function
    main(args)


# Main
def main(args):
    print(args.target)
