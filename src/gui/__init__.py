
import dearpygui.dearpygui as dpg

from data_loader import DATA_DIR
from gui.helper import add_geo_json_input_field, set_fonts

DANGER_ZONES_DIR = DATA_DIR / "danger_zones"
OSM_BBOX_DIR = DATA_DIR / "osm_graph"


OSM_JSON_BBOX = "OSM_JSON_BBOX"
DANGER_ZONE = "DANGER_ZONE"
POPULATION = "POPULATION"
RASTER_FILE = "RASTER_FILE"



def _save_callback() -> None:
    user_input = dpg.get_value(OSM_JSON_BBOX)  # Get input value
    print("User entered:", user_input)
    
    # Save to a file
    with open("user_input.txt", "w") as file:
        file.write(user_input)
    dpg.destroy_context()
    

def open_gui() -> None:
    
    dpg.create_context()
    dpg.create_viewport(title="Disaster Routing", width=800, height=600)  # Set viewport size
    dpg.setup_dearpygui()
        

    with dpg.window(tag="PrimaryWindow"):
        t1 = add_geo_json_input_field(title="OSM Graph", desc="Go to geojson.io and pick an area, copy the JSON into the below box, if left empty this will be Copenhagen:", tag=OSM_JSON_BBOX)
        t2 = add_geo_json_input_field(title="Danger Zone", desc="Go to geojson.io and pick a dangerzone, copy the JSON into the below box, if left empty this will be Amager:", tag=DANGER_ZONE)
        
        dpg.add_button(label="Save", callback=_save_callback, width=100)
        
    set_fonts([t1, t2])

    dpg.set_primary_window("PrimaryWindow", True)  # Make it fill the viewport
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.show_font_manager()
