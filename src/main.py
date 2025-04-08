import argparse
import logging
import signal

from config import ONE_HOUR, TWO_MINUTES, ProgramConfig
from controller import (
    controller_input_data,
    gui_close,
    gui_handler,
    run_matsim,
    set_dev_input_data,
)
from input_data import (
    verify_input,
)
from matsim_io import write_network, write_plans
from routes.route import Route, create_route_objects
from routes.route_utils import path

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname}] {message}",
    style="{",
)


def start_up(args: argparse.Namespace) -> ProgramConfig:
    if not args.dev:
        input_data = gui_handler()
    else:
        logging.info("Dev mode enabled")
        input_data = set_dev_input_data()
        logging.info(input_data.pretty_summary())
        input_is_okay, error_message = verify_input(input_data)
        if not input_is_okay:
            logging.info("Error message: %s", error_message)
    return controller_input_data(input_data)


def main(args: argparse.Namespace) -> None:
    program_config = start_up(args)
    # TODO add more algos, currently there are two
    paths: list[path] = program_config.route_algos[0].route_to_safety(
        program_config.origin_points, program_config.danger_zones, program_config.G
    )
    routes: list[Route] = create_route_objects(
        list_of_paths=paths,
        population_data=program_config.danger_zone_population_data,
        start=TWO_MINUTES,
        end=ONE_HOUR,
        cars_per_person=program_config.cars_per_person,
    )

    logging.info("Routes done")
    logging.info("Stats ---------------------")
    logging.info("Amount of routes: %s", len(routes))
    logging.info("Amount of people: %s", sum([r.num_people_on_route for r in routes]))
    logging.info(
        "Amount of nodes that could not reach dangerzone: %s",
        len(program_config.origin_points) - len(routes),
    )

    write_network(program_config.G, network_name="Copenhagen")
    write_plans(routes)

    run_matsim()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-dev", action="store_true", help="Enable dev mode (skips GUI)")
    group.add_argument(
        "-gui-only", action="store_true", help="Run GUI only (without simulation)"
    )
    args = parser.parse_args()

    signal.signal(signal.SIGTSTP, gui_close)

    if args.gui_only:
        start_up(args)
    else:
        main(args)
