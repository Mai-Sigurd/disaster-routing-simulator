
import webbrowser
from pathlib import Path

import dearpygui.dearpygui as dpg

GUI_DIR =  Path(__file__).resolve().parent

FONTDIR = GUI_DIR / "font/open-sans"


def set_fonts(bold_items: []) -> None: # type: ignore
    # add a font registry
    print(type(bold_items[0]))
    with dpg.font_registry():
        print(FONTDIR/"OpenSans-Regular.ttf")
        # first argument ids the path to the .ttf or .otf file
        normal_font = dpg.add_font(FONTDIR/"OpenSans-Regular.ttf", 20)
        bold_font = dpg.add_font(FONTDIR/"OpenSans-Bold.ttf", 30)
        dpg.bind_font(normal_font)
        for item in bold_items:
            dpg.bind_item_font(item=item, font=bold_font)


def add_geo_json_input_field(title, desc, tag: str) -> any: # type: ignore
        t1 = dpg.add_text(title)
        dpg.add_text(desc)
        dpg.add_button(label="https://geojson.io/", callback=lambda: webbrowser.open("https://geojson.io/")) 
        dpg.add_input_text(tag=tag, multiline=True, width=400, height=100)
        return t1 # type: ignore