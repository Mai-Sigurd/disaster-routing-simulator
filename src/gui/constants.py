from pathlib import Path

gui_type = int | str


MENU_TAG = "menu"

OSM_JSON_BBOX = "OSM_JSON_BBOX"
DANGER_ZONE = "DANGER_ZONE"

POPULATION = "POPULATION"
TIFF_FILE = "Worldpop tiff file"
POPULATION_NUMBER = "Population number"
DEPARTURE_TIME = "Departure Time"

MENU_CASE = "Case studies"
MENU_PICK_AREA = "Explore"

MAIN_WINDOW = "main_window"
EXPLORE_WINDOW = "explore_window"
CASE_WINDOW = "case_window"

GUI_DIR = Path(__file__).resolve().parent

FONTDIR = GUI_DIR / "font/open-sans"
