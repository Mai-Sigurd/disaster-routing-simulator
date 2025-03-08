import dearpygui.dearpygui as dpg

from gui.constants import (
    CPH_WINDOW,
    DANGER_ZONE,
    DANGER_ZONE_CPH,
    FIELD_WINDOW,
    FONTDIR,
    INPUTDATADIR,
    MENU_COPENHAGEN,
    MENU_PICK_AREA,
    MENU_TAG,
    OSM_JSON_BBOX,
    POPULATION,
    TIFF_FILE,
    gui_type,
)
from gui.fields import add_city_fields, add_input_fields_pick_area
from gui.input_data import InputData, save_input_data, save_to_json_file


def _save_input_data() -> None:
    input = InputData()
    osm_geopandas_json = dpg.get_value(OSM_JSON_BBOX)
    danger_zones_geopandas_json = dpg.get_value(DANGER_ZONE)
    interval = dpg.get_value("Interval")
    chunks = dpg.get_value("Departure time")
    worldpop = dpg.get_value(POPULATION) == TIFF_FILE
    population_number = dpg.get_value("Population number")
    worldpop_filepath = dpg.get_value("Worldpop tiff file")
    save_input_data(
        self=input,
        osm_geopandas_json=osm_geopandas_json,
        danger_zones_geopandas_json=danger_zones_geopandas_json,
        interval=interval,
        chunks=chunks,
        worldpop=worldpop,
        population_number=population_number,
        worldpop_filepath=worldpop_filepath,
    )
    save_to_json_file(input, INPUTDATADIR)
    dpg.stop_dearpygui()


def set_fonts(bold_items: list[gui_type], titel: str) -> None:
    with dpg.font_registry():
        normal_font = dpg.add_font(FONTDIR / "OpenSans-Regular.ttf", 20)
        bold_font = dpg.add_font(FONTDIR / "OpenSans-Bold.ttf", 30)
        titel_font = dpg.add_font(FONTDIR / "OpenSans-Bold.ttf", 40)
        dpg.bind_font(normal_font)
        for item in bold_items:
            dpg.bind_item_font(item=item, font=bold_font)
        dpg.bind_item_font(item=titel, font=titel_font)


def add_main_window(desc: str, tag: str, width: int, height: int) -> gui_type:
    dpg.add_window(label="", width=width, height=height, tag=tag, no_collapse=True, no_close=True)
    t1 = dpg.add_text(desc, parent=tag)
    dpg.add_radio_button(
        tag=MENU_TAG,
        items=[MENU_PICK_AREA, MENU_COPENHAGEN],
        parent=tag,
        horizontal=True,
        callback=change_windows,
        default_value=1,
    )
    return t1


def add_city_window(parent: str, tag: str, width: int, height: int) -> list[gui_type]:
    dpg.add_child_window(
        label="", tag=tag, show=True, parent=parent, width=width, height=height
    )
    bold_text = add_city_fields(parent=tag, city_tag=DANGER_ZONE_CPH)
    return bold_text  # type: ignore


def add_field_window(parent: str, tag: str, width: int, height: int) -> list[gui_type]:
    dpg.add_child_window(
        label="", tag=tag, show=True, parent=parent, width=width, height=height
    )
    bold_text = add_input_fields_pick_area(parent=tag)
    return bold_text  # type: ignore


def change_windows(sender: str, data: str) -> None:  
    if data == MENU_COPENHAGEN:
        dpg.show_item(CPH_WINDOW)
        dpg.hide_item(FIELD_WINDOW)
    else:
        dpg.show_item(FIELD_WINDOW)
        dpg.hide_item(CPH_WINDOW)


def add_go_button(parent: str) -> None:
    dpg.add_button(label="GO", callback=_save_input_data, width=100, parent=parent)
