from sys import implementation

import geopandas as gpd
from tqdm import tqdm
import numpy as np

from data_loader.population.utils import NODE_ID, POPULATION
from routes.route_utils import path


class Route:
    def __init__(
        self, route_path: path, num_people_on_route: int, depature_times: list[int]
    ) -> None:
        self.path = route_path
        self.num_people_on_route = num_people_on_route
        self.departure_times: list[int] = depature_times


def _departure_times(total_population: int, start: int, end: int) -> list[int]:
    """
    Introduces different departure times for the persons taking the given route, spread on a normal distribution
    between the given start and end times.
    :param routes: A list of Route objects.
    :param total_population: The total population.
    :param start: start of normal distribution. Given in seconds.
    :param end: end of normal distribution. Given in seconds.
    """
    mean = (start + end) / 2  # mean
    std_dev = (end - start) / 6  # Approx. 99.7% of values within range
    rng = np.random.default_rng()
    departures = rng.normal(loc=mean, scale=std_dev, size=total_population)
    # Clip values to ensure they are within [start, end] and round to nearest second
    departures = np.clip(np.round(departures), start, end).astype(int)
    raise NotImplementedError("Implement this function")


def create_route_objects(
    list_of_paths: list[path],
    population_data: gpd.GeoDataFrame,
    start: int,
    end: int,
    cars_per_person: int,
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
    total_population = population_data[POPULATION].sum()
    result = []
    for p in tqdm(list_of_paths):
        route_path = p
        num_people_on_route = int(
            population_data[population_data[NODE_ID] == p[0]].iloc[0][POPULATION]
            / cars_per_person
        )

        route_object = Route(route_path, num_people_on_route, [0])
        result.append(route_object)
    return result
