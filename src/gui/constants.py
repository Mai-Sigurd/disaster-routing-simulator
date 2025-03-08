from pathlib import Path

from data_loader import DATA_DIR

gui_type = int | str

DANGER_ZONES_DIR = DATA_DIR / "danger_zones"
OSM_BBOX_DIR = DATA_DIR / "osm_graph"
MENU_TAG = "menu"

OSM_JSON_BBOX = "OSM_JSON_BBOX"
DANGER_ZONE = "DANGER_ZONE"
DANGER_ZONE_CPH = "DANGER_ZONE_CPH"

POPULATION = "POPULATION"
TIFF_FILE = "Worldpop tiff file"
POPULATION_NUMBER = "Population number"
RASTER_FILE = "RASTER_FILE"

MENU_COPENHAGEN = "Copenhagen"
MENU_PICK_AREA = "Pick area"

MAIN_WINDOW = "main_window"
FIELD_WINDOW = "field_window"
CPH_WINDOW = "cph_window"

GUI_DIR = Path(__file__).resolve().parent

FONTDIR = GUI_DIR / "font/open-sans"

INPUTDATADIR = GUI_DIR / "input_data.json"
