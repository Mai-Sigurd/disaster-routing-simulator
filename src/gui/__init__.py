import logging

import dearpygui.dearpygui as dpg

from gui.constants import CASE_WINDOW, EXPLORE_WINDOW, MAIN_WINDOW, MENU_PICK_AREA
from gui.controller import (
    add_city_case_window,
    add_explore_window,
    add_main_window,
    change_windows,
    set_fonts_theme,
)

WIDTH = 800
HEIGHT = 650
INNER_WINDOW_WIDTH = 800
INNER_WINDOW_HEIGHT = 650


def open_gui(error_message: str = "") -> None:
    if error_message:
        logging.info("Opening GUI with input error message: %s", error_message)
    _open_gui(error_message)


def _open_gui(error_message: str = "") -> None:
    dpg.create_context()
    dpg.create_viewport(
        title="Disaster Routing", width=800, height=1100
    )  # Set viewport size
    dpg.setup_dearpygui()
    t1, e_msg = add_main_window(
        tag=MAIN_WINDOW,
        desc="Choose a city or pick an area",
        error_message=error_message,
        width=WIDTH,
        height=HEIGHT,
    )
    bold_text1 = add_explore_window(
        parent=MAIN_WINDOW,
        tag=EXPLORE_WINDOW,
        width=INNER_WINDOW_WIDTH,
        height=INNER_WINDOW_HEIGHT,
    )
    bold_text2 = add_city_case_window(
        parent=MAIN_WINDOW,
        tag=CASE_WINDOW,
        width=INNER_WINDOW_WIDTH,
        height=INNER_WINDOW_HEIGHT,
        danger_zone_desc="If left blank it will default to Amager",
    )

    set_fonts_theme(bold_text1 + bold_text2, t1, e_msg)
    change_windows("None", MENU_PICK_AREA)
    dpg.set_primary_window(MAIN_WINDOW, True)
    dpg.show_viewport()
    dpg.start_dearpygui()
    # After GUI closes, cleanup
    logging.info("GUI closed")
    dpg.destroy_context()


def close_gui() -> None:
    dpg.stop_dearpygui()
    dpg.destroy_context()
    logging.info("GUI closed")
    exit(0)
