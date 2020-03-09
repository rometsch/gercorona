#!/usr/bin/env python3

from bs4 import BeautifulSoup
from urllib.error import URLError
from urllib.error import HTTPError
from urllib.request import urlopen
import re
import os
import datetime

def main():
    url = "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html"
    res = get_webpage(url)
    data_table = extract_data_table(res)
    data = get_data_dict(data_table)
    date = get_date(res)
    date_str = "-".join(["{:02d}".format(int(n)) for n in date]) 
    data_file = date_str + ".txt"
    data_file = os.path.join("data", data_file)
    if not os.path.exists(data_file):
        with open(data_file, "w") as outfile:
            for name, val in data.items():
                print("{}\t{}".format(name, val), file=outfile)
    print("{}: obtained data for {}".format(datetime.datetime.now(), date_str))

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
    date = [y,m,d,H,M]
    return date


def get_data_dict(table):
    entries = table.findAll("td")
    data = {}
    name = ""
    for n,e in enumerate(entries):
        if n%3 == 0:
            name = e.contents[0]
            if "Gesamt" in name:
                break
        if n%3 == 1:
            val = e.contents[0]
            data[name] = val
        if n%3 == 2:
            continue
    return data

def get_webpage(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
    except URLError:
        print("Server down or incorrect domain")
    else:
        res = BeautifulSoup(html.read(), "html5lib")
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
