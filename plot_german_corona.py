#!/usr/bin/env python3
import datetime
import os
import re

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import (YEARLY, DateFormatter, RRuleLocator, drange,
                              rrulewrapper)


def datetime_from_isoformat(timestring):
    """ Convert a time sting 'yyyy-mm-dd HH:MM' to a datetime object.

    Parameters
    ----------
    timestring: str
        Time string in with format 'yyyy-mm-dd HH:MM'.

    Returns
    -------
    obj: datetime.datetime
        datetime object with date and time from input.
    """
    isoformat_str = r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})"
    m = re.match(isoformat_str, timestring)
    year, month, day, hour, minute = [int(i) for i in m.groups()]
    return datetime.datetime(year, month, day, hour, minute)

def datetime_from_customstring(timestring):
    """ Convert a time sting 'yyyy-mm-dd-HH-MM' to a datetime object.

    Parameters
    ----------
    timestring: str
        Time string in with format 'yyyy-mm-dd-HH-MM'.

    Returns
    -------
    obj: datetime.datetime
        datetime object with date and time from input.
    """
    isoformat_str = r"(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})"
    m = re.match(isoformat_str, timestring)
    year, month, day, hour, minute = [int(i) for i in m.groups()]
    return datetime.datetime(year, month, day, hour, minute)


# data taken from
# https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html
# for German state of Baden-Württemberg
# historic data from archive.org wayback machine
# https://web.archive.org/web/*/https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html

files = [ os.path.join("data", f) for f in os.listdir("data")]
database = {}
for fname in files:
    datestr = os.path.basename(fname).split(".")[0]
    dt = datetime_from_customstring(datestr)
    with open(fname, "r") as infile:
        for line in infile:
            if line == "": continue
            parts = line.split()
            num = int(parts[-1])
            name = " ".join(parts[:-1])
            if name in database:
                database[name][dt] = num
            else:
                database[name] = {dt : num}


fig, axes = plt.subplots(1,2, figsize=(10,6.4))
for name, data in database.items():
    dates = data.keys()
    values = data.values()
    if all(np.array([x for x in values]) < 5):
        continue
    for ax in axes:
        ax.plot_date(dates, values, label=name)

        formatter = DateFormatter('%y-%m-%d')
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_tick_params(rotation=30, labelsize=10)
        ax.grid(alpha=0.3)

axes[1].set_yscale("log")

box = axes[0].get_position()

# Put a legend to the right of the current axis
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.legend(bbox_to_anchor=(1.05, 1))
plt.title("SARS-CoV-2 infections for states with 5 or more cases\n(data from Robert Koch Institut)")

plt.savefig("corona.png", bbox_inches='tight')

#plt.show()
