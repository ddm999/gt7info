with open("build/CNAME", "w") as f:
    f.write("gt7info.gt-mod.site")

import shutil
shutil.rmtree("build/_data")