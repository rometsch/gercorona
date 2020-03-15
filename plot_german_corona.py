#!/usr/bin/env python3
import datetime
import os
import re

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import (YEARLY, DateFormatter, RRuleLocator, drange,
                              rrulewrapper, date2num)
from scipy.optimize import curve_fit

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

def exp_func(x, x0, c):
    return np.exp(c*(x-x0))

def get_exp_fit(xdata, ydata):
    """ Fits an exponential function to the data and returns a function."""
    popt, pcov = curve_fit(exp_func, xdata, ydata, p0 = (xdata[0], 1), bounds=(0, np.inf))
    return (lambda x: exp_func(x, *popt) , popt)

# data taken from
# https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html
# for German state of Baden-Württemberg
# historic data from archive.org wayback machine
# https://web.archive.org/web/*/https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html

files = [ os.path.join("data", f) for f in os.listdir("data")]
database = {}
for fname in files:
    datestr = os.path.basename(fname).split(".")[0]
    try:
        dt = datetime_from_customstring(datestr)
    except AttributeError:
        continue
    with open(fname, "r") as infile:
        try:
            total = 0
            for line in infile:
                if line == "": continue
                parts = line.split()
                num = int(parts[-1].replace(".",""))
                total += num
                name = "-".join(parts[:-1])
                if name in database:
                    database[name][dt] = num
                else:
                    database[name] = {dt : num}
            name = "Gesamt"
            num = total
            if name in database:
                database[name][dt] = num
            else:
                database[name] = {dt : num}
        except AttributeError:
            pass        

fig, axes = plt.subplots(1,2, figsize=(10,6.4))
names = sorted([n for n in database.keys()])

for name in names:
    #print("Plotting:", name)
    data = database[name]
    dates = [d for d in data.keys()]
    values = np.array([x for x in data.values()])
    time = np.array(date2num(dates))
    inds = time.argsort()
    time = time[inds]
    values = values[inds]
    if all(np.array([x for x in values]) < 50):
        continue
    fit, popt = get_exp_fit(time, values)
    #print(popt)
    t_sample = np.linspace(time[0], time[-1] + 0.2*(time[-1] - time[0]), 500)
    for ax in axes:
        line, = ax.plot_date(time, values, label=name)
        line, = ax.plot(t_sample, fit(t_sample), color=line.get_color())
        formatter = DateFormatter('%y-%m-%d')
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_tick_params(rotation=30, labelsize=10)
        ax.grid(alpha=0.3)

axes[1].set_yscale("log")

box = axes[0].get_position()

# Put a legend to the right of the current axis
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.legend(bbox_to_anchor=(1.05, 1))

last_date = sorted(dates)[-1]
plt.title("SARS-CoV-2 infections for states with 5 or more cases\ndata from Robert Koch Institut, updated {}".format(last_date))

plt.savefig("corona.png", bbox_inches='tight',dpi=300)

#plt.show()
