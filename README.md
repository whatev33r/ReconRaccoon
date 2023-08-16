![Supported Python versions](https://img.shields.io/badge/python-3.7+-blue.svg)

# ReconRacoon
Just some 1337 Racoon digging through other people's trash cans.

```
┌───────────────────────────────────────────┐
│                        ,,,                │
│ TS: 13:37:00        .'    `/\_/\          │
│                   .'       <─I─>          │
│        <((((((((((  )____(  \./           │
│                   \( \(   \(\(            │
│ ReconRacoon        `-"`-"  " "            │
└───────────────────────────────────────────┘

usage: ReconRacoon.py {module}
```

## Module: Resolve
```
usage: ReconRacoon.py resolve [-h] -t TARGET [-r TIMEOUT] [-a THREADS] [-u USER_AGENT] [-i {INFO,SUCCESS,REDIRECTION,CLIENT_ERROR,SERVER_ERROR}] [-x {INFO,SUCCESS,REDIRECTION,CLIENT_ERROR,SERVER_ERROR}] [-c] [-v]

options:
  -h, --help            show this help message and exit
  -t TARGET, --target TARGET
                        Target URLs or IPs (str/file)
  -r TIMEOUT, --request-timeout TIMEOUT
                        Timeout for all http requests
  -a THREADS, --active-threads THREADS
                        Threads for all http requests
  -u USER_AGENT, --user-agent USER_AGENT
                        Use custom user agent
  -i {INFO,SUCCESS,REDIRECTION,CLIENT_ERROR,SERVER_ERROR}, --include-filter {INFO,SUCCESS,REDIRECTION,CLIENT_ERROR,SERVER_ERROR}
                        Include HTTP reponse type
  -x {INFO,SUCCESS,REDIRECTION,CLIENT_ERROR,SERVER_ERROR}, --exclude-filter {INFO,SUCCESS,REDIRECTION,CLIENT_ERROR,SERVER_ERROR}
                        Exclude HTTP reponse type
  -c, --common-ports    Check all common webserver ports (seclists)
  -v, --verbose         Display verbose output (timeouts/errors)

```
