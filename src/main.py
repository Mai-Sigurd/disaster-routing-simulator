import argparse
import logging
import signal
import webbrowser

from config import (
    CASE_STUDIES_OUTPUT_FOLDER,
    EXPLORE_OUTPUT_FOLDER,
    SIM_WRAPPER_LINK,
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
    sim_wrapper_serve,
    write_danger_zone_data,
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


def simulate(program_config: ProgramConfig) -> dict[str, int]:
    paths: list[path] = program_config.route_algos[0].route_to_safety(
        program_config.origin_points, program_config.danger_zones, program_config.G
    )
    routes: list[Route] = create_route_objects(
        list_of_paths=paths,
        population_data=program_config.danger_zone_population_data,
        start=0,
        end=program_config.departure_end_time_sec,
        cars_per_person=program_config.cars_per_person,
    )
    logging.info("Routes done")
    stats = {
        "Amount of routes": len(routes),
        "Amount of nodes with no route to safety": len(program_config.origin_points)
        - len(routes),
    }
    write_network(program_config.G, network_name="Copenhagen")
    write_plans(routes, plan_filename="plans.xml")
    return stats


def save_analysis_files(program_config: ProgramConfig, stats: dict[str, int]) -> None:
    """
    Save the analysis files to the MATSIM_DATA_DIR.
    """
    write_danger_zone_data(
        program_conf=program_config,
        stats=stats,
        filepath=MATSIM_DATA_DIR / "OUTPUT" / "dangerzone_data.csv",
    )


def run_simwrapper_serve(simulation_type: SimulationType, path: str = "") -> None:
    """
    Run the SimWrapper server.
    """
    webbrowser.open(SIM_WRAPPER_LINK)
    logging.info("SimWrapper link: %s", SIM_WRAPPER_LINK)
    if path == "":
        logging.info("Running SimWrapper server...")
        if simulation_type == SimulationType.CASE_STUDIES:
            sim_wrapper_serve(CASE_STUDIES_OUTPUT_FOLDER)
        else:
            sim_wrapper_serve(EXPLORE_OUTPUT_FOLDER)
    else:
        sim_wrapper_serve(path)

    logging.info("SimWrapper server done")


def start_up(input_data: InputData, run_simulator: bool) -> None:
    """
    Start up the program.
    """
    if run_simulator:
        logging.info("Starting up...")
        program_config = controller_input_data(input_data)
        logging.info("Controller input data done")
        logging.info("Route algos done")
        stats = simulate(program_config)
        run_matsim()
        save_analysis_files(program_config, stats)
    run_simwrapper_serve(input_data.simulation_type)


def main(args: argparse.Namespace) -> None:
    if args.matsim_only:
        if mat_sim_files_exist("plans.xml.gz", "network.xml.gz"):
            run_matsim()
            run_simwrapper_serve(
                SimulationType.CASE_STUDIES, path=MATSIM_DATA_DIR / "output"
            )
        else:
            logging.fatal(
                "Matsim flag set as input but there are No MATSim files found"
            )
            raise SystemExit
    elif args.gui_only:
        input_data = gui_handler()
        return
    elif args.dev:
        start_up(set_dev_input_data(), True)
    elif args.small:
        start_up(set_small_data_input_data(), True)
    elif args.amager:
        start_up(set_amager_input_data(), True)
    elif args.ravenna:
        start_up(set_ravenna_input_data(), True)
    else:  ## normal program, no flag set
        input_data = gui_handler()
        start_up(
            input_data,
            run_simulator=input_data.simulation_type == SimulationType.EXPLORE,
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
