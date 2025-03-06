# Stage 1: Maven Build
FROM maven:3-eclipse-temurin-23 AS build
WORKDIR /app/simulator

# Download Maven dependencies (this will be cached)
COPY simulator/pom.xml .
RUN mvn dependency:go-offline

# Build the Maven project
COPY simulator .
RUN mvn package

# Stage 2: Python Environment
FROM python:3.12-slim AS python_base
WORKDIR /app

# Install GDAL and build tools required for the fiona and rasterio Python dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin libgdal-dev \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install and configure  Poetry
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.in-project true

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Stage 3: Final Image (Maven + Python)
FROM maven:3-eclipse-temurin-23 AS final
WORKDIR /app

# Copy built Java application and Python environment
COPY --from=build /app/simulator/target /app/simulator/target
COPY --from=python_base /usr/local /usr/local
COPY --from=python_base /app/.venv /app/.venv

# Copy Python project files
COPY pyproject.toml poetry.lock ./
COPY src/ src/
COPY data/ /app/data/

# Set environment variables (Java is already installed in this image)
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV VIRTUAL_ENV="/app/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Default command to run the application
CMD ["poetry", "run", "python", "src/main.py"]
