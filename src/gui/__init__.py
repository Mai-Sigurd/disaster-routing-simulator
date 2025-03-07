import dearpygui.dearpygui as dpg

from gui.helper import (
    FIELD_WINDOW,
    MAIN_WINDOW,
    add_field_window,
    add_go_button,
    add_main_window,
    set_fonts,
)

WIDTH = 800
HEIGHT = 1100


def open_gui() -> None:
    dpg.create_context()
    dpg.create_viewport(
        title="Disaster Routing", width=800, height=1100
    )  # Set viewport size
    dpg.setup_dearpygui()
    t1 = add_main_window(
        tag=MAIN_WINDOW,
        desc="Choose a city or pick an area",
        call_back_radio_button_data="soon",
        width=WIDTH,
        height=HEIGHT,
    )
    bold_text = add_field_window(
        parent=MAIN_WINDOW, tag=FIELD_WINDOW, width=WIDTH, height=HEIGHT - 100
    )
    add_go_button(parent=FIELD_WINDOW, tag="GO")
    set_fonts(bold_text, t1)
    dpg.set_primary_window(MAIN_WINDOW, True)
    dpg.show_viewport()
    dpg.start_dearpygui()
