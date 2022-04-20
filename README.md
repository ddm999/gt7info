# GT7 Info

The static website is built by `build.py` into the `build` folder.
The build script also produces a `build/data.json` file to be used by bots.

Historical and current data for dealerships, daily races, etc. for the site are stored in `_data`.
* `db` contains database information. Cars, countries, tracks, manufacturers with English names, IDs and relations.
* `rewards` contains reward cars and where they can be obtained.
* `dailyrace` contains daily race information per change (currently every Monday @ 06:00 UTC)
* `legend` contains legendary car dealership, changed every day @ 00:00 UTC.
* `used` contains used car dealership, changed every day @ 00:00 UTC.
* `championships` contains singleplayer championship data per update version (bottom of the screen in World Circuits).
* `events` contains singleplayer event data per update version (World Circuits). ***NOTE: unfinished, lots of data missing here.***
* `z_unordered` contains legend & used data from pre-release footage and from before data started being saved every day.
This is kept separate as it is not continuous with the rest of that data.

The `fonts` folder contains Google Fonts supplied fonts used by the site.
This folder is copied as-is into the final site.

The `img` folder contains all graphical assets used by the site.
Both GT7 web images and SVGs made from scratch are here.
This folder is copied as-is into the final site.

`index.html`, `campaign-rewards.html`, `engine-swaps.html`, `menu-book-used.html`, `workout-reward-estimate.html` are collated together into a single file.

`dailyrace.html`, `legend.html`, `used.html` are template files where `%VALUES` are replaced before being added to the site.

`db.py` is a support library for getting info out of the db data from `_data/db`.

`*.txt`, `*.md`, `*.png` files are all random data or details collected while working on the site.