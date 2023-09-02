#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

# Common http ports
ports = [66, 80, 81, 443, 445, 457, 1080, 1100, 1241, 1352, 1433, 1434, 1521,
         1944, 2301, 3000, 3128, 3306, 4000, 4001, 4002, 4100, 4443, 5000,
         5432, 5800, 5801, 5802, 6346, 6347, 7001, 7002, 8443, 8888, 30821]


# Check prefix
def check_prefix(target, common_ports):
    trgt = []
    if os.path.isfile(target) is True:
        with open(target) as file:
            check = [x.strip() for x in file.readlines()]
            for url in check:
                if url.startswith('https://') or url.startswith('http://'):
                    if common_ports:
                        for port in ports:
                            trgt.append(f'{url}:{port}')
                    else:
                        trgt.append(url)
                else:
                    if common_ports:
                        for port in ports:
                            trgt.append(f'http://{url}:{port}')
                            trgt.append(f'https://{url}:{port}')
                    else:
                        trgt.append(f'http://{url}')
                        trgt.append(f'https://{url}')
    else:
        if target.startswith('https://') or target.startswith('http://'):
            if common_ports:
                for port in ports:
                    trgt.append(f'{target}:{port}')
            else:
                trgt.append(target)
        else:
            if common_ports:
                for port in ports:
                    trgt.append(f'http://{target}:{port}')
                    trgt.append(f'https://{target}:{port}')
            else:
                trgt.append(f'http://{target}')
                trgt.append(f'https://{target}')
    return trgt
