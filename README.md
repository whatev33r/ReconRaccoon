![Supported Python versions](https://img.shields.io/badge/python-3.7+-blue.svg)
[![ReconRaccoon-CI](https://github.com/whatev33r/ReconRaccoon/actions/workflows/reconraccoon.yml/badge.svg)](https://github.com/whatev33r/ReconRaccoon/actions/workflows/reconraccoon.yml)

# ReconRaccoon 1.2.0
Just some 1337 Raccoon digging through other people's trash cans.

```
┌───────────────────────────────────────────┐
│ DT: 08/21/23           ,,,                │
│ TS: 14:10:32        .'    `/\_/\          │
│                   .'       <─I─>          │
│        <((((((((((  )____(  \./           │
│                   \( \(   \(\(            │
│ ReconRaccoon       `-"`-"  " "            │
└───────────────────────────────────────────┘
usage: reconraccoon.py [--aws-credentials AWS_CREDENTIALS] [{crawl,resolve,subenum,shcheck}]

Web Security Testing Framework

positional arguments:
  {crawl,resolve,subenum,shcheck}

options:
  --aws-credentials AWS_CREDENTIALS
                        Path to file containing AWS credentials for proxy hopping
```

## Installation
### PyPi
```
pip install reconraccoon
```

### From Source
```
pip install -r requirements.txt
python3 reconraccoon.py
```

## Usage
> reconraccoon.py {resolve,crawl,shcheck} -h

## Current Modules
- Resolve
  - Resolves targets to get overview of initial HTTP response codes.
- Crawl
  - Crawls HTTP response body for source files / links.
- Shcheck
  - Checks HTTP security headers (based on [shcheck](https://github.com/santoru/shcheck) by santoru).
- Template
  - Template for module development.
