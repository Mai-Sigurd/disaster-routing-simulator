import os

from setuptools import find_packages, setup

abs_path = os.path.abspath(os.path.dirname(__file__))

setup(
    name="routing_lib",
    version="0.2.3",
    license="MIT",
    description="Small package with alternative routing algorithms and measures.",
    long_description=open(os.path.join(abs_path, "README.rst")).read(),
    author="Ludovico Lemma",
    author_email="lwdovico@protonmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/lwdovico/routing-lib",
    keywords="Utils",
    install_requires=[
        "matplotlib",
        "numpy",
        "Shapely",
        "Fiona",
        "rtree",
        "pyproj",
        "pygeos",
        "scikit-mobility",
        "geopandas",
        "compress-json",
        "tqdm",
        "igraph",
        "eclipse-sumo",
        "sumolib",
        "libsumo",
        "seaborn",
    ],
)
