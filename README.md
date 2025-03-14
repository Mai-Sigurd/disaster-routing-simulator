# Disaster Routing Simulator

## Setup

This project requires **Python 3.12+**.

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

### MATSim

To run MATSim, you need to install **Java 23** and **Maven**.
If you are using macOS, you can install them using Homebrew:

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
### Dev mode
The program supports dev mode which skips the gui, and starts the program on Copenhagen with Amager as the danger zone. 
```bash
python src/main.py -dev
```

## Running the tests

To run the tests, execute the following command:

```bash
poetry run pytest
```

To add a new test, create a new file in the `tests` directory with the following name pattern: `test_*.py`.
