
import os, shutil
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
categories_bases_courses : dict[str, dict[str, list[dict]]] = {}
for category in ["circuit", "original", "city", "snow_dirt"]:
    categories_bases_courses[category] = {}

coursedata = coursedb_all_data().values()
for course in coursedata:
    base = course['Base']
    cat = course['Category']
    if base not in categories_bases_courses[cat]:
        categories_bases_courses[cat][base] = [course]
    else:
        categories_bases_courses[cat][base].append(course)

for cat in categories_bases_courses:
    for base in categories_bases_courses[cat]:
        categories_bases_courses[cat][base].sort(key=lambda c: int(c['LayoutNumber']))

##################################################
# helpers
##################################################
def CourseCategoryToShownName(category: str):
    match category:
        case "circuit":   return "World Circuits"
        case "original":  return "Original Circuits"
        case "city":      return "City Courses"
        case "snow_dirt": return "Dirt & Snow"

##################################################
# run through sections
##################################################
courses_section = ""
for category, bases in categories_bases_courses.items():
    category_html = category_template
    category_html = category_html.replace("%CATEGORYNAME", CourseCategoryToShownName(category))
    category_html = category_html.replace("%CATEGORY", category)

    crsbases_section = ""
    for base_id, courses in bases.items():
        base_html = base_template

        logo = crsbasedb_id_to_logo(base_id)
        base_name = crsbasedb_id_to_name(base_id)
        region = countrydb_id_to_code(int(courses[0]['Country']))
        flag = f"img/pdi-flag.png" if region == "pdi" else f"https://flagcdn.com/h24/{region}.png"

        base_html = base_html.replace("%TRACKLOGO", logo)
        base_html = base_html.replace("%FLAG", flag)
        base_html = base_html.replace("%TRACKNAME", base_name)
        base_html = base_html.replace("%NUMLAYOUTS", str(len(courses)))

        crslayouts_section = ""
        for course in courses:
            course_html = course_template

            MinTimeH = f"{int(course['MinTimeH']):02d}" if course['MinTimeH'] != "?" else "??"
            MinTimeM = f"{int(course['MinTimeM']):02d}" if course['MinTimeM'] != "?" else "??"
            MaxTimeH = f"{int(course['MaxTimeH']):02d}" if course['MaxTimeH'] != "?" else "??"
            MaxTimeM = f"{int(course['MaxTimeM']):02d}" if course['MaxTimeM'] != "?" else "??"

            course_html = course_html.replace("%TRACKNAME", course['Name'])
            course_html = course_html.replace("%LENGTH", f"{float(course['Length'])/1000:.3f}")
            course_html = course_html.replace("%STRAIGHT", f"{float(course['LongestStraight'])/1000:.3f}")
            course_html = course_html.replace("%ELEVATION", course['ElevationDiff'])
            course_html = course_html.replace("%ALTITUDE", course['Altitude'])
            course_html = course_html.replace("%CORNERS", course['NumCorners'])
            course_html = course_html.replace("%PITLANEDELTA", course['PitLaneDelta'])

            if f"{MinTimeH}{MinTimeM}{MaxTimeH}{MaxTimeM}" == "00000000":
                course_html += ('        <img id="hr24" src="img/track_24hr.png"/>24hr\n'
                                '        <span id="hr24-text">Supports 24hr time</span><br>\n')
            else:
                course_html += f'<span id="time-range">{MinTimeH}:{MinTimeM} to {MaxTimeH}:{MaxTimeM}</span>\n'

            if int(course['IsReverse']) != 0:
                course_html += '        <img id="rev" src="img/track_rev.png"/>rev\n'
            if int(course['IsOval']) != 0:
                course_html += '        <img id="oval" src="img/track_oval.png"/>oval\n'
            if int(course['NoRain']) != 0:
                course_html += '        <img id="norain" src="img/track_norain.png"/>norain<br>\n'
            else:
                course_html += ('        <img id="rain" src="img/track_rain.png"/>rain\n'
                                '        <span id="rain-text">Supports rain</span><br>\n')

            course_html += '</div>\n'
            crslayouts_section += course_html

        base_html = base_html.replace("%CRSLAYOUTS_SECTION", crslayouts_section)
        crsbases_section += base_html

    category_html = category_html.replace("%CRSBASES_SECTION", crsbases_section)
    courses_section += category_html

html = html.replace("%COURSES_SECTION", courses_section)

os.makedirs("build", exist_ok=True)
with open("build/courses.html", "w", encoding='utf-8') as f:
    f.write(html)

FILES_TO_COPY = ["style-courses.css"]
for file in FILES_TO_COPY:
    if os.path.exists(file):
        shutil.copyfile(file, f"build/{file}")

print("spaghetti")