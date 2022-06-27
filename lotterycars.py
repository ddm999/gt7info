from db import *

html = ""
with open("lottery-cars.html", "r", encoding='utf-8') as f:
    html = f.read()

lines = []
with open(f"_data/db/lotterycars.csv") as f:
    lines = f.readlines()
lines = lines[1:] # remove headers

cars_s = []
cars_m = []
cars_l = []
for lotterycar in lines:
    lotterycarsplit = lotterycar.strip().split(",")
    cars = []
    match lotterycarsplit[0]:
        case "L":
            cars = cars_l
        case "M":
            cars = cars_m
        case "S":
            cars = cars_s
    cars.append(f"{cardb_id_to_makername(lotterycarsplit[1])} {cardb_id_to_name(lotterycarsplit[1])}")

cars_s = sorted(cars_s)
cars_m = sorted(cars_m)
cars_l = sorted(cars_l)

section_s = ""
for car in cars_s:
    section_s += f"<li>{car}</li>\n"
section_m = ""
for car in cars_m:
    section_m += f"<li>{car}</li>\n"
section_l = ""
for car in cars_l:
    section_l += f"<li>{car}</li>\n"

html = html.replace("%LOTTERY_CAR_S", section_s)
html = html.replace("%LOTTERY_CAR_M", section_m)
html = html.replace("%LOTTERY_CAR_L", section_l)

with open("build/lottery-cars.html", "w") as f:
    f.write(html)