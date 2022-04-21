from datetime import date, datetime, timezone
from matplotlib import dates, pyplot
from db import *
import numpy as np

cardata = {}

def cardata_add(dealertype, date, carsplit):
    if len(carsplit) < 3 or carsplit[2] != "soldout":
        if int(carsplit[0]) in cardata:
            cardata[int(carsplit[0])].append(f"{dealertype},{date},{carsplit[1]}")
        else:
            cardata[int(carsplit[0])] = [f"{dealertype},{date},{carsplit[1]}"]

def cardata_exists(carid):
    if carid in cardata and len(cardata[carid]) > 1:
        return True
    return False

def cardata_plot(carid):
    now = datetime.now(timezone.utc).date()
    #mindate = now
    mindate = date.fromisoformat("2022-03-08")
    daycredits = {}
    for values in cardata[carid]:
        type, datestr, credits = values.split(',')
        if datestr == "*":
            daycredits["*"] = int(credits)
        else:
            dateval = date.fromisoformat(f"20{datestr}")
            daycredits[dates.date2num(dateval)] = int(credits)

    # convert to matplotlib (which also allows for indexing)
    mindate = dates.date2num(mindate)
    x = []
    y = []
    annotates = []
    lastval = None
    weeks = []
    for i in range(int(mindate), int(dates.date2num(now))+1):
        f = np.float64(i)
        x.append(dates.num2date(f))
        if f in daycredits:
            y.append(daycredits[f])
        elif "*" in daycredits:
            y.append(daycredits["*"])
        else:
            y.append(None)
        if y[-1] != lastval:
            lastval = y[-1]
            if lastval is not None:
                annotates.append((f"Cr. {int(lastval):,}",f,lastval))

    for i in range(int(dates.date2num(now)), int(mindate)-6, -7):
        f = np.float64(i)
        weeks.append(f)

    fig = pyplot.figure(figsize=(8,6))
    pyplot.title(cardb_id_to_name(carid), {'fontsize': 20})
    pyplot.ylim(0,max([i for i in y if i is not None])*1.1)
    pyplot.plot(x, y, marker='.')

    for annot in annotates:
        pyplot.annotate(annot[0], (annot[1], annot[2]), xytext=(4,4), textcoords="offset pixels")

    pyplot.grid(True, alpha=0.2)
    pyplot.xticks(weeks, rotation=60)
    pyplot.ticklabel_format(axis='y', style='plain')
    fig.subplots_adjust(bottom=0.16)
    pyplot.savefig(f"build/cars/prices_{carid}.png")
    pyplot.close()