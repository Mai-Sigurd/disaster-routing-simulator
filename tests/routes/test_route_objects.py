import geopandas as gpd
import pytest

import routes.route as route


def test_create_route_object(monkeypatch: pytest.MonkeyPatch) -> None:

    def _get_num_people_on_route(route_path: list[str], population_data: gpd.GeoDataFrame, cars_per_person: float) -> int:
        return 10
    def _get_total_population(population_data: gpd.GeoDataFrame) -> int:
        return 30
    monkeypatch.setattr(route,"_get_num_people_on_route", _get_num_people_on_route)
    monkeypatch.setattr(route,"_get_total_population", _get_total_population)
    list_of_paths = [["1", "2"], ["1", "2"], ["1", "2"]]
    population_data = gpd.GeoDataFrame()
    start = 0
    end = 1000
    cars_per_person = 1.0
    create_route_objects = route.create_route_objects(list_of_paths, population_data, start, end, cars_per_person)
    assert len(create_route_objects) == 3
    assert create_route_objects[0].num_people_on_route == 10
    assert create_route_objects[1].num_people_on_route == 10
    assert create_route_objects[2].num_people_on_route == 10

def test_create_route_object_uneven(monkeypatch: pytest.MonkeyPatch) -> None:

    def _get_num_people_on_route(route_path: list[str], population_data: gpd.GeoDataFrame, cars_per_person: float) -> int:
        return 7
    def _get_total_population(population_data: gpd.GeoDataFrame) -> int:
        return 21
    monkeypatch.setattr(route,"_get_num_people_on_route", _get_num_people_on_route)
    monkeypatch.setattr(route,"_get_total_population", _get_total_population)
    list_of_paths = [["1", "2"], ["1", "2"], ["1", "2"]]
    population_data = gpd.GeoDataFrame()
    start = 0
    end = 1000
    cars_per_person = 1.0
    create_route_objects = route.create_route_objects(list_of_paths, population_data, start, end, cars_per_person)
    assert len(create_route_objects) == 3
    assert create_route_objects[0].num_people_on_route == 7
    assert create_route_objects[1].num_people_on_route == 7
    assert create_route_objects[2].num_people_on_route == 7

def test_get_num_people_on_route() -> None:
    route_path = ["1", "2"]
    population_data = gpd.GeoDataFrame(data={"id": ["1", "2"], "pop": [10, 20]})
    cars_per_person = 1.0
    result = route._get_num_people_on_route(route_path, population_data, cars_per_person)
    assert result == 10




def test__get_total_population() -> None:
    population_data = gpd.GeoDataFrame(data={"pop": [10, 20]})
    result = route._get_total_population(population_data)
    assert result == 30
