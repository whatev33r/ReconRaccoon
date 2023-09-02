#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

from ReconRaccoon.src.framework import cli, functions


def __init__():
    parser = argparse.ArgumentParser(
        prog="reconraccoon.py template", description="Module for TEMPLATE"
    )
    parser.add_argument("-t", "--target", required=True)
    args, sysargs = parser.parse_known_args()
    main(args)


def main(args):
    print(cli.current_date)
    print(cli.current_time)
    target = functions.check_prefix(args.target, None)
    print(target)
