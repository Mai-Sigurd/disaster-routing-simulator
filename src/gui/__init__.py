import dearpygui.dearpygui as dpg

from gui.constants import CPH_WINDOW, FIELD_WINDOW, MAIN_WINDOW
from gui.controller import (
    add_cph_window,
    add_field_window,
    add_go_button,
    add_main_window,
    set_fonts,
)

WIDTH = 800
HEIGHT = 1100


def open_gui() -> None:
    try:
        _open_gui()
    except Exception as e:
        dpg.stop_dearpygui()
        dpg.destroy_context()
        print(e)


def _open_gui() -> None:
    dpg.create_context()
    dpg.create_viewport(
        title="Disaster Routing", width=800, height=1100
    )  # Set viewport size
    dpg.setup_dearpygui()
    t1 = add_main_window(
        tag=MAIN_WINDOW,
        desc="Choose a city or pick an area",
        width=WIDTH,
        height=HEIGHT,
    )
    bold_text1 = add_field_window(
        parent=MAIN_WINDOW, tag=FIELD_WINDOW, width=WIDTH, height=HEIGHT - 100
    )
    bold_text2 = add_cph_window(
        parent=FIELD_WINDOW,
        desc="Write text here",
        tag=CPH_WINDOW,
        width=WIDTH,
        height=HEIGHT,
    )

    add_go_button(parent=FIELD_WINDOW, tag="GO")
    set_fonts(bold_text1 + bold_text2, t1)
    dpg.set_primary_window(MAIN_WINDOW, True)
    dpg.show_viewport()
    dpg.start_dearpygui()
    # After GUI closes, cleanup
    dpg.destroy_context()
