#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from dotenv import dotenv_values
import requests

from ReconRaccoon.src.framework.aws_proxy_hob import AWSProxyHob

common_ports = [
    66,
    80,
    81,
    443,
    445,
    457,
    1080,
    1100,
    1241,
    1352,
    1433,
    1434,
    1521,
    1944,
    2301,
    3000,
    3128,
    3306,
    4000,
    4001,
    4002,
    4100,
    4443,
    5000,
    5432,
    5800,
    5801,
    5802,
    6346,
    6347,
    7001,
    7002,
    8443,
    8888,
    30821,
]


def process_single_url(url: str, use_common_ports: bool):
    ports = common_ports if use_common_ports else []

    if url.startswith(("http://", "https://")):
        return [f"{url}:{port}" for port in ports] or [url]

    return [
        f"http://{url}:{port}" for port in ports
    ] + [
        f"https://{url}:{port}" for port in ports
    ] or [f"http://{url}", f"https://{url}"]


def process_file(file_path: str, use_common_ports: bool):
    with open(file_path) as file:
        urls = [x.strip() for x in file.readlines()]
        return [url for u in urls for url in process_single_url(u, use_common_ports)]


def check_prefix(target: str, use_common_ports: bool):
    if os.path.isfile(target):
        return process_file(target, use_common_ports)
    else:
        return process_single_url(target, use_common_ports)


def read_aws_credentials_from_env(filename):
    env_vars = dotenv_values(filename)
    aws_access_key_id = env_vars.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = env_vars.get("AWS_SECRET_ACCESS_KEY")
    return aws_access_key_id, aws_secret_access_key


def get_session(target):
    if not AWSProxyHob.get_instance(None, None):
        return requests.Session()
    return AWSProxyHob.get_proxy_session(target)
