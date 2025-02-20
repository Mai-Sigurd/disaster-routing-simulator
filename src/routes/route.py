import geopandas as gpd
from tqdm import tqdm

from data_loader.population.population import NODE_ID, POPULATION
from routes.route_utils import path


class Route:
    def __init__(self, route_path: path, num_people_on_route: int) -> None:
        self.path = route_path
        self.num_people_on_route = num_people_on_route
        self.departure_times: dict[int, int] = {0: num_people_on_route}

    def introduce_departure_times(self, chunks: int, interval: int) -> None:
        """
        Introduces different departure times for the persons taking the given route.

        :param chunks: In how many different chunks should the persons on the route depart.
        :param interval: How long should the interval between each departure be. Given in seconds.
        :return: A dictionary of departure times where keys are seconds after midnight and values are the number of people departing on that time.
        """
        departure_times: dict[int, int] = {}
        people_per_interval = int(self.num_people_on_route / chunks)
        remaining_people = self.num_people_on_route % chunks

        seconds_from_midnight = 0
        if chunks < self.num_people_on_route:
            for i in range(chunks):
                count = people_per_interval + (
                    1 if i < remaining_people else 0
                )  # Distribute remainder evenly
                departure_times[seconds_from_midnight] = count
                seconds_from_midnight += interval
        else:  # There are more chunks than people, so there will be 1 person in the first chunk(s) and then 0 in the remaining. The remaining will not even be present in the departure_times dict.
            for i in range(self.num_people_on_route):
                departure_times[seconds_from_midnight] = 1
                seconds_from_midnight += interval

        self.departure_times = departure_times


def create_route_objects(
    list_of_paths: list[path],
    population_data: gpd.GeoDataFrame,
    chunks: int,
    interval: int,
) -> list[Route]:
    """
    Creates a list of Route objects from a list of routes.

    :param list_of_paths: A list of routes.
    :param population_data: A GeoDataFrame containing the population data.
    :param chunks: In how many different chunks should the persons on the route depart.
    :param interval: How long should the interval between each departure be. Given in seconds.
    :return: A list of Route objects.
    """
    result = []
    for p in tqdm(list_of_paths):
        route_path = p
        num_people_on_route = int(
            population_data[population_data[NODE_ID] == p[0]].iloc[0][POPULATION]
        )

        route_object = Route(route_path, num_people_on_route)
        route_object.introduce_departure_times(chunks, interval)
        result.append(route_object)
    return result
