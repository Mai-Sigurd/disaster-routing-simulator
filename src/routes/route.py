import logging

import geopandas as gpd
import numpy as np
from numpy.typing import NDArray
from tqdm import tqdm

from data_loader.population.utils import NODE_ID, POPULATION
from routes.route_utils import path


class Route:
    def __init__(
        self, route_path: path, num_people_on_route: int, departure_times: list[int]
    ) -> None:
        if len(departure_times) != num_people_on_route:
            logging.fatal(
                "Number of departure times must equal the number of people on route."
            )
            raise ValueError("Mismatch between departure times and number of people on route.")
        self.path = route_path
        self.num_people_on_route = num_people_on_route
        self.departure_times = departure_times


def _departure_times(total_population: int, start: int, end: int) -> NDArray[np.int_]:
    """
    Introduces different departure times for the persons taking the given route, spread on a normal distribution
    between the given start and end times.
    :param total_population: The total population.
    :param start: start of normal distribution. Given in seconds.
    :param end: end of normal distribution. Given in seconds.
    """
    mean = (start + end) / 2  # mean
    std_dev = (end - start) / 6  # Approx. 99.7% of values within range
    rng = np.random.default_rng()
    departures = rng.normal(loc=mean, scale=std_dev, size=total_population).astype(
        np.int_
    )
    return departures


def _get_num_people_on_route(
    route_path: list[str], population_data: gpd.GeoDataFrame, cars_per_person: float
) -> int:
    """
    Returns the number of people on a given route.
    :param route_path: A list of node IDs representing the route.
    :param population_data: A GeoDataFrame containing the population data.
    :param cars_per_person: The number of cars per person.
    :return: The number of people on the route.
    """
    return int(
        population_data[population_data[NODE_ID] == route_path[0]].iloc[0][POPULATION]
        * cars_per_person
    )


def _get_total_population(
    population_data: gpd.GeoDataFrame, cars_per_person: float
) -> int:
    result = population_data[POPULATION].sum()
    if result is None:
        logging.fatal("Population data is empty")
    return int(result * cars_per_person)


def create_route_objects(
    list_of_paths: list[path],
    population_data: gpd.GeoDataFrame,
    start: int,
    end: int,
    cars_per_person: float,
) -> list[Route]:
    """
    Creates a list of Route objects from a list of routes.

    :param list_of_paths: A list of routes.
    :param population_data: A GeoDataFrame containing the population data.
    :param start: start of normal distribution. Given in seconds.
    :param end: end of normal distribution. Given in seconds.
    :param cars_per_person: The number of cars per person.
    :return: A list of Route objects.
    """
    total_population = _get_total_population(population_data, cars_per_person)
    result = []
    departure_times = _departure_times(total_population, start, end)
    for p in tqdm(list_of_paths):
        route_path = p
        num_people_on_route = _get_num_people_on_route(
            route_path, population_data, cars_per_person
        )
        selected, departure_times = np.split(departure_times, [num_people_on_route])
        route_object = Route(route_path, num_people_on_route, list(selected))
        result.append(route_object)
    return result
