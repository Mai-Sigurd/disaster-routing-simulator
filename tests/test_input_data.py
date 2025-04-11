import pytest

from input_data import InputData, PopulationType, SimulationType, verify_input


def test_verify(
    monkeypatch: pytest.MonkeyPatch, osm_graph_bbox: str, danger_zone: str
) -> None:
    input_data = InputData(
        population_type=PopulationType.GEO_JSON_FILE,
        simulation_type=SimulationType.CASE_STUDIES,
        population_number=0,
        danger_zones_geopandas_json="",
        worldpop_filepath="",
    )
    assert verify_input(input_data) == (True, "")

    input_data = InputData(
        population_type=PopulationType.TIFF_FILE,
        simulation_type=SimulationType.EXPLORE,
        population_number=0,
        danger_zones_geopandas_json=danger_zone,
        worldpop_filepath="",
    )
    assert verify_input(input_data) == (False, "Worldpop tiff file path is empty")

    input_data = InputData(
        population_type=PopulationType.TIFF_FILE,
        simulation_type=SimulationType.EXPLORE,
        population_number=0,
        danger_zones_geopandas_json=danger_zone,
        worldpop_filepath="filenothere",
    )
    assert verify_input(input_data) == (False, "Worldpop tiff file not found")

    input_data = InputData(
        population_type=PopulationType.NUMBER,
        simulation_type=SimulationType.EXPLORE,
        population_number=0,
        danger_zones_geopandas_json=danger_zone,
        worldpop_filepath="",
    )
    assert verify_input(input_data) == (
        False,
        "Population number must be greater than 0",
    )

    input_data = InputData(
        population_type=PopulationType.GEO_JSON_FILE,
        simulation_type=SimulationType.CASE_STUDIES,
        population_number=0,
        danger_zones_geopandas_json="Invalid input",
        worldpop_filepath="",
    )
    assert verify_input(input_data) == (
        False,
        "CPH city, danger zone is invalid geojson",
    )
