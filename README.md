# Disaster Routing Simulator

## Setup

### Virtual environment

To create a virtual environment and install the dependencies, execute the following commands:

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install poetry
poetry install
```

### MATSim GUI

To setup and use the MATSim GUI, follow the instructions in
the [MATSim Installation Guide](https://matsim.org/install/#use-the-matsim-gui)

The MATSim configuration file is located at [here](data/matsim/config.xml).

## Running the tests

To run the tests, execute the following command:

```bash
poetry run pytest
```

To add a new test, create a new file in the `tests` directory with the following name pattern: `test_*.py`.
