import geopandas as gpd
import pytest

import routes.route as route


def test_create_route_object(monkeypatch: pytest.MonkeyPatch) -> None:
    dict_of_paths = {"1": [["1", "2"]], "2": [["2", "1"]]}
    population_data = gpd.GeoDataFrame(data={"id": ["1", "2"], "pop": [10, 10]})
    start = 0
    end = 1000
    cars_per_person = 1.0
    create_route_objects = route.create_route_objects(
        dict_of_paths, population_data, start, end, cars_per_person
    )
    assert len(create_route_objects) == 2
    assert create_route_objects[0].num_people_on_route == 10
    assert create_route_objects[1].num_people_on_route == 10


def test_create_route_object_error_no_population_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dict_of_paths = {"1": [["1", "2"], ["1", "2"], ["1", "2"]]}
    population_data = gpd.GeoDataFrame(data={"id": ["1", "2"], "pop": ["", ""]})
    start = 0
    end = 1000
    cars_per_person = 1.0
    try:
        route.create_route_objects(
            dict_of_paths, population_data, start, end, cars_per_person
        )
    except ValueError as e:
        assert str(e) == "Population data is empty"

    dict_of_paths = {"1": [["1", "2"], ["1", "2"], ["1", "2"]]}
    population_data = gpd.GeoDataFrame(data={"id": ["1", "2"], "pop": [0, 0]})
    start = 0
    end = 1000
    cars_per_person = 1.0
    try:
        route.create_route_objects(
            dict_of_paths, population_data, start, end, cars_per_person
        )
    except ValueError as e:
        assert str(e) == "Population data is 0"


def test_create_route_object_uneven(monkeypatch: pytest.MonkeyPatch) -> None:
    dict_of_paths = {"1": [["1", "2"]], "2": [["2", "1"]]}
    population_data = gpd.GeoDataFrame(data={"id": ["1", "2"], "pop": [7, 5]})
    start = 0
    end = 1000
    cars_per_person = 1.0
    create_route_objects = route.create_route_objects(
        dict_of_paths, population_data, start, end, cars_per_person
    )
    assert len(create_route_objects) == 2
    assert create_route_objects[0].num_people_on_route == 7
    assert create_route_objects[1].num_people_on_route == 5


def test_get_num_people_on_route() -> None:
    population_data = gpd.GeoDataFrame(data={"id": ["1", "2"], "pop": [10, 20]})
    cars_per_person = 1.0
    result = route._get_num_people_on_route("1", population_data, cars_per_person)
    assert result == 10


def test__get_total_population() -> None:
    population_data = gpd.GeoDataFrame(data={"pop": [10, 20]})
    result = route._get_total_population(population_data, 1.0)
    assert result == 30


def test_create_route_object_full(monkeypatch: pytest.MonkeyPatch) -> None:
    dict_of_paths = {"1": [["1", "2"]], "2": [["2", "1"]]}
    population_data = gpd.GeoDataFrame(data={"id": ["1", "2"], "pop": [7, 5]})
    start = 0
    end = 1000
    cars_per_person = 0.5
    create_route_objects = route.create_route_objects(
        dict_of_paths, population_data, start, end, cars_per_person
    )
    assert len(create_route_objects) == 2
    assert create_route_objects[0].num_people_on_route == 3
    assert create_route_objects[1].num_people_on_route == 2
