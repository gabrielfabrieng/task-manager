"""
End-to-end happy path: register -> create task -> mark done.

Exercises the full stack through Nginx: React SPA -> DRF -> Postgres.
"""

from __future__ import annotations

import uuid

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def _tid(name: str) -> tuple[str, str]:
    return (By.CSS_SELECTOR, f'[data-testid="{name}"]')


def test_register_create_and_complete_task(driver, wait, base_url):
    suffix = uuid.uuid4().hex[:8]
    username = f"e2e_{suffix}"

    # --- Register ---
    driver.get(f"{base_url}/register")
    wait.until(EC.presence_of_element_located(_tid("register-form")))
    driver.find_element(*_tid("register-username")).send_keys(username)
    driver.find_element(*_tid("register-email")).send_keys(f"{username}@example.com")
    driver.find_element(*_tid("register-password")).send_keys("StrongPass123")
    driver.find_element(*_tid("register-submit")).click()

    # --- Lands on the tasks page ---
    wait.until(EC.text_to_be_present_in_element(_tid("current-user"), username))

    # --- Create a task ---
    title = f"Task {suffix}"
    driver.find_element(*_tid("task-title")).send_keys(title)
    driver.find_element(*_tid("task-add")).click()

    wait.until(EC.presence_of_element_located(_tid("task-item")))
    assert title in driver.find_element(*_tid("task-item-title")).text

    # --- Mark it done ---
    driver.find_element(*_tid("task-toggle")).click()
    # Wait until the mutation lands and the item is re-rendered as done.
    wait.until(
        lambda d: "done" in d.find_element(*_tid("task-item")).get_attribute("class")
    )


def test_login_rejects_bad_credentials(driver, wait, base_url):
    driver.get(f"{base_url}/login")
    wait.until(EC.presence_of_element_located(_tid("login-form")))
    driver.find_element(*_tid("login-username")).send_keys("nobody")
    driver.find_element(*_tid("login-password")).send_keys("wrongpassword")
    driver.find_element(*_tid("login-submit")).click()
    wait.until(EC.presence_of_element_located(_tid("login-error")))
    assert driver.find_element(*_tid("login-error")).is_displayed()
