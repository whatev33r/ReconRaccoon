#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import importlib
import os

from ReconRaccoon.src.framework import cli, functions
from ReconRaccoon.src.framework.aws_proxy_hob import AWSProxyHob


def main():
    print(cli.raccoon)

    working_dir = os.path.dirname(os.path.realpath(__file__))
    modules = [f for f in next(os.walk(f"{working_dir}/src/modules"))[1]]
    if "template" in modules:
        modules.remove("template")
    if "__pycache__" in modules:
        modules.remove("__pycache__")

    parser = argparse.ArgumentParser(
        prog="reconraccoon.py",
        description="Web Security Testing Framework",
        add_help=False,
    )
    parser.add_argument("module", choices=modules, nargs="?", help="")
    parser.add_argument("--aws-credentials", type=str, required=False, dest="aws_credentials",
                        help="Path to file containing AWS credentials for proxy hopping")
    args, unknown = parser.parse_known_args()

    try:
        use_proxies = False
        if args.aws_credentials:
            print(f"{cli.green}[+]{cli.endc} Setting up AWS Proxy hopping")
            aws_access_key_id, aws_secret_key = functions.read_aws_credentials_from_env(
                args.aws_credentials)
            if aws_access_key_id is None or aws_secret_key is None:
                print(
                    f"{cli.red}[x]{cli.endc} Error: AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY not found in {args.aws_credentials}")
                print(
                    f"{cli.yellow}[x]{cli.endc} Continuing without AWS Proxy hopping")
            else:
                use_proxies = True
                AWSProxyHob.set_credentials(aws_access_key_id, aws_secret_key)
                print(f"{cli.green}[+]{cli.endc} AWS Proxy hopping enabled")

        if args.module:
            print(f"{cli.green}[+]{cli.endc} Executing: {args.module}")
            module = importlib.import_module(
                f"ReconRaccoon.src.modules.{args.module}.main")
            setattr(module, "USE_PROXIES", use_proxies)
            module.__init__()
        else:
            parser.print_help()
    except Exception as E:
        exit(f"{cli.red}[x]{cli.endc} Error: {E}")


if __name__ == "__main__":
    main()
