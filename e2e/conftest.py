"""Selenium E2E fixtures.

The tests drive a remote Chromium (Selenium standalone) against the running
app served by Nginx. Both hosts come from the environment so the same tests run
locally and in CI.
"""

from __future__ import annotations

import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("E2E_BASE_URL", "http://nginx")
SELENIUM_URL = os.environ.get("SELENIUM_URL", "http://selenium:4444/wd/hub")


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    drv = webdriver.Remote(command_executor=SELENIUM_URL, options=options)
    drv.set_window_size(1280, 900)
    yield drv
    drv.quit()


@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 15)
