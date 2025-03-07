import webbrowser
from pathlib import Path

import dearpygui.dearpygui as dpg

from data_loader import DATA_DIR

DANGER_ZONES_DIR = DATA_DIR / "danger_zones"
OSM_BBOX_DIR = DATA_DIR / "osm_graph"


OSM_JSON_BBOX = "OSM_JSON_BBOX"
DANGER_ZONE = "DANGER_ZONE"
POPULATION = "POPULATION"
RASTER_FILE = "RASTER_FILE"

COPENHAGEN = "Copenhagen"
PICK_AREA = "Pick area"

MAIN_WINDOW = "main_window"
FIELD_WINDOW = "field_window"

GUI_DIR = Path(__file__).resolve().parent

FONTDIR = GUI_DIR / "font/open-sans"


def _save_callback() -> None:
    user_input = dpg.get_value(OSM_JSON_BBOX)  # Get input value
    print("User entered:", user_input)

    # Save to a file
    with open("user_input.txt", "w") as file:
        file.write(user_input)
    dpg.destroy_context()
    # TODO: Add the rest of the input fields


def set_fonts(bold_items: [], titel):  # type: ignore
    with dpg.font_registry():
        normal_font = dpg.add_font(FONTDIR / "OpenSans-Regular.ttf", 20)
        bold_font = dpg.add_font(FONTDIR / "OpenSans-Bold.ttf", 30)
        titel_font = dpg.add_font(FONTDIR / "OpenSans-Bold.ttf", 40)
        dpg.bind_font(normal_font)
        for item in bold_items:
            dpg.bind_item_font(item=item, font=bold_font)
        dpg.bind_item_font(item=titel, font=titel_font)


def add_main_window(desc, tag, call_back_radio_button_data: str, width, height: int):  # type: ignore  # dpg returns a ( int | str ) type that mypy cant handle
    dpg.add_window(
        label="", width=width, height=height, tag=tag, no_collapse=True, no_close=True
    )
    t1 = dpg.add_text(desc, parent=tag)
    dpg.add_radio_button(items=[COPENHAGEN, PICK_AREA], parent=tag, horizontal=True)
    return t1

    # TODO add callback for radio button


def add_field_window(parent, tag: str, width, height: int) -> list:  # type: ignore  # dpg returns a ( int | str ) type that mypy cant handle
    dpg.add_child_window(
        label="", tag=tag, show=True, parent=parent, width=width, height=height
    )
    t1 = _add_geo_json_input_field(
        title="OSM Graph",
        desc="Go to geojson.io and pick an area, copy the JSON into the below box",
        desc2="The area should be a bounding box of the city",
        desc3="If left blank it will default to Copenhagen",
        tag=OSM_JSON_BBOX,
        parent=tag,
    )
    t2 = _add_geo_json_input_field(
        title="Danger Zone",
        desc="Go to geojson.io and pick a dangerzone, copy the JSON into the below box",
        desc2="The area should be a polygon of the dangerzone, withing the OSM Graph",
        desc3="If left blank it will default to a Amager",
        tag=DANGER_ZONE,
        parent=tag,
    )
    t3 = _add_population_input_field(
        title="Population",
        desc="Choose the population type:",
        desc2="Either download a worldpop tiff file and input the filepath or input a population number which will be evenly distributed across the dangerzone",
        tag=POPULATION,
        types=["Worldpop tiff file", "Population number"],
        parent=tag,
    )
    t4 = _add_departure_time_input_field(
        title="Departure time",
        desc_chunk="Enter the departure time in hours: ",
        desc_interval="Enter the interval in minutes: ",
        tag_chunk="Departure time",
        tag_interval="Interval",
        parent=tag,
    )

    return [t1, t2, t3, t4]


def add_go_button(parent, tag: str):  # type: ignore
    dpg.add_button(label=tag, callback=_save_callback, width=100, parent=parent)


def _add_geo_json_input_field(title, desc, desc2, desc3, tag, parent: str):  # type: ignore  # dpg returns a ( int | str ) type that mypy cant handle
    t1 = dpg.add_text(title, parent=parent)
    dpg.add_text(desc, parent=parent)
    dpg.add_text(desc2, parent=parent)
    dpg.add_text(desc3, parent=parent)
    dpg.add_button(
        label="https://geojson.io/",
        callback=lambda: webbrowser.open("https://geojson.io/"),
        parent=parent,
    )
    dpg.add_input_text(tag=tag, multiline=True, width=400, height=100, parent=parent)
    return t1


def _type_radio_callback(sender, app_data, user_data):  # type: ignore
    for i in user_data:
        dpg.configure_item(i, show=False)
    dpg.configure_item(app_data, show=True)


def _add_population_input_field(
    title, desc, desc2, tag: str, types: list[str], parent: str
):  # type: ignore  # dpg returns a ( int | str ) type that mypy cant handle
    t1 = dpg.add_text(title, parent=parent)
    dpg.add_text(desc, parent=parent)
    dpg.add_text(desc2, parent=parent)
    dpg.add_button(
        label="https://hub.worldpop.org/geodata",
        callback=lambda: webbrowser.open(
            "https://hub.worldpop.org/geodata/listing?id=78"
        ),
        parent=parent,
    )
    dpg.add_radio_button(
        items=types,
        default_value=1,
        tag=tag,
        horizontal=True,
        callback=_type_radio_callback,
        user_data=types,
        parent=parent,
    )

    dpg.add_input_text(tag=types[0], show=True, parent=parent)
    dpg.add_input_int(tag=types[1], show=False, parent=parent)

    return t1


def _add_departure_time_input_field(
    title, desc_chunk, desc_interval, tag_chunk, tag_interval: str, parent: str
):  # type: ignore  # dpg returns a ( int | str ) type that mypy cant handle
    t1 = dpg.add_text(title, parent=parent)
    dpg.add_text(desc_chunk, parent=parent)
    dpg.add_input_int(tag=tag_chunk, parent=parent)
    dpg.add_text(desc_interval, parent=parent)
    dpg.add_input_int(tag=tag_interval, parent=parent)
    return t1
