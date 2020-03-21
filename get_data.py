#!/usr/bin/env python3

import datetime
import os
import re
import urllib
from urllib.error import HTTPError, URLError

from bs4 import BeautifulSoup


def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("raw", exist_ok=True)

    url = "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html"
    res = get_webpage(url)
    now = str(datetime.datetime.now()).replace(" ", "-").replace(":", "-")
    raw_file = os.path.join("raw", "{}.html".format(now))
    with open(raw_file, "w") as outfile:
        print(res, file=outfile)
    date = get_date(res)
    remove_whitespaces(res)
    data_table = extract_data_table(res)
    data = get_data_dict(data_table)
    date_str = "-".join(["{:02d}".format(int(n)) for n in date])
    data_file = date_str + ".txt"
    data_file = os.path.join("data", data_file)
    if not os.path.exists(data_file):
        with open(data_file, "w") as outfile:
            for name, val in data.items():
                print("{}\t{}".format(name, val), file=outfile)
    print("{}: obtained data for {}".format(datetime.datetime.now(), date_str))

def remove_whitespaces(soup):
    allowed_chars = ["-"]
    for child in soup.children:
        if child.string:
            child.string = ''.join([ch for ch in child.string if ch.isalnum() or ch in allowed_chars])
        else:
            remove_whitespaces(child)

def get_date(res):
    for e in res.findAll("p"):
        try:
            pattern = "\(Datenstand: ([\d]+)\.([\d]+).([\d]{4}), ([\d]{2}):([\d]{2}) Uhr\)"
            m = re.search(pattern, str(e.contents[0]))
            if m is not None:
                date = m.groups()
                break
            pattern = "Stand: ([\d]+)\.([\d]+).([\d]{4}), ([\d]+):([\d]{2}) Uhr"
            m = re.search(pattern, str(e.contents[0]))
            if m is not None:
                date = m.groups()
                break
        except IndexError:
            pass
    d, m, y, H, M = date
    date = [y, m, d, H, M]
    return date


def get_data_dict(table):
    entries = table.findAll("td")
    data = {}
    name = ""
    N = 6
    for n, e in enumerate(entries):
        if n % N == 0:
            name = e.contents[0]
        if "Gesamt" in name:
            break
        if n % N == 1:
            val = e.contents[0].split()[0]
            data[name] = val
        else:
            continue
    return data


def get_webpage(url):
    try:
        # Open the URL as Browser, not as python urllib
        page = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0'})
        infile = urllib.request.urlopen(page).read()
        html = infile.decode('utf-8')
    except HTTPError as e:
        print(e)
    except URLError:
        print("Server down or incorrect domain")
    else:
        res = BeautifulSoup(html, "html5lib")
    return res


def extract_data_table(res):
    tables = res.findAll("table")
    for table in tables:
        if "Bundesland" in str(table):
            data_table = table
            break
    return data_table


if __name__ == "__main__":
    main()
