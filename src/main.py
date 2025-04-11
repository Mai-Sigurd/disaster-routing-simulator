import argparse
import logging
import signal

from config import (
    ONE_HOUR,
    TWO_MINUTES,
    ProgramConfig,
    set_amager_input_data,
    set_dev_input_data,
    set_ravenna_input_data,
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
    SimulationType,
)
from matsim_io import MATSIM_DATA_DIR, mat_sim_files_exist, write_network, write_plans
from routes.route import Route, create_route_objects
from routes.route_utils import path

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname}] {message}",
    style="{",
)


def simulate(program_config: ProgramConfig) -> None:
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
    write_plans(routes, plan_filename="plans.xml")


def save_analysis_files(program_config: ProgramConfig) -> None:
    """
    Save the analysis files to the MATSIM_DATA_DIR.
    """
    write_g_and_dangerzone_data(
        danger_zone=program_config.danger_zones,
        filepath=MATSIM_DATA_DIR / "OUTPUT" / "dangerzone_data.csv",
    )


def run_simwrapper_serve(simulation_type: SimulationType) -> None:
    """
    Run the SimWrapper server.
    """
    logging.info("Running SimWrapper server...")
    if simulation_type == SimulationType.CASE_STUDIES:
        # TODO SimWrapper server code here, simwrapper serve in case studies output folder
        pass
    else:
        # TODO SimWrapper server code here, simwrapper serve in explore output folder
        pass


def start_up(input_data: InputData, run_simulater: bool) -> None:
    """
    Start up the program.
    """
    if run_simulater:
        logging.info("Starting up...")
        program_config = controller_input_data(input_data)
        logging.info("Controller input data done")
        logging.info("Route algos done")
        simulate(program_config)
        run_matsim()
        save_analysis_files(program_config)
    run_simwrapper_serve(input_data.simulationType)


def main(args: argparse.Namespace) -> None:
    match args:
        case args.matsim_only:
            if mat_sim_files_exist("plans.xml.gz", "network.xml.gz"):
                start_up(None, False)
            else:
                logging.fatal(
                    "Matsim flag set as input but there are No MATSim files found"
                )
                raise SystemExit
        case args.gui_only:
            print("here????")
            input_data = gui_handler()

            return
        case args.dev:
            start_up(set_dev_input_data(), True)
        case args.small:
            start_up(set_small_data_input_data(), True)
        case args.amager:
            start_up(set_amager_input_data(), True)
        case args.ravenna:
            start_up(set_ravenna_input_data(), True)
        case _:  ## normal program, no flag set
            input_data = gui_handler()
            print(input_data)
            start_up(
                input_data,
                run_simulater=input_data.simulationType == SimulationType.EXPLORE,
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
        help="Enable dev mode (skips GUI), and uses small danger zone on amager",
    )
    group.add_argument("-amager", action="store_true", help="Use Amager danger zone")
    group.add_argument("-ravenna", action="store_true", help="Use Ravenna danger zone")
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
    main(args)
