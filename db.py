
##################################################
# load databases
##################################################
db_cars = [] # type: list[str]
with open(f"_data/db/cars.csv") as f:
    db_cars = f.readlines()
db_cars = db_cars[1:] # remove headers

db_cargrp = [] # type: list[str]
with open(f"_data/db/cargrp.csv") as f:
    db_cargrp = f.readlines()
db_cargrp = db_cargrp[1:] # remove headers

db_country = [] # type: list[str]
with open(f"_data/db/country.csv") as f:
    db_country = f.readlines()
db_country = db_country[1:] # remove headers

db_course = [] # type: list[str]
with open(f"_data/db/course.csv") as f:
    db_course = f.readlines()
db_course = db_course[1:] # remove headers

db_crsbase = [] # type: list[str]
with open(f"_data/db/crsbase.csv") as f:
    db_crsbase = f.readlines()
db_crsbase = db_crsbase[1:] # remove headers

db_maker = [] # type: list[str]
with open(f"_data/db/maker.csv") as f:
    db_maker = f.readlines()
db_maker = db_maker[1:] # remove headers

db_stockperf = [] # type: list[str]
with open(f"_data/db/stockperf.csv") as f:
    db_stockperf = f.readlines()
db_stockperf = db_stockperf[1:] # remove headers

##################################################
# database queries
##################################################
def cardb_id_to_name(input_id : int):
    input_id = int(input_id)
    for line in db_cars:
        id, name, maker = line.strip().split(",")
        if int(id) == input_id:
            return name
    raise ValueError(f"carid {input_id} not found!")

def cardb_id_to_maker(input_id : int):
    input_id = int(input_id)
    for line in db_cars:
        id, name, maker = line.strip().split(",")
        if int(id) == input_id:
            return int(maker)
    raise ValueError(f"carid {input_id} not found!")

def cargrpdb_id_to_group(input_id : int):
    input_id = int(input_id)
    for line in db_cargrp:
        id, group = line.strip().split(",")
        if int(id) == input_id:
            return group
    raise ValueError(f"carid {input_id} not found!")

def countrydb_id_to_name(input_id : int):
    input_id = int(input_id)
    for line in db_country:
        id, name, code = line.strip().split(",")
        if int(id) == input_id:
            return name
    raise ValueError(f"countryid {input_id} not found!")

def countrydb_id_to_code(input_id : int):
    input_id = int(input_id)
    for line in db_country:
        id, name, code = line.strip().split(",")
        if int(id) == input_id:
            return code
    raise ValueError(f"countryid {input_id} not found!")

def coursedb_id_to_name(input_id : int):
    input_id = int(input_id)
    for line in db_course:
        id, name, base, country, category, length, straight, elevation, altitude, minH, minM, minS, maxH, maxM, maxS, layout, rev, pitlane, oval, corner, dryOnly = line.strip().split(",")
        if int(id) == input_id:
            return name
    raise ValueError(f"courseid {input_id} not found!")

def coursedb_id_to_base(input_id : int):
    input_id = int(input_id)
    for line in db_course:
        id, name, base, country, category, length, straight, elevation, altitude, minH, minM, minS, maxH, maxM, maxS, layout, rev, pitlane, oval, corner, dryOnly = line.strip().split(",")
        if int(id) == input_id:
            return int(base)
    raise ValueError(f"courseid {input_id} not found!")

def coursedb_id_to_country(input_id : int):
    input_id = int(input_id)
    for line in db_course:
        id, name, base, country, category, length, straight, elevation, altitude, minH, minM, minS, maxH, maxM, maxS, layout, rev, pitlane, oval, corner, dryOnly = line.strip().split(",")
        if int(id) == input_id:
            return int(country)
    raise ValueError(f"courseid {input_id} not found!")

def coursedb_all_data():
    data = {}
    for line in db_course:
        id, name, base, country, category, length, straight, elevation, altitude, minH, minM, minS, maxH, maxM, maxS, layout, rev, pitlane, oval, corner, dryOnly = line.strip().split(",")
        data[id] = {'ID':id, 'Name':name, 'Base':base, 'Country':country, 'Category':category, 'Length':length,
        'LongestStraight':straight, 'ElevationDiff':elevation, 'Altitude':altitude,
        'MinTimeH':minH, 'MinTimeM':minM, 'MinTimeS':minS, 'MaxTimeH':maxH, 'MaxTimeM':maxM, 'MaxTimeS':maxS,
        'LayoutNumber':layout, 'IsReverse':rev, 'PitLaneDelta':pitlane, 'IsOval':oval, 'NumCorners':corner, 'NoRain':dryOnly}
    return data

def crsbasedb_id_to_name(input_id : int):
    input_id = int(input_id)
    for line in db_crsbase:
        id, name, logo = line.strip().split(",")
        if int(id) == input_id:
            return name
    raise ValueError(f"crsbaseid {input_id} not found!")

def crsbasedb_id_to_logo(input_id : int):
    input_id = int(input_id)
    for line in db_crsbase:
        id, name, logo = line.strip().split(",")
        if int(id) == input_id:
            return logo
    raise ValueError(f"crsbaseid {input_id} not found!")

def crsbase_all_data():
    data = {}
    first_crs = {}
    crsdata = coursedb_all_data()
    for crs in crsdata:
        if crs['Base'] not in first_crs.keys():
            first_crs[crs['Base']] = crs

    for line in db_crsbase:
        id, name, logo = line.strip().split(",")
        data[id] = {'Name':name, 'Logo':logo, 'FirstLayoutID':first_crs[id]['ID']}
    return data

def makerdb_id_to_name(input_id : int):
    input_id = int(input_id)
    for line in db_maker:
        id, name, country = line.strip().split(",")
        if int(id) == input_id:
            return name
    raise ValueError(f"makerid {input_id} not found!")

def makerdb_id_to_country(input_id : int):
    input_id = int(input_id)
    for line in db_maker:
        id, name, country = line.strip().split(",")
        if int(id) == input_id:
            return int(country)
    raise ValueError(f"makerid {input_id} not found!")

def stockperfdb_id_tyre_to_pp(input_id : int, input_tyre : str):
    input_id = int(input_id)
    for line in db_stockperf:
        id, pp, tyre = line.strip().split(",")
        if int(id) == input_id and tyre == input_tyre:
            return pp
    return "0" # no entry is provided when the car has "⚠️ PP"
    #raise ValueError(f"carid {input_id} / tyre {input_tyre} not found!")

##################################################
# combined db queries
##################################################
def cardb_id_to_makername(input_id : int):
    maker = cardb_id_to_maker(input_id)
    return makerdb_id_to_name(maker)

def cardb_id_to_countrycode(input_id : int):
    maker = cardb_id_to_maker(input_id)
    return makerdb_id_to_countrycode(maker)

def coursedb_id_to_basename(input_id : int):
    crsbase = coursedb_id_to_base(input_id)
    return crsbasedb_id_to_name(crsbase)

def coursedb_id_to_logoname(input_id : int):
    crsbase = coursedb_id_to_base(input_id)
    return crsbasedb_id_to_logo(crsbase)

def coursedb_id_to_countrycode(input_id : int):
    country = coursedb_id_to_country(input_id)
    return countrydb_id_to_code(country)

def makerdb_id_to_countrycode(input_id : int):
    country = makerdb_id_to_country(input_id)
    return countrydb_id_to_code(country)

def stockperfdb_id_to_pp_dict(input_id : int):
    tyres = ["CH","CM","CS","SH","SM","SS","RH","RM","RS","IM","W","D"]
    ppdict = {}
    for tyre in tyres:
        pp = stockperfdb_id_tyre_to_pp(input_id, tyre)
        ppdict[tyre] = pp
    return ppdict

##################################################
# db reverse query (item -> id)
##################################################
def makerdb_name_to_id(input_name : str):
    input_name_upper = input_name.upper()
    for line in db_maker:
        id, name, country = line.strip().split(",")
        if name.upper() == input_name_upper:
            return id
    raise ValueError(f"maker name '{input_name}' not found!")

def cardb_name_to_id(input_name : str):
    input_name_upper = input_name.upper()
    for line in db_cars:
        id, name, maker = line.strip().split(",")
        if name.upper() == input_name_upper:
            return id
    raise ValueError(f"car name '{input_name}' not found!")

def coursedb_name_to_id(input_name : str):
    input_name_upper = input_name.upper()
    for line in db_course:
        id, name, base, country, category, length, straight, elevation, altitude, minH, minM, minS, maxH, maxM, maxS, layout, rev, pitlane, oval, corner, dryOnly = line.strip().split(",")
        if name.upper() == input_name_upper:
            return id
    raise ValueError(f"course name '{input_name}' not found!")

def cargrpdb_list_ids_from_group(input_group : str):
    idlist = []
    for line in db_cargrp:
        id, group = line.strip().split(",")
        if group == input_group:
            idlist.append(int(id))
    if len(idlist) == 0:
        raise ValueError(f"group '{input_group}' not found!")
    return idlist