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
INNER_WINDOW_HEIGHT = 700


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

    with dpg.theme() as white_theme:
        with dpg.theme_component(dpg.mvAll):
            # Backgrounds
            dpg.add_theme_color(
                dpg.mvThemeCol_WindowBg, (255, 255, 255), category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ChildBg, (255, 255, 255), category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBg, (245, 245, 245), category=dpg.mvThemeCat_Core
            )  # input fields, combo, etc.
            dpg.add_theme_color(
                dpg.mvThemeCol_Button, (230, 230, 230), category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonHovered,
                (210, 210, 210),
                category=dpg.mvThemeCat_Core,
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonActive,
                (180, 180, 180),
                category=dpg.mvThemeCat_Core,
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_SliderGrab, (100, 100, 100), category=dpg.mvThemeCat_Core
            )

            # Text
            dpg.add_theme_color(
                dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core
            )

            # Borders and other elements
            dpg.add_theme_color(
                dpg.mvThemeCol_Border, (200, 200, 200), category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBgHovered,
                (225, 225, 225),
                category=dpg.mvThemeCat_Core,
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBgActive,
                (210, 210, 210),
                category=dpg.mvThemeCat_Core,
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBg, (240, 240, 240), category=dpg.mvThemeCat_Core
            )  # Light gray background
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBgHovered,
                (230, 230, 230),
                category=dpg.mvThemeCat_Core,
            )  # Slightly darker on hover
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBgActive,
                (220, 220, 220),
                category=dpg.mvThemeCat_Core,
            )  # Even darker when active
            dpg.add_theme_color(
                dpg.mvThemeCol_Border, (180, 180, 180), category=dpg.mvThemeCat_Core
            )  # Visible border
            dpg.add_theme_style(
                dpg.mvStyleVar_FrameRounding, 4, category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_FrameBorderSize, 1.0, category=dpg.mvThemeCat_Core
            )

    dpg.bind_theme(white_theme)
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
