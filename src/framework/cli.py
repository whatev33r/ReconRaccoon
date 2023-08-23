#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

# Colors
endc = '\033[m'
black = '\033[30m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'
blue = '\033[34m'
purple = '\033[35m'
cyan = '\033[36m'
white = '\033[37m'

# Styles
bold = '\033[01m'

# Timestamp
now = datetime.datetime.now()
current_time = now.strftime("%H:%M:%S")
current_date = now.strftime("%D")

# Banner
raccoon = rf'''┌───────────────────────────────────────────┐
│ DT: {current_date}           ,,,                │
│ TS: {current_time}        .'    `/\_/\          │
│                   .'       <─I─>          │
│        <((((((((((  )____(  \./           │
│                   \( \(   \(\(            │
│ {yellow}Recon{purple}Raccoon{endc}       `-"`-"  " "            │
└───────────────────────────────────────────┘'''
