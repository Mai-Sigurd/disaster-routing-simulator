import webbrowser

import dearpygui.dearpygui as dpg

from gui.constants import (
    DANGER_ZONE,
    OSM_JSON_BBOX,
    POPULATION,
    POPULATION_NUMBER,
    TIFF_FILE,
    gui_type,
)


def add_input_fields_pick_area(parent: str) -> list[gui_type]:
    t2 = _add_danger_zone_input_field(parent=parent, tag=DANGER_ZONE)

    t3 = _add_population_input_field(
        title="Population",
        desc="Choose the population type:",
        desc2="Either download a worldpop tiff file and input the filepath or input a population number which will be evenly distributed across the dangerzone",
        tag=POPULATION,
        types=[
            TIFF_FILE,
            POPULATION_NUMBER,
        ],  # if you change the ordering, remember to change ordering constants in constants.py
        parent=parent,
    )
    return [t2, t3]


def add_city_fields(parent: str, city_tag: str, desc3: str = "") -> list[gui_type]:
    bold_text = _add_danger_zone_input_field(parent=parent, tag=city_tag, desc3=desc3)
    return [bold_text]


def _add_danger_zone_input_field(parent: str, tag: str, desc3: str = "") -> gui_type:
    t2 = _add_geo_json_input_field(
        title="Danger Zone",
        desc="Go to geojson.io and pick a dangerzone, copy the JSON into the below box",
        desc2="The area should be a polygon of the dangerzone, withing the OSM Graph",
        desc3=desc3,
        tag=tag,
        parent=parent,
    )
    return t2


def _add_geo_json_input_field(
    title: str, desc: str, desc2: str, desc3: str, tag: str, parent: str
) -> gui_type:
    t1 = dpg.add_text(title, parent=parent)
    dpg.add_text(desc, parent=parent)
    dpg.add_text(desc2, parent=parent)
    if desc3:
        dpg.add_text(desc3, parent=parent)
    dpg.add_button(
        label="https://geojson.io/",
        callback=lambda: webbrowser.open("https://geojson.io/"),
        parent=parent,
    )
    dpg.add_input_text(tag=tag, multiline=True, width=400, height=100, parent=parent)
    return t1


def _add_population_input_field(
    title: str, desc: str, desc2: str, tag: str, types: list[str], parent: str
) -> gui_type:
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
        default_value=types[0],
        tag=tag,
        horizontal=True,
        callback=_show_input_field_based_on_radio,
        user_data=types,
        parent=parent,
    )

    dpg.add_input_text(tag=types[0], show=True, parent=parent)
    dpg.add_input_int(tag=types[1], show=False, parent=parent)

    return t1


def _show_input_field_based_on_radio(sender, app_data, user_data) -> None:  # type: ignore
    for i in user_data:
        dpg.configure_item(i, show=False)
    dpg.configure_item(app_data, show=True)


def _add_departure_time_input_field(
    title: str,
    desc_chunk: str,
    desc_interval: str,
    tag_chunk: str,
    tag_interval: str,
    parent: str,
) -> gui_type:
    t1 = dpg.add_text(title, parent=parent)
    dpg.add_text(desc_chunk, parent=parent)
    dpg.add_input_int(tag=tag_chunk, show=True, parent=parent, default_value=0)
    dpg.add_text(desc_interval, parent=parent)
    dpg.add_input_int(tag=tag_interval, show=True, parent=parent, default_value=0)
    return t1
