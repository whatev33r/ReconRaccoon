#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import importlib
import os

from ReconRaccoon.src.framework import cli


def main():
    print(cli.raccoon)

    working_dir = os.path.dirname(os.path.realpath(__file__))
    modules = [f for f in next(os.walk(f"{working_dir}/src/modules"))[1]]

    parser = argparse.ArgumentParser(
        prog="reconraccoon.py",
        description="Web Security Testing Framework",
        add_help=False,
    )
    parser.add_argument("module", choices=modules, nargs="?", help="")
    args, unknown = parser.parse_known_args()

    try:
        if args.module:
            print(f"{cli.green}[+]{cli.endc} Executing: {args.module}")
            init = getattr(
                importlib.import_module(f"ReconRaccoon.src.modules.{args.module}.main"),
                "__init__",
            )
            init()
        else:
            parser.print_help()
    except Exception as E:
        exit(f"{cli.red}[x]{cli.endc} Error: {E}")


# Main
if __name__ == "__main__":
    main()
