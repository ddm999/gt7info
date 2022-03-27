import os
from db import *

useddir = os.listdir("_data/used")
useddir.sort()
useddir.remove("starter.csv")

legenddir = os.listdir("_data/legend")
legenddir.sort()

dailyracedir = os.listdir("_data/dailyrace")
dailyracedir.sort()

useddir = ["starter.csv"]
for used in useddir:
    with open(f"_data/used/{used}", "r") as f:
        input_lines = f.readlines()
    input_lines = input_lines[1:] # remove headers
    output_lines = ["id,cr,state\n"]
    for line in input_lines:
        manu, name, cr, state = line.strip().split(",")
        carid = cardb_name_to_id(name)
        output_lines.append(f"{carid},{cr},{state}\n")
    with open(f"_data/used/{used}", "w") as f:
        f.writelines(output_lines)

for legend in legenddir:
    with open(f"_data/legend/{legend}", "r") as f:
        input_lines = f.readlines()
    input_lines = input_lines[1:] # remove headers
    output_lines = ["id,cr,state\n"]
    for line in input_lines:
        manu, name, cr, state = line.strip().split(",")
        carid = cardb_name_to_id(name)
        output_lines.append(f"{carid},{cr},{state}\n")
    with open(f"_data/legend/{legend}", "w") as f:
        f.writelines(output_lines)

for dailyrace in dailyracedir:
    with open(f"_data/dailyrace/{dailyrace}", "r") as f:
        input_lines = f.readlines()
    input_lines = input_lines[1:] # remove headers
    output_lines = ["courseid,laps,cars,starttype,fuelcons,tyrewear,cartype,category,specificcars,widebodyban,nitrousban,tyres,bop,spec,garagecar,pitlanepen,time,offset\n"]
    for line in input_lines:
        track,laps,cars,starttype,fuelcons,tyrewear,cartype,category,specificcars,widebodyban,nitrousban,tyres,bop,spec,garagecar,pitlanepen,time,offset = line.strip().split(",")
        courseid = coursedb_name_to_id(track)
        output_lines.append(f"{courseid},{laps},{cars},{starttype},{fuelcons},{tyrewear},{cartype},{category},{specificcars},{widebodyban},{nitrousban},{tyres},{bop},{spec},{garagecar},{pitlanepen},{time},{offset}\n")
    with open(f"_data/dailyrace/{dailyrace}", "w") as f:
        f.writelines(output_lines)