![Supported Python versions](https://img.shields.io/badge/python-3.7+-blue.svg)

# ReconRaccoon 1.1.0
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
usage: reconraccoon.py [-s {module}] [{module}]

Web Security Testing Framework

positional arguments:
  {module}

options:
  -s {module}, --setup {module}
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
