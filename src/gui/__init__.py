import dearpygui.dearpygui as dpg

from gui.constants import CPH_WINDOW, FIELD_WINDOW, MAIN_WINDOW, PICK_AREA
from gui.controller import (
    add_cph_window,
    add_field_window,
    add_go_button,
    add_main_window,
    change_windows,
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


# TODO add input verificaction step.
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
        parent=MAIN_WINDOW, tag=FIELD_WINDOW, width=WIDTH, height=HEIGHT - 200
    )
    bold_text2 = add_cph_window(
        parent=MAIN_WINDOW,
        tag=CPH_WINDOW,
        width=WIDTH,
        height=HEIGHT,
    )
    add_go_button(parent=MAIN_WINDOW)

    set_fonts(bold_text1 + bold_text2, t1)
    change_windows(None, PICK_AREA)
    dpg.set_primary_window(MAIN_WINDOW, True)
    dpg.show_viewport()
    dpg.start_dearpygui()
    # After GUI closes, cleanup
    dpg.destroy_context()
