import argparse
import logging
import signal

from config import (
    ONE_HOUR,
    TWO_MINUTES,
    ProgramConfig,
    set_dev_input_data,
    set_small_data_input_data,
)
from controller import (
    controller_input_data,
    gui_close,
    gui_handler,
    run_matsim,
    write_g_and_dangerzone_data,
)
from input_data import (
    InputData,
    verify_input,
)
from matsim_io import MATSIM_DATA_DIR, mat_sim_files_exist, write_network, write_plans
from routes.route import Route, create_route_objects
from routes.route_utils import path

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname}] {message}",
    style="{",
)


def set_pre_existing_input_data(args: argparse.Namespace) -> InputData:
    if args.dev:
        input_data = set_dev_input_data()
        mode = "dev"
    elif args.small:
        input_data = set_small_data_input_data()
        mode = "small"
    else:
        logging.fatal("Invalid mode")
        raise ValueError("Invalid mode")
    logging.info(f"{mode} mode enabled")
    logging.info(input_data.pretty_summary())
    input_is_okay, error_message = verify_input(input_data)
    if not input_is_okay:
        logging.info("Error message: %s", error_message)
    return input_data


def start_up(args: argparse.Namespace) -> ProgramConfig:
    dev_modes = args.dev or args.small
    if not dev_modes:
        input_data = gui_handler()
    else:
        input_data = set_pre_existing_input_data(args)
    return controller_input_data(input_data)


def main(args: argparse.Namespace) -> None:
    mat_sim_only = args.matsim_only and mat_sim_files_exist(
        "plans.xml.gz", "network.xml.gz"
    )
    if args.matsim_only and not mat_sim_only:
        logging.info("No MATSim files found, creating the files")
        args.dev = True
    if not mat_sim_only:
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
        logging.info(
            "Amount of people: %s", sum([r.num_people_on_route for r in routes])
        )
        logging.info(
            "Amount of nodes that could not reach dangerzone: %s",
            len(program_config.origin_points) - len(routes),
        )
        write_network(program_config.G, network_name="Copenhagen")
        write_plans(routes, plan_filename="plans.xml")

    run_matsim()
    if not mat_sim_only:
        write_g_and_dangerzone_data(
            danger_zone=program_config.danger_zones,
            filepath=MATSIM_DATA_DIR / "OUTPUT" / "dangerzone_data.csv",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-dev",
        action="store_true",
        help="Enable dev mode (skips GUI), and uses dev input data",
    )
    group.add_argument(
        "-small",
        action="store_true",
        help="Enable dev mode (skips GUI), and uses a very small dangerzone",
    )
    group.add_argument(
        "-gui-only", action="store_true", help="Run GUI only (without simulation)"
    )
    group.add_argument(
        "-matsim-only",
        action="store_true",
        help="Run Matsim only (precomputed routes on Copenhagen)",
    )
    args = parser.parse_args()
    signal.signal(signal.SIGTSTP, gui_close)

    if args.gui_only:
        start_up(args)
    else:
        main(args)
