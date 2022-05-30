
from db import *

html = ""
with open("courses.html", "r", encoding='utf-8') as f:
    html = f.read()

category_template = ""
with open("course_category.html", "r", encoding='utf-8') as f:
    category_template = f.read()

base_template = ""
with open("course_base.html", "r", encoding='utf-8') as f:
    base_template = f.read()

course_template = ""
with open("course.html", "r", encoding='utf-8') as f:
    course_template = f.read()

##################################################
# handle courses
##################################################
def course_sorter(id):
    course = coursedata[id]
    return f"{course['Category']} {course['Base']} {course['LayoutNumber']}"

categories_bases_courses : dict[str, dict[int, list[dict]]] = {}
for category in ["circuit", "original", "city", "snow_dirt"]:
    categories_bases_courses[category] = {}

coursedata = coursedb_all_data().values()
for course in coursedata:
    if course['Base'] not in categories_bases_courses[course['Category']].keys():
        categories_bases_courses[course['Category']][course['Base']] = [course]
    else:
        categories_bases_courses[course['Category']][course['Base']].append(course)

##################################################
# helpers
##################################################
def CourseCategoryToShownName(category : str):
    if category == "circuit":
        return "World Circuits"
    elif category == "original":
        return "Original Circuits"
    elif category == "city":
        return "City Courses"
    elif category == "snow_dirt":
        return "Dirt & Snow"

##################################################
# run through sections
##################################################
courses_section = ""
for category, bases in categories_bases_courses.items():
    category_html = category_template

    categoryname = CourseCategoryToShownName(category)

    category_html = category_html.replace("%CATEGORYNAME", categoryname)
    category_html = category_html.replace("%CATEGORY", category)

    courses_section += category_html

"""
for id in sorted_ids:
    course_html = course_template

    track = coursedata[id]["Name"]
    logo = crsbasedb_id_to_logo(coursedata[id]["Base"])
    region = coursedata[id]["Country"]
    flag = f"img/pdi-flag.png" if region == "pdi" else f"https://flagcdn.com/h24/{region}.png"

    MinTimeH = int(coursedata[id]['MinTimeH'])
    MinTimeM = int(coursedata[id]['MinTimeM'])
    MaxTimeH = int(coursedata[id]['MaxTimeH'])
    MaxTimeM = int(coursedata[id]['MaxTimeM'])

    course_html = course_html.replace("%TRACKLOGO", logo)
    course_html = course_html.replace("%FLAG", flag)
    course_html = course_html.replace("%TRACKNAME", track)
    course_html = course_html.replace("%LENGTH", f"{int(coursedata[id]['Length'])/1000}")
    course_html = course_html.replace("%STRAIGHT", f"{int(coursedata[id]['LongestStraight'])/1000}")
    course_html = course_html.replace("%ELEVATION", coursedata[id]["ElevationDiff"])
    course_html = course_html.replace("%ALTITUDE", coursedata[id]["Altitude"])
    course_html = course_html.replace("%CORNERS", coursedata[id]["NumCorners"])
    course_html = course_html.replace("%PITLANEDELTA", coursedata[id]["PitLaneDelta"])

    if MinTimeH == 0 and MinTimeM == 0 and MaxTimeH == 0 and MaxTimeM == 0:
        course_html += ('        <img id="24hr" src="img/track_24hr.png"/>24hr\n'+
                        '        <span id="24hr-text">Supports 24hr time</span><br>\n')
    else:
        course_html += f'<span id="time-range">{MinTimeH:02d}:{MinTimeM:02d} to {MaxTimeH:02d}:{MaxTimeM:02d}</span>\n'

    if int(coursedata[id]['IsReverse']) != 0:
        course_html += '        <img id="rev" src="img/track_rev.png"/>rev\n'

    if int(coursedata[id]['IsOval']) != 0:
        course_html += '        <img id="oval" src="img/track_oval.png"/>oval\n'

    if int(coursedata[id]['NoRain']) != 0:
        course_html += '        <img id="norain" src="img/track_norain.png"/>norain<br>\n'
    else:
        course_html += ('       <img id="rain" src="img/track_rain.png"/>rain\n'+
                        '       <span id="rain-text">Supports rain</span><br>\n')

    courses_section += course_html
"""

html = html.replace("%COURSES_SECTION", courses_section)

with open("build/courses.html", "w") as f:
    f.write(html)

FILES_TO_COPY = ["style-courses-220530.css"]

import shutil
for file in FILES_TO_COPY:
    shutil.copyfile(f"{file}", f"build/{file}")