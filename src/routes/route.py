import logging
from typing import Tuple

import geopandas as gpd
import numpy as np
from numpy.typing import NDArray
from tqdm import tqdm

from data_loader.population import get_total_population
from data_loader.population.population_utils import NODE_ID, POPULATION
from routes.route_utils import path


class Route:
    def __init__(
        self, route_path: path, num_people_on_route: int, departure_times: list[int]
    ) -> None:
        if len(departure_times) != num_people_on_route:
            logging.fatal(
                "Number of departure times must equal the number of people on route."
            )
            raise ValueError(
                "Mismatch between departure times and number of people on route."
            )
        self.path = route_path
        self.num_people_on_route = num_people_on_route
        self.departure_times = departure_times

    def add_remainder(self, remainder: int, departures: list[int]) -> None:
        """
        Adds a remainder to the route.
        :param remainder: The number of people on the route.
        :param departures: A list of departure times.
        """
        self.num_people_on_route += remainder
        self.departure_times.extend(departures)


def _get_normal_dist_departure_time_list(
    total_population: int, start: int, end: int
) -> NDArray[np.int_]:
    """
    Introduces different departure times for the persons taking the given route, spread on a normal distribution
    between the given start and end times.
    :param total_population: The total population.
    :param start: start of normal distribution. Given in seconds.
    :param end: end of normal distribution. Given in seconds.
    """
    mean = (start + end) / 2
    std_dev = (end - start) / 6  # Approx. 99.7% of values within range
    rng = np.random.default_rng()
    departures = rng.normal(loc=mean, scale=std_dev, size=total_population).astype(
        np.int_
    )
    return departures


def _get_num_people_on_route(
    origin_point: str, population_data: gpd.GeoDataFrame, cars_per_person: float
) -> int:
    """
    Returns the number of people on a given route.
    :param origin_point: The origin point of the route.
    :param population_data: A GeoDataFrame containing the population data.
    :param cars_per_person: The number of cars per person.
    :return: The number of people on the route.
    """
    return int(
        population_data[population_data[NODE_ID] == origin_point].iloc[0][POPULATION]
        * cars_per_person
    )


def create_route_objects(
    origin_to_paths: dict[str, list[path]],
    population_data: gpd.GeoDataFrame,
    start: int,
    end: int,
    cars_per_person: float,
) -> list[Route]:
    """
    Creates a list of Route objects from a list of routes.

    :param origin_to_paths: A dictionary mapping origin points to a list of paths.
    :param population_data: A GeoDataFrame containing the population data.
    :param start: start of normal distribution. Given in seconds.
    :param end: end of normal distribution. Given in seconds.
    :param cars_per_person: The number of cars per person.
    :return: A list of Route objects.
    """
    total_population = get_total_population(population_data, cars_per_person)
    result = []
    departure_times = _get_normal_dist_departure_time_list(total_population, start, end)
    for origin_point in tqdm(origin_to_paths.keys()):
        paths = origin_to_paths[origin_point]
        num_people_on_route = _get_num_people_on_route(
            origin_point, population_data, cars_per_person
        )
        number_of_diverse_routes = len(paths)
        if number_of_diverse_routes < 1:
            logging.warning(
                f"Origin point {origin_point} has no routes to safety. Skipping."
            )
            continue
        elif number_of_diverse_routes == 1:
            route_path = paths[0]
            route_object, departure_times = _create_route_object(
                departure_times=departure_times,
                path=route_path,
                num_people_on_route=num_people_on_route,
            )
            result.append(route_object)
        elif num_people_on_route < len(paths):
            for i in range(num_people_on_route):
                route_path = paths[i]
                route_object, departure_times = _create_route_object(
                    departure_times=departure_times,
                    path=route_path,
                    num_people_on_route=num_people_on_route,
                )
                result.append(route_object)
        else:
            routes, departure_times = population_diversify_route_math(
                num_people_on_route=num_people_on_route,
                paths=paths,
                departure_times=departure_times,
            )
            result.extend(routes)
    return result


def population_diversify_route_math(
    num_people_on_route: int, paths: list[path], departure_times: NDArray[np.int_]
) -> Tuple[list[Route], NDArray[np.int_]]:
    """
    Diversifies the routes for a given number of people on a route.
    :param num_people_on_route: The number of people on the route.
    :param paths: A list of paths.
    :param departure_times: A list of departure times.
    :return: A list of Route objects.
    """
    num, remainder = divmod(num_people_on_route, len(paths))
    result = []
    for p in paths:
        route, departure_times = _create_route_object(
            departure_times=departure_times, path=p, num_people_on_route=num
        )
        result.append(route)
    selected_remainder, departure_times = np.split(departure_times, [remainder])
    result[0].add_remainder(remainder=remainder, departures=list(selected_remainder))
    return result, departure_times


def _create_route_object(
    departure_times: NDArray[np.int_], path: path, num_people_on_route: int
) -> Tuple[Route, NDArray[np.int_]]:
    """
    Creates a Route object from a list of departure times and a path.
    :param departure_times: A list of departure times.
    :param path: A path.
    :param num_people_on_route: The number of people on the route.
    :return: A Route object.
    """
    selected, departure_times = np.split(departure_times, [num_people_on_route])
    route_object = Route(path, num_people_on_route, list(selected))
    return route_object, departure_times
