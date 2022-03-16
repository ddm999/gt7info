import os, shutil
from config import LAST_UPDATE

##################################################
# get region code from manufacturer name
##################################################
def manufacturer_to_region(manu : str):
    match manu:
        case "GRAN TURISMO" | "GT AWARDS (SEMA)":
            return "" # 0
        case "DAIHATSU" | "HONDA" | "MAZDA" | "MITSUBISHI" | "NISSAN" | "SUBARU" |\
                "SUZUKI" | "TOYOTA" | "INFINITI" | "LEXUS" | "AMUSE" | "RE AMEMIYA" |\
                "SUPER FORMULA" | "GREDDY":
            return "jp" #  2
        case "CHEVROLET" | "DODGE" | "FORD" | "SHELBY" | "PONTIAC" | "PLYMOUTH" | "DMC" |\
                "CHAPARRAL" | "TESLA" | "SRT" | "FITTIPALDI MOTORS" | "WILLYS" | "JEEP" |\
                "CHRIS HOLSTROM CONCEPTS" | "ECKERT'S ROD & CUSTOM" | "WICKED FABRICATION":
            return "us" #  3
        case "ASTON MARTIN" | "JAGUAR" | "TVR" | "MINI" | "CATERHAM" | "MCLAREN" |\
                "RADICAL" | "BAC":
            return "gb" #  4
        case "AUDI" | "BMW" | "MERCEDES-BENZ" | "RUF" | "VOLKSWAGEN" | "BUGATTI" |\
                "PORSCHE" | "AMG":
            return "de" #  5
        case "CITROEN" | "PEUGEOT" | "RENAULT" | "ALPINE" | "RENAULT SPORT" | "DS AUTOMOBILES":
            return "fr" #  6
        case "ALFA ROMEO" | "FIAT" | "LANCIA" | "PAGANI" | "AUTOBIANCHI" | "FERRARI" |\
                "LAMBORGHINI" | "MASERATI" | "ABARTH" | "ZAGATO" | "DE TOMASO":
            return "it" #  7
        case "HYUNDAI" | "GENESIS":
            return "kr" #  9
        case "KTM":
            return "at" # 15
        case _:
            raise ValueError(f"{manu=}")

html = ""
with open("index.html", "r") as f:
    html = f.read()

used_template = ""
with open("used.html", "r") as f:
    used_template = f.read()

legend_template = ""
with open("legend.html", "r") as f:
    legend_template = f.read()

legenddir = os.listdir("_data/legend")
useddir = os.listdir("_data/used")
legenddir.sort()
useddir.sort()
useddir.remove("starter.csv")
##################################################
# handle used car dealership
##################################################
lines = [] # type: list[str]
with open(f"_data/used/{useddir[-1]}") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

normal = {} # type: dict[str, int]
limited = {} # type: dict[str, int]
for car in lines:
    carsplit = car.strip().split(",")
    # days appeared, negative means still counting
    if carsplit[3] == "normal":
        normal[carsplit[1]] = -1
    elif carsplit[3] == "limited":
        limited[carsplit[1]] = -1

for i in range(len(useddir)-1):
    morelines = []
    with open(f"_data/used/{useddir[-2-i]}") as f:
        morelines = f.readlines()
    morelines = morelines[1:] # remove headers

    carnames = {}
    for car in morelines:
        carsplit = car.strip().split(",")
        carnames[carsplit[1]] = carsplit[3]

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

usedcars_section = ""
for line in lines:
    if line == "\n":
        continue
    data = line.strip().split(",")
    manufacturer_orig, name, cr, state = data
    manufacturer = manufacturer_orig.strip().upper()
    region = manufacturer_to_region(manufacturer)

    new = state == "normal" and name in normal.keys() and normal[name] == 1
    if new:
        car = '<p class="car carnew">\n'+used_template
    elif state == "limited":
        car = '<p class="car carlimited">\n'+used_template
    elif state == "soldout":
        car = '<p class="car carsold">\n'+used_template
    else:
        car = '<p class="car">\n'+used_template

    car = car.replace("%REGION", region)
    car = car.replace("%MANUFACTURER", manufacturer)
    car = car.replace("%NAME", name)
    car = car.replace("%CREDITS", f"{int(cr):,}")
    if new:
        car += '\n      <span id="new">NEW</span>'
    if state == "normal":
        if name in normal.keys() and normal[name] > 0: # >0 checks for messed up data
            if normal[name] <= 5:
                car += f'\n      <span id="days-estimate">Estimate: {7-normal[name]} More Days Remaining</span>'
            else:
                car += '\n      <span id="days-estimate">Estimate: Limited Stock Soon</span>'
    elif state == "limited":
        if name in limited.keys() and limited[name] == 2:
            car += '\n      <span id="limited">Limited Stock</span><span id="days-remaining">Last Day Available</span>'
        elif name in limited.keys() and limited[name] == 1:
            car += '\n      <span id="limited">Limited Stock</span><span id="days-remaining">1 More Day Remaining</span>'
        else:
            car += '\n      <span id="limited">Limited Stock</span>'
    elif state == "soldout":
        car += '\n      <span id="dimmer"></span><span id="soldout">SOLD OUT</span>'
    usedcars_section += f'{car}\n      </p>'

##################################################
# handle legend car dealership
##################################################
lines = [] # type: list[str]
with open(f"_data/legend/{legenddir[-1]}") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

normal = {} # type: dict[str, int]
limited = {} # type: dict[str, int]
for car in lines:
    carsplit = car.strip().split(",")
    # days appeared, negative means still counting
    if carsplit[3] == "normal":
        normal[carsplit[1]] = -1
    elif carsplit[3] == "limited":
        limited[carsplit[1]] = -1

for i in range(len(legenddir)-1):
    morelines = []
    with open(f"_data/legend/{legenddir[-2-i]}") as f:
        morelines = f.readlines()
    morelines = morelines[1:] # remove headers

    carnames = {}
    for car in morelines:
        carsplit = car.strip().split(",")
        carnames[carsplit[1]] = carsplit[3]

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

legendcars_section = ""
for line in lines:
    if line == "\n":
        continue
    data = line.strip().split(",")
    manufacturer_orig, name, cr, state = data
    manufacturer = manufacturer_orig.strip()

    new = state == "normal" and name in normal.keys() and normal[name] == 1
    if new:
        car = '<p class="lcar carnew">\n'+legend_template
    elif state == "limited":
        car = '<p class="lcar carlimited">\n'+legend_template
    elif state == "soldout":
        car = '<p class="lcar carsold">\n'+legend_template
    else:
        car = '<p class="lcar">\n'+legend_template

    car = car.replace("%MANUFACTURER", manufacturer)
    car = car.replace("%NAME", name)
    car = car.replace("%CREDITS", f"{int(cr):,}")
    if new:
        car += '\n      <span id="new">NEW</span>'
    if state == "normal":
        if name in normal.keys() and normal[name] > 0: # >0 checks for messed up data
            if normal[name] <= 5:
                car += f'\n      <span id="days-estimate">Estimate: {7-normal[name]} More Days Remaining</span>'
            else:
                car += '\n      <span id="days-estimate">Estimate: Limited Stock Soon</span>'
    elif state == "limited":
        if name in limited.keys() and limited[name] == 2:
            car += '\n      <span id="limited">Limited Stock</span><span id="days-remaining">Last Day Available</span>'
        elif name in limited.keys() and limited[name] == 1:
            car += '\n      <span id="limited">Limited Stock</span><span id="days-remaining">1 More Day Remaining</span>'
        else:
            car += '\n      <span id="limited">Limited Stock</span>'
    elif state == "soldout":
        car += '\n      <span id="dimmer"></span><span id="soldout">SOLD OUT</span>'
    car += '\n</p>'
    legendcars_section += car + '\n'

##################################################
# do replacements
##################################################
html = html.replace("%USEDCARS_UPDATESTRING", useddir[-1].replace(".csv", ""))
html = html.replace("%USEDCARS_SECTION", usedcars_section)
html = html.replace("%LEGENDCARS_UPDATESTRING", legenddir[-1].replace(".csv", ""))
html = html.replace("%LEGENDCARS_SECTION", legendcars_section)
html = html.replace("%CAMPAIGNREWARDS_SECTION", "Coming soon!<br>In the meantime, check:")
html = html.replace("%ENGINESWAPS_SECTION", "Coming soon!<br>In the meantime, check:")
html = html.replace("%GAMEISSUES_SECTION", "Coming soon!<br>In the meantime, check issues known by the developers here:")
html = html.replace("%DAILYRACES_SECTION", "Coming soon!<br>Sorry, I don't know anywhere that provides just this data right now. Check GTPlanet news?")
html = html.replace("%BOP_SECTION", "Coming soon!<br>In the meantime, you can reference Gran Turismo Sport's BoP here:")

##################################################
# output built html
##################################################
if os.path.exists("build"):
    shutil.rmtree("build")
os.mkdir("build")
with open("build/index.html", "w") as f:
    f.write(html)

FILES_TO_COPY = ["style-220315.css", "legend-hagerty.svg", "legend-hagerty-icon.svg", "ucd-auto.svg"]
FOLDERS_TO_COPY = ["fonts"]

for file in FILES_TO_COPY:
    shutil.copyfile(f"{file}", f"build/{file}")
for folder in FOLDERS_TO_COPY:
    shutil.copytree(f"{folder}", f"build/{folder}")
