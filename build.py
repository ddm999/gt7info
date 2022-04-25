import os, shutil, json
from datetime import datetime, timezone
from cardata import *
from db import *

jsondata = {
    "updatetimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

html = ""
with open("index.html", "r", encoding='utf-8') as f:
    html = f.read()

used_template = ""
with open("used.html", "r", encoding='utf-8') as f:
    used_template = f.read()

legend_template = ""
with open("legend.html", "r", encoding='utf-8') as f:
    legend_template = f.read()
    
dailyrace_template = ""
with open("dailyrace.html", "r", encoding='utf-8') as f:
    dailyrace_template = f.read()

useddir = os.listdir("_data/used")
useddir.sort()
useddir.remove("starter.csv")
useddir.remove("menubook.csv")

legenddir = os.listdir("_data/legend")
legenddir.sort()

dailyracedir = os.listdir("_data/dailyrace")
dailyracedir.sort()

##################################################
# handle brand central prices
##################################################
lines = []
with open(f"_data/brandcentral/{os.listdir('_data/brandcentral')[-1]}") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

for car in lines:
    cardata_add("brandcentral","*",car.strip().split(","))

##################################################
# handle rewards
##################################################
lines = []
with open(f"_data/rewards/{os.listdir('_data/rewards')[-1]}") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

rewards = {}
for reward in lines:
    rewardsplit = reward.strip().split(",")
    rewards[rewardsplit[0]] = rewardsplit[1:]
##################################################
# handle used car dealership
##################################################
lines = [] # type: list[str]
with open(f"_data/used/{useddir[-1]}") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

jsondata["used"] = {
    "date": useddir[-1][:-4],
    "cars": [],
}

normal = {} # type: dict[str, int]
limited = {} # type: dict[str, int]
soldout = {} # type: dict[str, int]
for car in lines:
    carsplit = car.strip().split(",")
    # days appeared, negative means still counting
    if carsplit[2] == "normal":
        normal[carsplit[0]] = -1
    elif carsplit[2] == "limited":
        limited[carsplit[0]] = -1
    elif carsplit[2] == "soldout":
        soldout[carsplit[0]] = -1

for i in range(len(useddir)):
    morelines = []
    with open(f"_data/used/{useddir[-1-i]}") as f:
        morelines = f.readlines()
    morelines = morelines[1:] # remove headers


    carnames = {}
    for car in morelines:
        carsplit = car.strip().split(",")
        carnames[carsplit[0]] = carsplit[2]
        cardata_add("used", useddir[-1-i].replace('.csv',''), carsplit)

    if i == 0: # don't include current day in estimate calculation
        continue

    for k in normal.keys():
        if normal[k] < 0:
            if k in carnames.keys() and carnames[k] == "normal":
                normal[k] -= 1
            else:                       
                normal[k] = 0-normal[k]

    for k in limited.keys():
        if limited[k] < 0:
            if k in carnames.keys() and carnames[k] == "limited":
                limited[k] -= 1
            else:                       
                limited[k] = 0-limited[k]
                normal[k] = -1

    for k in soldout.keys():
        if soldout[k] < 0:
            if k in carnames.keys() and carnames[k] == "soldout":
                soldout[k] -= 1
            else:                       
                soldout[k] = 0-soldout[k]

usedcars_section = ""
for line in lines:
    if line == "\n":
        continue
    carid, cr, state = line.strip().split(",")
    name = cardb_id_to_name(carid)
    manufacturer = cardb_id_to_makername(carid)
    region = cardb_id_to_countrycode(carid)

    new = state == "normal" and carid in normal.keys() and normal[carid] == 1

    if new:
        car = '<p class="car carnew">\n'+used_template
    elif state == "limited":
        car = '<p class="car carlimited">\n'+used_template
    elif state == "soldout":
        car = '<p class="car carsold">\n'+used_template
    else:
        car = '<p class="car">\n'+used_template

    flag = f"img/pdi-flag.png" if region == "pdi" else f"https://flagcdn.com/h24/{region}.png"

    car = car.replace("%FLAG", flag)
    car = car.replace("%MANUFACTURER", manufacturer.upper())
    if cardata_exists(int(carid)):
        car = car.replace("%NAME", f'<a href="cars/prices_{carid}.png" target="_blank">{name}</a>')
    else:
        car = car.replace("%NAME", name)
    car = car.replace("%CREDITS", f"{int(cr):,}")
    estimatedays = 0
    maxestimatedays = 0
    daysvisible = 0
    if new:
        car += '\n        <span id="new">NEW</span>'

    if state == "normal":
        daysvisible = normal[carid]
        if carid in normal.keys() and normal[carid] > 0: # >0 checks for messed up data
            if normal[carid] <= 4:
                estimatedays = 7-normal[carid]
                maxestimatedays = 10-normal[carid]
                car += f'\n        <span id="days-estimate">Estimate: {estimatedays-1} to {maxestimatedays-1} More Days Remaining</span>'
            elif normal[carid] <= 6:
                estimatedays = 3
                maxestimatedays = 10-normal[carid]
                car += f'\n        <span id="days-estimate">Estimate: {estimatedays-1} to {maxestimatedays-1} More Days Remaining</span>'
            else:
                estimatedays = 3
                maxestimatedays = 3
                car += '\n        <span id="days-estimate">Limited Stock Soon<br>(2+ More Days Remaining)</span>'
    elif state == "limited":
        daysvisible = normal[carid] + limited[carid]
        if carid in limited.keys() and limited[carid] == 2:
            estimatedays = 1
            car += '\n        <span id="limited">Limited Stock</span><span id="days-remaining">Last Day Available</span>'
        elif carid in limited.keys() and limited[carid] == 1:
            estimatedays = 2
            car += '\n        <span id="limited">Limited Stock</span><span id="days-remaining">1 More Day Remaining</span>'
        else:
            estimatedays = 1
            car += '\n        <span id="limited">Limited Stock</span><span id="days-remaining">0 Days Remaining <small style="font-size: 9px;">This should be sold out...</small></span>'
        maxestimatedays = estimatedays
    elif state == "soldout":
        estimatedays = 0
        maxestimatedays = 0
        car += '\n        <span id="soldout">SOLD OUT</span>'
    else:
        car += f'\n        <span id="days-estimate">Unknown estimate due to error by Polyphony.</span>'

    if carid in rewards.keys():
        rewardinfo = rewards[carid]
        car +=  '\n        <span id="reward-text">REWARD<br>CAR</span>'
        rewardtype = ""
        match rewardinfo[0]:
            case "menubook":
                rewardtype = "Menu Book"
            case "license":
                rewardtype = "License:"
            case "mission":
                rewardtype = "Mission Set:"
        car += f'\n        <img id="reward-icon" src="img/open-book.svg" width="24" title="Reward from {rewardtype} {rewardinfo[1]}'
        if rewardinfo[2] != "-":
            car += f' All {rewardinfo[2].capitalize()}'
        car +=  '"/>'
 
    usedcars_section += f'{car}\n      </p>'
    jsondata["used"]["cars"].append({
        "carid": carid, "manufacturer": manufacturer, "region": region, "name": name, "credits": int(cr),
        "state": state, "estimatedays": estimatedays, "maxestimatedays": maxestimatedays, "new": new, "daysvisible": daysvisible
    })

##################################################
# handle legend car dealership
##################################################
lines = [] # type: list[str]
with open(f"_data/legend/{legenddir[-1]}") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

jsondata["legend"] = {
    "date": legenddir[-1][:-4],
    "cars": [],
}

normal = {} # type: dict[str, int]
limited = {} # type: dict[str, int]
for car in lines:
    carsplit = car.strip().split(",")
    # days appeared, negative means still counting
    if carsplit[2] == "normal":
        normal[carsplit[0]] = -1
    elif carsplit[2] == "limited":
        limited[carsplit[0]] = -1

for i in range(len(legenddir)):
    morelines = []
    with open(f"_data/legend/{legenddir[-1-i]}") as f:
        morelines = f.readlines()
    morelines = morelines[1:] # remove headers

    carnames = {}
    for car in morelines:
        carsplit = car.strip().split(",")
        carnames[carsplit[0]] = carsplit[2]
        cardata_add("legend", legenddir[-1-i].replace('.csv',''), carsplit)

    if i == 0: # don't include current day in estimate calculation
        continue

    for k in normal.keys():
        if normal[k] < 0:
            if k in carnames.keys() and carnames[k] == "normal":
                normal[k] -= 1
            else:                       
                normal[k] = 0-normal[k]

    for k in limited.keys():
        if limited[k] < 0:
            if k in carnames.keys() and carnames[k] == "limited":
                limited[k] -= 1
            else:
                limited[k] = 0-limited[k]
                normal[k] = -1

legendcars_section = ""
for line in lines:
    if line == "\n":
        continue
    carid, cr, state = line.strip().split(",")
    name = cardb_id_to_name(carid)
    manufacturer = cardb_id_to_makername(carid)
    region = cardb_id_to_countrycode(carid)

    new = state == "normal" and carid in normal.keys() and normal[carid] == 1
    if new:
        car = '<p class="lcar carnew">\n'+legend_template
    elif state == "limited":
        car = '<p class="lcar carlimited">\n'+legend_template
    elif state == "soldout":
        car = '<p class="lcar carsold">\n'+legend_template
    else:
        car = '<p class="lcar">\n'+legend_template

    car = car.replace("%MANUFACTURER", manufacturer)
    if cardata_exists(int(carid)):
        car = car.replace("%NAME", f'<a href="cars/prices_{carid}.png" target="_blank">{name}</a>')
    else:
        car = car.replace("%NAME", name)
    car = car.replace("%CREDITS", f"{int(cr):,}")
    grind = int(cr)/2750000
    play = int(cr)/400000
    onetime = int(cr)/4000000
    customrace = int(cr)/122053
    nordslaps = int(cr)/6203.8
    if state != "soldout":
        #if onetime > 1:
        #    car += f'\n      <span id="onetime">Time to earn with one-time rewards: {int(onetime)+1} hours</span>'
        if grind > 1:
            car += f'\n        <span id="grind">Optimal grinding time to earn: {int(grind)+1} hours</span>'
        if play > 50:
            car += f'\n        <span id="play">Normal gameplay time to earn: {int(play)+1} hours 🤡</span>'
        elif play > 10:
            car += f'\n        <span id="play">Normal gameplay time to earn: {int(play)+1} hours 💀</span>'
        elif play > 3:
            car += f'\n        <span id="play">Normal gameplay time to earn: {int(play)+1} hours</span>'
        #if customrace > 3:
        #    car += f'\n      <span id="customrace">Number of <b>24 hour</b> custom races to earn: {int(customrace)+1}</span>'
        #if nordslaps > 25:
        #    car += f'\n      <span id="nordslaps">Gr.3 custom race Nordschleife laps to earn: {int(nordslaps)+1}</span>'

    estimatedays = 0
    maxestimatedays = 0
    daysvisible = 0
    if new:
        car += '\n        <span id="new">NEW</span>'
    if state == "normal":
        daysvisible = normal[carid]
        if carid in normal.keys() and normal[carid] > 0: # >0 checks for messed up data
            if normal[carid] <= 3:
                estimatedays = 6-normal[carid]
                maxestimatedays = 11-normal[carid]
                car += f'\n        <span id="days-estimate">Estimate: {estimatedays-1} to {maxestimatedays-1} More Days Remaining</span>'
            elif normal[carid] <= 7:
                estimatedays = 3
                maxestimatedays = 11-normal[carid]
                car += f'\n        <span id="days-estimate">Estimate: {estimatedays-1} to {maxestimatedays-1} More Days Remaining</span>'
            else:
                estimatedays = 3
                car += '\n        <span id="days-estimate">Limited Stock Soon<br>(2+ More Days Remaining)</span>'
    elif state == "limited":
        daysvisible = normal[carid] + limited[carid]
        if carid in limited.keys() and limited[carid] == 2:
            estimatedays = 1
            car += '\n        <span id="limited">Limited Stock</span><span id="days-remaining">Last Day Available</span>'
        elif carid in limited.keys() and limited[carid] == 1:
            estimatedays = 2
            car += '\n        <span id="limited">Limited Stock</span><span id="days-remaining">1 More Day Remaining</span>'
        else:
            estimatedays = 1
            car += '\n        <span id="limited">Limited Stock</span><span id="days-remaining">0 Days Remaining <small style="font-size: 9px;">This should be sold out...</small></span>'
    elif state == "soldout":
        estimatedays = 0
        car += '\n        <span id="dimmer"></span><span id="soldout">SOLD OUT</span>'

    if carid in rewards.keys():
        rewardinfo = rewards[carid]
        car +=  '\n        <span id="reward-text">REWARD<br>CAR</span>'
        rewardtype = ""
        match rewardinfo[0]:
            case "menubook":
                rewardtype = "Menu Book"
            case "license":
                rewardtype = "License:"
            case "mission":
                rewardtype = "Mission Set:"
        car += f'\n        <img id="reward-icon" src="img/open-book.svg" width="24" title="Reward from {rewardtype} {rewardinfo[1]}'
        if rewardinfo[2] != "-":
            car += f' All {rewardinfo[2].capitalize()}'
        car +=  '"/>'

    legendcars_section += car + '\n      </p>'
    jsondata["legend"]["cars"].append({
        "carid": carid, "manufacturer": manufacturer, "region": region, "name": name, "credits": int(cr),
        "state": state, "estimatedays": estimatedays, "maxestimatedays": maxestimatedays, "new": new, "daysvisible": daysvisible
    })

##################################################
# handle campaign rewards
##################################################
campaignrewards_section = ""
with open(f"campaign-rewards.html", encoding='utf-8') as f:
    campaignrewards_section = f.read()

##################################################
# handle engine swaps
##################################################
engineswaps_section = ""
with open(f"engine-swaps.html", encoding='utf-8') as f:
    engineswaps_section = f.read()

##################################################
# handle workout rewards
##################################################
workoutrewards_section = ""
with open(f"workout-reward-estimate.html", encoding='utf-8') as f:
    workoutrewards_section = f.read()

##################################################
# handle daily races
##################################################
dailyraces_section = ""

lines = [] # type: list[str]
with open(f"_data/dailyrace/{dailyracedir[-1]}") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

jsondata["dailyrace"] = {
    "date": dailyracedir[-1][:-4],
    "races": [],
}

letters = ["A", "B", "C"] # lmao

i = -1
for line in lines:
    i += 1
    if line == "\n":
        continue
    courseid,laps,cars,starttype,fuelcons,tyrewear,cartype,category,specificcars,widebodyban,nitrousban,tyres,bop,spec,carused,damage,shortcutpen,carcollisionpen,pitlanepen,time,offset = line.strip().split(",")
    track = coursedb_id_to_name(courseid)
    crsbase = coursedb_id_to_basename(courseid)
    logo = coursedb_id_to_logoname(courseid)
    region = coursedb_id_to_countrycode(courseid)

    widebodyban = widebodyban == "y"
    nitrousban = nitrousban == "y"
    bop = bop == "y"
    spec = spec == "y"
    carused = carused if carused != "n" else False
    damage = damage if damage != "n" else False
    shortcutpen = shortcutpen == "y"
    carcollisionpen = carcollisionpen == "y"
    pitlanepen = pitlanepen == "y"

    dailyrace = '<div class="dailyrace">'+dailyrace_template

    flag = f"img/pdi-flag.png" if region == "pdi" else f"https://flagcdn.com/h24/{region}.png"

    dailyrace = dailyrace.replace("%LETTER", letters[i])
    dailyrace = dailyrace.replace("%TRACKLOGO", logo)
    dailyrace = dailyrace.replace("%FLAG", flag)
    dailyrace = dailyrace.replace("%TRACKNAME", track)
    dailyrace = dailyrace.replace("%LAPS", laps)
    dailyrace = dailyrace.replace("%CARS", cars)
    dailyrace = dailyrace.replace("%STARTTYPE", "Grid Start" if starttype == "grid" else starttype.capitalize())
    dailyrace = dailyrace.replace("%FUELCONS", fuelcons)
    dailyrace = dailyrace.replace("%TYREWEAR", tyrewear)
    dailyrace = dailyrace.replace("%TIME", time)
    dailyrace = dailyrace.replace("%BOP", "Applicable" if bop else "no [TODO]")
    dailyrace = dailyrace.replace("%SPEC", "Specified" if spec else "no [TODO]")
    if carused == "garage":
        dailyrace = dailyrace.replace("%GARAGECAR", "Garage Car")
    elif carused == "rent":
        dailyrace = dailyrace.replace("%GARAGECAR", "Event-Specified Car")
    elif carused == "any":
        dailyrace = dailyrace.replace("%GARAGECAR", "Garage Car, Event-Specified Car")
    else:
        dailyrace = dailyrace.replace("%GARAGECAR", "ERROR: wtf???")
    dailyrace = dailyrace.replace("%DAMAGE", damage.capitalize() if damage else "Disabled")
    dailyrace = dailyrace.replace("%SHORTCUTPEN", "Enabled" if shortcutpen else "Disabled")
    dailyrace = dailyrace.replace("%COLLISIONPEN", "Enabled" if carcollisionpen else "Disabled")
    dailyrace = dailyrace.replace("%PITLANEPEN", "Enabled" if pitlanepen else "Disabled")

    mincheck = int(offset)
    schedule = ""
    scheduledata = []
    while mincheck < 60:
        schedule += f"XX:{mincheck:02}, "
        scheduledata.append(mincheck)
        mincheck += int(time)+5
    schedule = schedule[:-2]
    dailyrace = dailyrace.replace("%SCHEDULE", schedule)

    regulations = ''

    if cartype == "category":
        regulations += '\n        <span class="racedetailsection" id="regulations">'+\
                       '\n            <div class="racedetailheader" id="regulations">Regulations</div>'+\
                       '\n            <div class="racedetailrow">'+\
                       '\n                <span class="racedetaillabel" id="categorylabel">Category</span>'+\
                      f'\n                <span class="racedetailcontent" id="category">{category}</span>'+\
                       '\n            </div>'
    elif cartype == "specific":
        regulations += '\n        <span class="racedetailsection" id="specificcars">'+\
                       '\n            <div class="racedetailheader" id="specificcars">Regulations (Specified Car)</div>'
        x = 0
        for carid in specificcars.split("|"):
            car = cardb_id_to_name(carid)
            regulations += f'\n                <div class="racedetailrow"><span class="specifiedcar">{car}</span></div>'
            #if x == 0:
            #    regulations += '\n                <div class="racedetailrow">'
            #regulations += f'\n                    <span class="specifiedcar">{car}</span>'
            #x += 1
            #if x == 2:
            #    x = 0
            #    regulations += '\n                </div>'
        #if x != 0:
        #    regulations += '\n                </div>'
        regulations += '\n            </span>'+\
                       '\n        <span class="racedetailsection" id="regulations">'+\
                       '\n            <div class="racedetailheader" id="regulations">Regulations</div>'

    if widebodyban:
        regulations += '\n            <div class="racedetailrow">'+\
                       '\n                <span class="racedetaillabel" id="widebodylabel">Wide Body</span>'+\
                       '\n                <span class="racedetailcontent" id="widebody">Prohibited</span>'+\
                       '\n            </div>'
    if nitrousban:
        regulations += '\n            <div class="racedetailrow">'+\
                       '\n                <span class="racedetaillabel" id="nitrouslabel">Nitrous</span>'+\
                       '\n                <span class="racedetailcontent" id="nitrous">Cannot be Fitted</span>'+\
                       '\n            </div>'
    if tyres != "-":
        regulations += '\n            <div class="racedetailrow">'+\
                       '\n                <span class="racedetaillabel" id="">Tyre Choice</span>'+\
                      f'\n                <span class="racedetailcontent" id="">'
        for tyre in tyres.split("|"):
            regulations += f'<div class="tyre" id="{tyre}">{tyre}</div> '
        regulations = regulations[:-1] + '</span>\n            </div>'
    
    regulations += '\n        </span>'

    dailyrace = dailyrace.replace("%REGULATIONS", regulations)

    if bop:
        dailyrace += '<div class="boprace">BoP Race</div>'

    dailyrace += '\n</div>'
    dailyraces_section += dailyrace

    jsondata["dailyrace"]["races"].append({
        "courseid": courseid, "crsbase": crsbase, "track": track, "logo": f'img/track/{logo}.png', "region": region,
        "laps": int(laps), "cars": int(cars), "starttype": starttype, "fuelcons": int(fuelcons), "tyrewear": int(tyrewear),
        "cartype": cartype, "widebodyban": widebodyban, "nitrousban": nitrousban, "tyres": tyres.split("|"),
        "bop": bop, "carsettings_specified": spec, "garagecar": True if (carused == "garage" or carused == "both") else False, "carused": carused,
        "damage": damage, "shortcutpen": shortcutpen, "carcollisionpen": carcollisionpen, "pitlanepen": pitlanepen,
        "time": int(time), "offset": int(offset), "schedule": scheduledata
    })
    if cartype == "category":
        jsondata["dailyrace"]["races"][-1]["category"] = category
    elif cartype == "specific":
        jsondata["dailyrace"]["races"][-1]["specificcars_ids"] = specificcars.split("|")
        jsondata["dailyrace"]["races"][-1]["specificcars"] = list(map(cardb_id_to_name, jsondata["dailyrace"]["races"][-1]["specificcars_ids"]))

##################################################
# do replacements
##################################################
html = html.replace("%USEDCARS_UPDATESTRING", useddir[-1].replace(".csv", ""))
html = html.replace("%USEDCARS_SECTION", usedcars_section)
html = html.replace("%LEGENDCARS_UPDATESTRING", legenddir[-1].replace(".csv", ""))
html = html.replace("%LEGENDCARS_SECTION", legendcars_section)
html = html.replace("%CAMPAIGNREWARDS_SECTION", campaignrewards_section)
html = html.replace("%ENGINESWAPS_SECTION", engineswaps_section)
html = html.replace("%WORKOUTREWARDS_SECTION", workoutrewards_section)
html = html.replace("%MENUBOOKUSEDCARS_SECTION", "Coming very soon!")
html = html.replace("%DAILYRACES_SECTION", dailyraces_section)
#html = html.replace("%BOP_SECTION", "Coming soon! (Well, probably after economy changes make obtaining Gr.3 cars more reasonable.)<br>In the meantime, you can reference Gran Turismo Sport's BoP here:")

##################################################
# output built html & json data
##################################################
from time import sleep

if os.path.exists("build"):
    shutil.rmtree("build")
    sleep(1) # build folder is so large we need to delay now (windows moment)
os.mkdir("build")
os.mkdir("build/cars")
with open("build/index.html", "w", encoding='utf-8') as f:
    f.write(html)
with open(f"build/data.json", "w") as f:
    json.dump(jsondata, f)

FILES_TO_COPY = ["style-220425.css"]
FOLDERS_TO_COPY = ["fonts", "img"]

for file in FILES_TO_COPY:
    shutil.copyfile(f"{file}", f"build/{file}")
for folder in FOLDERS_TO_COPY:
    shutil.copytree(f"{folder}", f"build/{folder}")

##################################################
# per car data
##################################################

for line in db_cars:
    id, _, _ = line.strip().split(",")
    id = int(id)
    if cardata_exists(id):
        cardata_plot(id)