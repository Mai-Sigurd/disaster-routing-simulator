from pathlib import Path

gui_type = int | str


MENU_TAG = "menu"

OSM_JSON_BBOX = "OSM_JSON_BBOX"
DANGER_ZONE = "DANGER_ZONE"
DANGER_ZONE_CPH = "DANGER_ZONE_CPH"

POPULATION = "POPULATION"
TIFF_FILE = "Worldpop tiff file"
POPULATION_NUMBER = "Population number"
TAG_CHUNK = "Departure_time"
TAG_INTERVAL = "Interval"

MENU_COPENHAGEN = "Copenhagen"
MENU_PICK_AREA = "Pick area"

MAIN_WINDOW = "main_window"
FIELD_WINDOW = "field_window"
CPH_WINDOW = "cph_window"

GUI_DIR = Path(__file__).resolve().parent

FONTDIR = GUI_DIR / "font/open-sans"
