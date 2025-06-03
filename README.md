# Disaster Routing Simulator

In order to run the project, follow the steps outline in the Setup section and run the command in the Running the project section.

## Setup

This project requires **Python 3.10+**, and Java


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

### Install Java
If you are using macOS, you can install Java using Homebrew:

```bash
# Install Java 23 and Maven
brew install openjdk@23 maven

# Add Java 23 to the PATH, since Homebrew does not automatically link Java
echo 'export JAVA_HOME="$(brew --prefix openjdk@23)"' >> ~/.zshrc
echo 'export PATH="$JAVA_HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

> **Note:** If you're using **Bash**, update `~/.bashrc` instead of `~/.zshrc`.

Before running the project, install the MATSim dependencies:

```bash
# Install MATSim dependencies
cd simulator
mvn clean install
```


## Running the project

To run the project, execute the following command:

```bash
python src/main.py
```
This will open a browser showcasing the dashboard.
N.B.: SimWrapper does not work with the Safari browser. Paste the link into another browser.

## Developer Guide


The program includes a developer mode, which skips the GUI and starts the program directly in Copenhagen,
with Amager set as the danger zone.

```bash
python src/main.py -dev
```
The program also includes a matsim only mode, 
which skips the GUI and starts the MATSim simulation directly on precomputed CPH routes.

```bash
python src/main.py -matsim-only
```


The program includes a small developer mode, which skips the GUI and starts the program directly in Copenhagen,
with a very small part of Amager as the danger zone.

```bash
python src/main.py -small
```

The program also includes a GUI-only mode, which runs the graphical interface without starting the simulation.
Useful for testing the UI separately.

```bash
python src/main.py -gui-only
```

## Running the tests

To run the tests, execute the following command:

```bash
poetry run pytest
```

To add a new test, create a new file in the `tests` directory with the following name pattern: `test_*.py`.


