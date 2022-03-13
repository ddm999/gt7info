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

##################################################
# handle used car dealership
##################################################
lines = [] # type: list[str]
with open(f"_data/used/{LAST_UPDATE}.csv") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

usedcars_section = ""
for line in lines:
    if line == "\n":
        continue
    data = line.strip().split(",")
    manufacturer_orig, name, cr, state = data
    manufacturer = manufacturer_orig.strip().upper()
    car = '<p id="car">\n'+used_template
    region = manufacturer_to_region(manufacturer)
    car = car.replace("%REGION", region)
    car = car.replace("%MANUFACTURER", manufacturer)
    car = car.replace("%NAME", name)
    car = car.replace("%CREDITS", f"{int(cr):,}")
    if state == "limited":
        car += '\n      <span id="limited">Limited Stock</span>'
    elif state == "soldout":
        car += '\n      <span id="dimmer"></span><span id="soldout">SOLD OUT</span>'
    usedcars_section += f'{car}\n      </p>'

##################################################
# handle legend car dealership
##################################################
lines = [] # type: list[str]
with open(f"_data/legend/{LAST_UPDATE}.csv") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

legendcars_section = ""
for line in lines:
    if line == "\n":
        continue
    data = line.strip().split(",")
    manufacturer_orig, name, cr, state = data
    manufacturer = manufacturer_orig.strip()
    car = '<p id="lcar">\n'+legend_template
    region = manufacturer_to_region(manufacturer.upper())
    car = car.replace("%REGION", region)
    car = car.replace("%MANUFACTURER", manufacturer)
    car = car.replace("%NAME", name)
    car = car.replace("%CREDITS", f"{int(cr):,}")
    if state == "limited":
        car += '\n<span id="limited">Limited Stock</span>'
    elif state == "soldout":
        car += '\n<span id="soldout">SOLD OUT</span>'
    car += '\n</p>'
    legendcars_section += car + '\n'

##################################################
# do replacements
##################################################
html = html.replace("%USEDCARS_UPDATESTRING", LAST_UPDATE)
html = html.replace("%USEDCARS_SECTION", usedcars_section)
html = html.replace("%LEGENDCARS_UPDATESTRING", LAST_UPDATE)
html = html.replace("%LEGENDCARS_SECTION", legendcars_section)
html = html.replace("%CAMPAIGNREWARDS_SECTION", "Coming soon! In the meantime, check:")
html = html.replace("%ENGINESWAPS_SECTION", "Coming soon! In the meantime, check:")

##################################################
# output built html
##################################################
if os.path.exists("build"):
    shutil.rmtree("build")
os.mkdir("build")
with open("build/index.html", "w") as f:
    f.write(html)

FILES_TO_COPY = ["style-220313.css", "legend-hagerty.svg", "legend-hagerty-icon.svg", "ucd-auto.svg"]
FOLDERS_TO_COPY = ["fonts"]

for file in FILES_TO_COPY:
    shutil.copyfile(f"{file}", f"build/{file}")
for folder in FOLDERS_TO_COPY:
    shutil.copytree(f"{folder}", f"build/{folder}")
