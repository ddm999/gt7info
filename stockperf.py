import json
from db import *

html = ""
with open("stock-perf.html", "r", encoding='utf-8') as f:
    html = f.read()

perf_template = ""
with open("stock-perf-car.html", "r", encoding='utf-8') as f:
    perf_template = f.read()

##################################################
# run through sections
##################################################
perf_section = ""
jsondata = {"stockperf": []}
csvdata = "carid,manufacturer,name,group,CH,CM,CS,SH,SM,SS,RH,RM,RS,IM,W,D\n"

carids = cargrpdb_list_ids_from_group("N")
carids.extend(cargrpdb_list_ids_from_group("X"))

sorted_carids = sorted(carids, key=lambda x:float(stockperfdb_id_to_pp_dict(x)["SS"]), reverse=True)
for carid in sorted_carids:
    perf_car = perf_template

    ppdict = stockperfdb_id_to_pp_dict(carid)
    manufacturer = cardb_id_to_makername(carid)
    name = cardb_id_to_name(carid)
    group = cargrpdb_id_to_group(carid)

    perf_car = perf_car.replace("%CAR_MANU", manufacturer)
    perf_car = perf_car.replace("%CAR_NAME", name)
    perf_car = perf_car.replace("%CAR_GROUP", f"<b><i>{group}</i></b>" if group == "X" else group)
    perf_car = perf_car.replace("%CAR_CH", ppdict["CH"])
    perf_car = perf_car.replace("%CAR_CM", ppdict["CM"])
    perf_car = perf_car.replace("%CAR_CS", ppdict["CS"])
    perf_car = perf_car.replace("%CAR_SH", ppdict["SH"])
    perf_car = perf_car.replace("%CAR_SM", ppdict["SM"])
    perf_car = perf_car.replace("%CAR_SS", ppdict["SS"])
    perf_car = perf_car.replace("%CAR_RH", ppdict["RH"])
    perf_car = perf_car.replace("%CAR_RM", ppdict["RM"])
    perf_car = perf_car.replace("%CAR_RS", ppdict["RS"])
    perf_car = perf_car.replace("%CAR_IM", ppdict["IM"])
    perf_car = perf_car.replace("%CAR_W", ppdict["W"])

    perf_section += perf_car

    jsondata["stockperf"].append({
        "carid": carid, "manufacturer": manufacturer,
        "name": name, "group": group, "PP": ppdict
    })
    csvdata += f'{carid},{manufacturer},{name},{group},'+\
               f'{ppdict["CH"]},{ppdict["CM"]},{ppdict["CS"]},'+\
               f'{ppdict["SH"]},{ppdict["SM"]},{ppdict["SS"]},'+\
               f'{ppdict["RH"]},{ppdict["RM"]},{ppdict["RS"]},'+\
               f'{ppdict["IM"]},{ppdict["W"]},{ppdict["D"]}\n'

html = html.replace("%CAR_PERFS", perf_section)

with open("build/stock-perf.html", "w") as f:
    f.write(html)

with open(f"build/data-stock-perf.json", "w") as f:
    json.dump(jsondata, f)

with open("build/data-stock-perf.csv", "w") as f:
    f.write(csvdata)
