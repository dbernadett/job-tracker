import os

import pytest
from bs4 import BeautifulSoup


@pytest.fixture
def data_folder():
    return os.path.join(os.path.realpath(os.path.dirname(__file__)), "data")


@pytest.fixture
def zoox_html(data_folder):
    with open(os.path.join(data_folder, "html/zoox.html"), "r") as file:
        html = file.read()
    return html


@pytest.fixture
def cruise_html(data_folder):
    with open(os.path.join(data_folder, "html/cruise.html"), "r") as file:
        html = file.read()
    return html


@pytest.fixture
def zoox_bs(zoox_html):
    return BeautifulSoup(zoox_html, features="html.parser")


@pytest.fixture
def cruise_bs(cruise_html):
    return BeautifulSoup(cruise_html, features="html.parser")
