import dearpygui.dearpygui as dpg

from gui.constants import (
    CPH_WINDOW,
    DANGER_ZONE,
    DANGER_ZONE_CPH,
    FIELD_WINDOW,
    FONTDIR,
    MENU_COPENHAGEN,
    MENU_PICK_AREA,
    MENU_TAG,
    OSM_JSON_BBOX,
    POPULATION,
    POPULATION_NUMBER,
    TAG_CHUNK,
    TAG_INTERVAL,
    TIFF_FILE,
    gui_type,
)
from gui.fields import add_city_fields, add_input_fields_pick_area
from input_data import InputData, PopulationType, CITY, save_to_pickle, INPUTDATADIR


def _save_input_data() -> None:
    danger_zones_geopandas_json = dpg.get_value(DANGER_ZONE)
    interval = dpg.get_value(TAG_INTERVAL)
    chunks = dpg.get_value(TAG_CHUNK)
    pop_type = PopulationType.GEO_JSON_FILE
    city = dpg.get_value(MENU_TAG)
    population_number = dpg.get_value(POPULATION_NUMBER)
    worldpop_filepath = dpg.get_value(TIFF_FILE)
    osm_geopandas_json = ""
    if city == MENU_COPENHAGEN:
        city = CITY.CPH
    else:
        city = CITY.NONE
        osm_geopandas_json = dpg.get_value(OSM_JSON_BBOX)
    if dpg.get_value(POPULATION) == TIFF_FILE:
        pop_type = PopulationType.TIFF_FILE
    else:
        pop_type = PopulationType.NUMBER

    input_data = InputData(
        type=pop_type,
        interval=interval,
        chunks=chunks,
        city=city,
        population_number=population_number,
        osm_geopandas_json_bbox=osm_geopandas_json,
        danger_zones_geopandas_json=danger_zones_geopandas_json,
        worldpop_filepath=worldpop_filepath,
    )

    save_to_pickle(input_data, INPUTDATADIR)
    dpg.stop_dearpygui()


def set_fonts_theme(bold_items: list[gui_type], titel: str, e_msg: str) -> None:
    with dpg.font_registry():
        normal_font = dpg.add_font(FONTDIR / "OpenSans-Regular.ttf", 20)
        bold_font = dpg.add_font(FONTDIR / "OpenSans-Bold.ttf", 30)
        titel_font = dpg.add_font(FONTDIR / "OpenSans-Bold.ttf", 40)
        dpg.bind_font(normal_font)
        for item in bold_items:
            dpg.bind_item_font(item=item, font=bold_font)
        dpg.bind_item_font(item=titel, font=titel_font)
    with dpg.theme() as error_theme:
        with dpg.theme_component(dpg.mvText):
            dpg.add_theme_color(
                dpg.mvThemeCol_Text, (255, 0, 0, 255)
            )  # RED color in RGBA format
        dpg.bind_item_theme(e_msg, error_theme)


def add_main_window(
    desc: str, error_message: str, tag: str, width: int, height: int
) -> tuple[gui_type, gui_type]:
    dpg.add_window(
        label="", width=width, height=height, tag=tag, no_collapse=True, no_close=True
    )
    t1 = dpg.add_text(desc, parent=tag)
    e_msg = dpg.add_text(error_message, parent=tag)
    dpg.add_radio_button(
        tag=MENU_TAG,
        items=[MENU_PICK_AREA, MENU_COPENHAGEN],
        parent=tag,
        horizontal=True,
        callback=change_windows,
        default_value=MENU_PICK_AREA,
    )
    return t1, e_msg


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
