
from db import *

html = ""
with open("courses.html", "r", encoding='utf-8') as f:
    html = f.read()

course_template = ""
with open("course.html", "r", encoding='utf-8') as f:
    course_template = f.read()

##################################################
# handle courses
##################################################
def course_sorter(id):
    course = coursedata[id]
    return f"{course['Base']} {course['LayoutNumber']}"

coursedata = coursedb_all_data()
sorted_ids = sorted(coursedata, key=course_sorter)

courses_section = ""
for id in sorted_ids:
    course_html = course_template

    track = coursedata[id]["Name"]
    logo = crsbasedb_id_to_logo(coursedata[id]["Base"])
    region = coursedata[id]["Country"]
    flag = f"img/pdi-flag.png" if region == "pdi" else f"https://flagcdn.com/h24/{region}.png"

    course_html = course_html.replace("%TRACKLOGO", logo)
    course_html = course_html.replace("%FLAG", flag)
    course_html = course_html.replace("%TRACKNAME", track)
    course_html = course_html.replace("%LENGTH", f"{int(coursedata[id]['Length'])/1000}")
    course_html = course_html.replace("%STRAIGHT", f"{int(coursedata[id]['LongestStraight'])/1000}")
    course_html = course_html.replace("%ELEVATION", coursedata[id]["ElevationDiff"])
    course_html = course_html.replace("%ALTITUDE", coursedata[id]["Altitude"])
    course_html = course_html.replace("%CORNERS", coursedata[id]["NumCorners"])
    course_html = course_html.replace("%MINTIMEH", f"{int(coursedata[id]['MinTimeH']):02d}")
    course_html = course_html.replace("%MINTIMEM", f"{int(coursedata[id]['MinTimeM']):02d}")
    course_html = course_html.replace("%MAXTIMEH", f"{int(coursedata[id]['MaxTimeH']):02d}")
    course_html = course_html.replace("%MAXTIMEM", f"{int(coursedata[id]['MaxTimeM']):02d}")
    course_html = course_html.replace("%PITLANEDELTA", coursedata[id]["PitLaneDelta"])

    courses_section += course_html

html = html.replace("%COURSES_SECTION", courses_section)

with open("build/courses.html", "w") as f:
    f.write(html)