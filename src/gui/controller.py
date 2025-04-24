import logging

import dearpygui.dearpygui as dpg

from gui.constants import (
    CASE_WINDOW,
    DANGER_ZONE,
    DEPARTURE_TIME,
    EXPLORE_WINDOW,
    FONTDIR,
    MENU_CASE,
    MENU_PICK_AREA,
    MENU_TAG,
    POPULATION,
    POPULATION_NUMBER,
    TIFF_FILE,
    gui_type,
)
from gui.fields import add_input_fields_pick_area
from input_data import (
    INPUTDATADIR,
    InputData,
    PopulationType,
    SimulationType,
    save_to_pickle,
)


def _save_input_data() -> None:
    logging.info("Getting input data from GUI")
    danger_zones_geopandas_json = dpg.get_value(DANGER_ZONE)
    population_number = dpg.get_value(POPULATION_NUMBER)
    worldpop_filepath = dpg.get_value(TIFF_FILE)
    simulation_type = SimulationType.EXPLORE
    departure_end_time_minute = dpg.get_value(DEPARTURE_TIME)
    if dpg.get_value(POPULATION) == TIFF_FILE:
        pop_type = PopulationType.TIFF_FILE
    else:
        pop_type = PopulationType.NUMBER

    input_data = InputData(
        population_type=pop_type,
        simulation_type=simulation_type,
        population_number=population_number,
        danger_zones_geopandas_json=danger_zones_geopandas_json,
        worldpop_filepath=worldpop_filepath,
        departure_end_time_sec=departure_end_time_minute * 60,
    )

    save_to_pickle(input_data, INPUTDATADIR)
    dpg.stop_dearpygui()


def _case_studies() -> None:
    input_data = InputData(
        population_type=PopulationType.NUMBER,  # Will not be used
        simulation_type=SimulationType.CASE_STUDIES,
        danger_zones_geopandas_json="",  # Will not be used
        population_number=1,  # Will not be used
        departure_end_time_sec=3600,  # Will not be used
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
        items=[MENU_PICK_AREA, MENU_CASE],
        parent=tag,
        horizontal=True,
        callback=change_windows,
        default_value=MENU_PICK_AREA,
    )
    return t1, e_msg


def add_city_case_window(
    parent: str, tag: str, width: int, height: int, danger_zone_desc: str
) -> list[gui_type]:
    dpg.add_child_window(
        label="", tag=tag, show=True, parent=parent, width=width, height=height
    )
    dpg.add_text(
        "Case Studies:\n\n"
        "Case Study 1: Copenhagen, Denmark\n"
        "The danger zone encompasses Amager, which has limited evacuation routes, "
        "creating a high risk of congestion during emergencies.\n\n"
        "Case Study 2: Ravenna, Italy\n"
        "This coastal city experienced devastating flooding in May 2023 due to extreme rainfall..",
        parent=tag,
        wrap=0,
    )
    dpg.add_button(
        label="See Case Studies",
        callback=_case_studies,
        parent=tag,
    )
    return []


def add_explore_window(
    parent: str, tag: str, width: int, height: int
) -> list[gui_type]:
    dpg.add_child_window(
        label="", tag=tag, show=True, parent=parent, width=width, height=height
    )
    bold_text = add_input_fields_pick_area(parent=tag)
    dpg.add_text(
        "\n Once the simulation is finished, a web browser showing the simulation dashboards will open.",
        parent=tag,
    )
    add_go_button(parent=tag)
    return bold_text  # type: ignore


def change_windows(sender: str, data: str) -> None:
    if data == MENU_CASE:
        dpg.show_item(CASE_WINDOW)
        dpg.hide_item(EXPLORE_WINDOW)
    else:
        dpg.show_item(EXPLORE_WINDOW)
        dpg.hide_item(CASE_WINDOW)


def add_go_button(parent: str) -> None:
    dpg.add_button(label="GO", callback=_save_input_data, width=100, parent=parent)
