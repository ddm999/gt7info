import os, shutil, json
from datetime import datetime, timezone
from cardata import *
from db import *
from math import floor

GT_VERSION = 1.29 #NOTE: IF THIS GOES ABOVE x.59, SCREAM AND ADJUST THE CODE
DATA_VERSION = 1
BUILD_TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")

version_hack_hour = floor(GT_VERSION)
version_hack_minute = floor((GT_VERSION - version_hack_hour) * 100)
version_hack_second = floor(DATA_VERSION)
jsondata = {
    "updatetimestamp": datetime.now().strftime(f"%Y-%m-%d {version_hack_hour:02d}:{version_hack_minute:02d}:{version_hack_second:02d}")
}

html = ""
with open("index.html", "r", encoding='utf-8') as f:
    html = f.read()

html = html.replace("%BUILD_TIMESTAMP", BUILD_TIMESTAMP)

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
# handle rewards, engine swaps, lottery cars, trophy cars
##################################################
lines = []
with open(f"_data/rewards/{os.listdir('_data/rewards')[-1]}") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

rewards = {}
for reward in lines:
    rewardsplit = reward.strip().split(",")
    rewards[rewardsplit[0]] = rewardsplit[1:]

lines = []
with open(f"_data/db/engineswaps.csv") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

engineswaps = {}
for engineswap in lines:
    engineswapsplit = engineswap.strip().split(",")
    engineswaps[engineswapsplit[0]] = engineswapsplit[1:]

lines = []
with open(f"_data/db/lotterycars.csv") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

lotterycars = {}
for lotterycar in lines:
    lotterycarsplit = lotterycar.strip().split(",")
    if lotterycarsplit[0] != "B":
        lotterycars[lotterycarsplit[1]] = lotterycarsplit[0]

lines = []
with open(f"_data/db/trophy.csv") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

trophycars = {}
for trophycar in lines:
    trophycarsplit = trophycar.strip().split(",")
    trophycars[trophycarsplit[1]] = trophycarsplit[0]

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

for i in range(len(useddir)):
    morelines = []
    with open(f"_data/used/{useddir[-1-i]}") as f:
        morelines = f.readlines()
    morelines = morelines[1:] # remove headers

    for car in morelines:
        carsplit = car.strip().split(",")
        cardata_add("used", useddir[-1-i].replace('.csv',''), carsplit)

usedcars_section = ""
for line in lines:
    if line == "\n":
        continue
    carid, cr, state, daysremaining = line.strip().split(",")
    daysremaining = int(daysremaining)
    name = cardb_id_to_name(carid)
    manufacturer = cardb_id_to_makername(carid)
    region = cardb_id_to_countrycode(carid)

    #HACK for cars that go through bad state changes
    fucked = False
    if int(carid) == 999999:
        fucked = True
    #HACK end

    if state == "new":
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

    if state == "new":
        car += '\n        <span id="new">NEW</span>'
    elif state == "limited":
        car += '\n        <span id="limited">Limited Stock</span>'
    elif state == "soldout":
        car += '\n        <span id="soldout">SOLD OUT</span>'

    if not fucked:
        if daysremaining > 3:
            car += f'\n        <span id="days-estimate">Available For {daysremaining-1} More Days</span>'
        elif daysremaining == 3:
            car += f'\n        <span id="days-remaining">Available For 1 More Day</span>'
        elif daysremaining == 2:
            car += f'\n        <span id="days-remaining">Last Day Available</span>'
        elif daysremaining == -1:
            car += f'\n        <span id="days-estimate">No Estimate Available</span>'
    else:
        car += f'\n        <span id="days-estimate">No Estimate Available</span>'

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

    if carid in engineswaps.keys():
        engineswapinfo = engineswaps[carid]
        car +=  '\n        <span id="engineswap-text">ENGINE<br>SWAP</span>'+\
               f'\n        <img id="engineswap-icon" src="img/engine.svg" width="24" title="Supports engine swap: {engineswapinfo[1]} from {cardb_id_to_name(engineswapinfo[0])}"/>'

    if carid in lotterycars.keys():
        lotterycarinfo = lotterycars[carid]
        lotterystars = ""
        match lotterycarinfo:
            case "L":
                lotterystars = "4/5/6"
            case "M":
                lotterystars = "3/4/5"
            case "S":
                lotterystars = "1/2/3/4"
        car +=  '\n        <span id="lottery-text">TICKET<br>REWARD</span>'+\
               f'\n        <img id="lottery-icon" src="img/gift.svg" width="24" title="Can be won from {lotterystars} star tickets. Special parts for this car can be recieved from 4/5 star tickets."/>'

    if carid in trophycars.keys():
        trophyname = trophycars[carid]
        car +=  '\n        <span id="trophy-text">TROPHY<br>REQ.</span>'+\
               f'\n        <img id="trophy-icon" src="img/trophy.svg" width="24" title="Must be owned to earn the {trophyname} trophy."/>'

    usedcars_section += f'{car}\n      </p>'
    jsondata["used"]["cars"].append({
        "carid": carid, "manufacturer": manufacturer, "region": region, "name": name, "credits": int(cr),
        "state": "normal" if state == "new" else state, "estimatedays": daysremaining-1, "maxestimatedays": daysremaining-1, "new": state == "new"
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

for i in range(len(legenddir)):
    morelines = []
    with open(f"_data/legend/{legenddir[-1-i]}") as f:
        morelines = f.readlines()
    morelines = morelines[1:] # remove headers

    for car in morelines:
        carsplit = car.strip().split(",")
        cardata_add("legend", legenddir[-1-i].replace('.csv',''), carsplit)

legendcars_section = ""
for line in lines:
    if line == "\n":
        continue
    carid, cr, state, daysremaining = line.strip().split(",")
    daysremaining = int(daysremaining)
    name = cardb_id_to_name(carid)
    manufacturer = cardb_id_to_makername(carid)
    region = cardb_id_to_countrycode(carid)

    if state == "new":
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
    #if state != "soldout":
        #if onetime > 1:
        #    car += f'\n      <span id="onetime">Time to earn with one-time rewards: {int(onetime)+1} hours</span>'
        #if grind > 1:
        #    car += f'\n        <span id="grind">Optimal grinding time to earn: {int(grind)+1} hours</span>'
        #if play > 50:
        #    car += f'\n        <span id="play">Normal gameplay time to earn: {int(play)+1} hours 🤡</span>'
        #elif play > 10:
        #    car += f'\n        <span id="play">Normal gameplay time to earn: {int(play)+1} hours 💀</span>'
        #elif play > 3:
        #    car += f'\n        <span id="play">Normal gameplay time to earn: {int(play)+1} hours</span>'
        #if customrace > 3:
        #    car += f'\n      <span id="customrace">Number of <b>24 hour</b> custom races to earn: {int(customrace)+1}</span>'
        #if nordslaps > 25:
        #    car += f'\n      <span id="nordslaps">Gr.3 custom race Nordschleife laps to earn: {int(nordslaps)+1}</span>'

    
    if state == "new":
        car += '\n        <span id="new">NEW</span>'
    elif state == "limited":
        car += '\n        <span id="limited">Limited Stock</span>'
    elif state == "soldout":
        car += '\n        <span id="soldout">SOLD OUT</span>'

    if not fucked:
        if daysremaining > 3:
            car += f'\n        <span id="days-estimate">Available For {daysremaining-1} More Days</span>'
        elif daysremaining == 3:
            car += f'\n        <span id="days-remaining">Available For 1 More Day</span>'
        elif daysremaining == 2:
            car += f'\n        <span id="days-remaining">Last Day Available</span>'
        elif daysremaining == -1:
            car += f'\n        <span id="days-estimate">No Estimate Available</span>'
    else:
        car += f'\n        <span id="days-estimate">No Estimate Available</span>'

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

    if carid in engineswaps.keys():
        engineswapinfo = engineswaps[carid]
        car +=  '\n        <span id="engineswap-text">ENGINE<br>SWAP</span>'+\
               f'\n        <img id="engineswap-icon" src="img/engine-lcd.svg" width="24" title="Supports engine swap: {engineswapinfo[1]} from {cardb_id_to_name(engineswapinfo[0])}"/>'

    if carid in trophycars.keys():
        trophyname = trophycars[carid]
        car +=  '\n        <span id="trophy-text">TROPHY<br>REQ.</span>'+\
               f'\n        <img id="trophy-icon" src="img/trophy.svg" width="24" title="Must be owned to earn the {trophyname} trophy."/>'

    legendcars_section += car + '\n      </p>'
    jsondata["legend"]["cars"].append({
        "carid": carid, "manufacturer": manufacturer, "region": region, "name": name, "credits": int(cr),
        "state": "normal" if state == "new" else state, "estimatedays": daysremaining-1, "maxestimatedays": daysremaining-1, "new": state == "new"
    })

##################################################
# handle html injects
##################################################
engineswaps_section = ""
with open(f"engine-swaps.html", encoding='utf-8') as f:
    engineswaps_section = f.read()

ticketrewards_section = ""
with open(f"ticket-rewards.html", encoding='utf-8') as f:
    ticketrewards_section = f.read()

menubookusedcars_section = ""
with open(f"menu-book-used.html", encoding="utf-8") as f:
    menubookusedcars_section = f.read()

##################################################
# handle daily races
##################################################
"""
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
    courseid,laps,cars,starttype,fuelcons,tyrewear,cartype,category,specificcars,widebodyban,nitrousban,tyres,requiredtyres,bop,spec,carused,damage,shortcutpen,carcollisionpen,pitlanepen,time,offset = line.strip().split(",")
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
    dailyrace = dailyrace.replace("%STARTTYPE", "Grid Start" if starttype == "grid" else ("Grid with False Start Check" if starttype == "grid_with_false_start" else "Rolling Start"))
    dailyrace = dailyrace.replace("%FUELCONS", fuelcons)
    dailyrace = dailyrace.replace("%TYREWEAR", tyrewear)
    dailyrace = dailyrace.replace("%TIME", time)
    dailyrace = dailyrace.replace("%BOP", "On" if bop else "Off")
    dailyrace = dailyrace.replace("%SPEC", "Specified" if spec else "Allowed")
    if carused == "garage":
        dailyrace = dailyrace.replace("%GARAGECAR", "Garage Car")
    elif carused == "rent":
        dailyrace = dailyrace.replace("%GARAGECAR", "Event-Specified Car")
    elif carused == "any":
        dailyrace = dailyrace.replace("%GARAGECAR", "Garage Car, Event-Specified Car")
    else:
        dailyrace = dailyrace.replace("%GARAGECAR", "ERROR: wtf???")
    dailyrace = dailyrace.replace("%DAMAGE", damage.capitalize() if damage else "Disabled")
    dailyrace = dailyrace.replace("%SHORTCUTPEN", "Light" if shortcutpen else "Disabled")
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
    
    #HACK: todo, actual "no dr/sr updates" support
    if i == 0:
        regulations += '\n        <span class="racedetailrow"><span class="specifiedcar" style="color: #fe2;">No DR / SR Updates</span></span>'
        #regulations += '\n        <span class="racedetailrow"><span class="specifiedcar" style="color: #271;">DR / SR Updates enabled</span></span>'

    if cartype == "specific" or cartype == "both" or cartype == "specific_tuninglimits":
        regulations += '\n        <span class="racedetailsection" id="specificcars">'+\
                       '\n            <div class="racedetailheader" id="specificcars">Regulations (Specified Car)</div>'
        x = 0
        for carid in specificcars.split("|"):
            car = cardb_id_to_name(carid)

            #HACK: rental hack
            if carid in []:
                regulations += f'\n                <div class="racedetailrow"><span class="specifiedcar">{car}</span> [CANNOT BE RENTED]</div>'
            else:
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
        regulations += '\n        </span>'

    regulations += '\n        <span class="racedetailsection" id="regulations">'+\
                   '\n            <div class="racedetailheader" id="regulations">Regulations</div>'

    if cartype == "category" or cartype == "both":
        regulations += '\n            <div class="racedetailrow">'+\
                       '\n                <span class="racedetaillabel" id="categorylabel">Category</span>'+\
                      f'\n                <span class="racedetailcontent" id="category">{category}</span>'+\
                       '\n            </div>'
    elif cartype == "pp":
        regulations += '\n            <div class="racedetailrow">'+\
                       '\n                <span class="racedetaillabel" id="categorylabel">Car Type</span>'+\
                      f'\n                <span class="racedetailcontent" id="category">{category}</span>'+\
                       '\n            </div>'
        regulations += '\n            <div class="racedetailrow">'+\
                       '\n                <span class="racedetaillabel" id="categorylabel">PP</span>'+\
                      f'\n                <span class="racedetailcontent" id="category">{specificcars} or less</span>'+\
                       '\n            </div>'
    elif cartype == "dt_tuninglimits":
        splitcategory = category.split("|")
        if len(splitcategory) == 5:
            cartag, PSpower, HPpower, KGweight, LBweight = splitcategory
            regulations += '\n            <div class="racedetailrow">'+\
                           '\n                <span class="racedetaillabel" id="categorylabel">Car Type</span>'+\
                          f'\n                <span class="racedetailcontent" id="category">{cartag}</span>'+\
                           '\n            </div>'
            regulations += '\n            <div class="racedetailrow">'+\
                           '\n                <span class="racedetaillabel" id="categorylabel">Drivetrain</span>'+\
                          f'\n                <span class="racedetailcontent" id="category">{specificcars}</span>'+\
                           '\n            </div>'
            regulations += '\n            <div class="racedetailrow">'+\
                           '\n                <span class="racedetaillabel" id="categorylabel">Power</span>'+\
                          f'\n                <span class="racedetailcontent" id="category">{PSpower} PS or less / {HPpower} HP or less</span>'+\
                           '\n            </div>'
            regulations += '\n            <div class="racedetailrow">'+\
                           '\n                <span class="racedetaillabel" id="categorylabel">Weight</span>'+\
                          f'\n                <span class="racedetailcontent" id="category">At least {KGweight} kg / At least {LBweight} lbs.</span>'+\
                           '\n            </div>'
    elif cartype == "specific_tuninglimits":
        splitcategory = category.split("|")
        if len(splitcategory) == 4:
            PSpower, HPpower, KGweight, LBweight = splitcategory
            regulations += '\n            <div class="racedetailrow">'+\
                           '\n                <span class="racedetaillabel" id="categorylabel">Power</span>'+\
                          f'\n                <span class="racedetailcontent" id="category">{PSpower} PS or less / {HPpower} HP or less</span>'+\
                           '\n            </div>'
            regulations += '\n            <div class="racedetailrow">'+\
                           '\n                <span class="racedetaillabel" id="categorylabel">Weight</span>'+\
                          f'\n                <span class="racedetailcontent" id="category">At least {KGweight} kg / At least {LBweight} lbs.</span>'+\
                           '\n            </div>'


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
    if requiredtyres != "-":
        regulations += '\n            <div class="racedetailrow">'+\
                       '\n                <span class="racedetaillabel" id="">Required Tyre Type</span>'+\
                      f'\n                <span class="racedetailcontent" id="">'
        for tyre in requiredtyres.split("|"):
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
        "cartype": cartype, "widebodyban": widebodyban, "nitrousban": nitrousban, "tyres": tyres.split("|"), "requiredtyres": requiredtyres.split("|"),
        "bop": bop, "carsettings_specified": spec, "garagecar": True if (carused == "garage" or carused == "both") else False, "carused": carused,
        "damage": damage, "shortcutpen": shortcutpen, "carcollisionpen": carcollisionpen, "pitlanepen": pitlanepen,
        "time": int(time), "offset": int(offset), "schedule": scheduledata
    })
    if cartype == "category" or cartype == "both":
        jsondata["dailyrace"]["races"][-1]["category"] = category
    if cartype == "specific" or cartype == "both" or cartype == "specific_tuninglimits":
        jsondata["dailyrace"]["races"][-1]["specificcars_ids"] = specificcars.split("|")
        jsondata["dailyrace"]["races"][-1]["specificcars"] = list(map(cardb_id_to_name, jsondata["dailyrace"]["races"][-1]["specificcars_ids"]))
    if cartype == "pp":
        jsondata["dailyrace"]["races"][-1]["cartags"] = category
        jsondata["dailyrace"]["races"][-1]["pplimit"] = specificcars
    if cartype == "dt_tuninglimits":
        jsondata["dailyrace"]["races"][-1]["cartags"] = cartag
        jsondata["dailyrace"]["races"][-1]["drivetrainlimit"] = specificcars
    if cartype == "specific_tuninglimits" or cartype == "dt_tuninglimits":
        jsondata["dailyrace"]["races"][-1]["pslimit"] = PSpower
        jsondata["dailyrace"]["races"][-1]["kglimit"] = KGweight
"""

jsondata["dailyrace"] = {
    "date": "70-01-01",
    "races": [],
}

for i in range(3):
    jsondata["dailyrace"]["races"].append({
        "courseid": 0, "crsbase": "No Longer Updated", "track": "No Longer Updated", "logo": f'img/track/nothing.png', "region": "pd",
        "laps": 0, "cars": 0, "starttype": "You can check Twitter instead: @Nenkaai the weekend before & @Mistah_MCA at the start of a week", "fuelcons": 0, "tyrewear": 0,
        "cartype": "category", "widebodyban": False, "nitrousban": False, "tyres": [], "requiredtyres": [],
        "bop": False, "carsettings_specified": False, "garagecar": False, "carused": False,
        "damage": False, "shortcutpen": False, "carcollisionpen": False, "pitlanepen": False,
        "time": 0, "offset": 0, "schedule": "Tell your bot author to stop trying to get daily races :)"
    })
##################################################
# do replacements
##################################################
html = html.replace("%USEDCARS_UPDATESTRING", useddir[-1].replace(".csv", ""))
html = html.replace("%USEDCARS_SECTION", usedcars_section)
html = html.replace("%LEGENDCARS_UPDATESTRING", legenddir[-1].replace(".csv", ""))
html = html.replace("%LEGENDCARS_SECTION", legendcars_section)
html = html.replace("%ENGINESWAPS_SECTION", engineswaps_section)
html = html.replace("%TICKETREWARDS_SECTION", ticketrewards_section)
html = html.replace("%MENUBOOKUSEDCARS_SECTION", menubookusedcars_section)
html = html.replace("%DAILYRACES_UPDATESTRING", dailyracedir[-1].replace(".csv", ""))
#html = html.replace("%DAILYRACES_SECTION", dailyraces_section)
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

FILES_TO_COPY = ["course-bop.html", "campaign-rewards.html", "engine-swaps.html", "gr1-hybrid-info.html", "menu-book-used.html", "ticket-rewards.html", "legacy-changes.html", "style.css", "style-simple.css"]
FOLDERS_TO_COPY = ["fonts", "img", "_data"]

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