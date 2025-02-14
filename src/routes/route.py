class Route:
    def __init__(self, path: list[str], num_people_on_route: int) -> None:
        self.path = path
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
        for i in range(chunks):
            count = people_per_interval + (
                1 if i < remaining_people else 0
            )  # Distribute remainder evenly
            departure_times[seconds_from_midnight] = count
            seconds_from_midnight += interval

        self.departure_times = departure_times
