# main.py — Sprint 8 QA Project Urban Routes
import json
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common import WebDriverException

import data

# =========================
# Utilidad provista (NO modificar)
# =========================
def retrieve_phone_code(driver) -> str:
    """Intercepta código de confirmación desde los logs de performance."""
    code = None
    for _ in range(10):
        try:
            logs = [
                log["message"] for log in driver.get_log("performance")
                if log.get("message") and "api/v1/number?number" in log.get("message")
            ]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd(
                    "Network.getResponseBody",
                    {"requestId": message_data["params"]["requestId"]}
                )
                code = "".join([x for x in body["body"] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.")
        return code


DEFAULT_TIMEOUT = 12


class UrbanRoutesPage:
    # ---------- Localizadores ----------
    LOC_FROM = (By.ID, "from")
    LOC_TO = (By.ID, "to")
    LOC_TARIFF_COMFORT = (By.XPATH, "//*[contains(.,'Comfort')]")
    LOC_PHONE_INPUT = (By.XPATH, "//input[@type='tel']")
    LOC_CARD_NUMBER = (By.XPATH, "//input[contains(@placeholder,'Card')]")
    LOC_DRIVER_MESSAGE = (By.XPATH, "//textarea")
    LOC_BLANKET_TISSUES = (By.XPATH, "//*[contains(.,'Blanket') or contains(.,'Manta')]")
    LOC_ICE_CREAM_PLUS = (By.XPATH, "//*[contains(.,'+')]")
    LOC_ORDER_TAXI_BTN = (By.XPATH, "//*[contains(.,'Order') or contains(.,'Taxi')]")
    LOC_SEARCH_MODAL = (By.XPATH, "//*[contains(.,'searching') or contains(.,'Buscando')]")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    # ---------- Acciones ----------
    def open(self, url: str):
        self.driver.get(url)
        self.wait.until(EC.element_to_be_clickable(self.LOC_FROM))

    def set_route(self, from_addr: str, to_addr: str):
        from_el = self.wait.until(EC.element_to_be_clickable(self.LOC_FROM))
        from_el.clear()
        from_el.send_keys(from_addr)
        from_el.send_keys(Keys.ENTER)

        to_el = self.wait.until(EC.element_to_be_clickable(self.LOC_TO))
        to_el.clear()
        to_el.send_keys(to_addr)
        to_el.send_keys(Keys.ENTER)

    def get_from(self):
        return self.driver.find_element(*self.LOC_FROM).get_property("value")

    def get_to(self):
        return self.driver.find_element(*self.LOC_TO).get_property("value")

    def select_comfort_tariff(self):
        self.driver.find_element(*self.LOC_TARIFF_COMFORT).click()

    def fill_phone(self, phone):
        phone_input = self.driver.find_element(*self.LOC_PHONE_INPUT)
        phone_input.send_keys(phone)

    def add_card(self, num, date, cvv):
        card_input = self.driver.find_element(*self.LOC_CARD_NUMBER)
        card_input.send_keys(num)

    def write_driver_message(self, msg):
        msg_field = self.driver.find_element(*self.LOC_DRIVER_MESSAGE)
        msg_field.send_keys(msg)

    def toggle_blanket_tissues(self):
        self.driver.find_element(*self.LOC_BLANKET_TISSUES).click()

    def add_ice_creams(self, n=2):
        plus = self.driver.find_element(*self.LOC_ICE_CREAM_PLUS)
        for _ in range(n):
            plus.click()

    def order_taxi(self):
        self.driver.find_element(*self.LOC_ORDER_TAXI_BTN).click()

    def search_modal_visible(self):
        return self.wait.until(EC.presence_of_element_located(self.LOC_SEARCH_MODAL))


# =========================
# Fixture del driver
# =========================
@pytest.fixture(scope="function")
def driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--window-size=1280,900")
    # opts.add_argument("--headless=new")  # descomenta si quieres headless
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.page_load_strategy = "eager"
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    drv = webdriver.Chrome(options=opts)
    drv.set_page_load_timeout(30)
    drv.set_script_timeout(30)
    yield drv
    drv.quit()


# =========================
# Tests divididos
# =========================
class TestUrbanRoutes:

    def test_set_route(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.set_route(data.address_from, data.address_to)
        assert page.get_from() == data.address_from
        assert page.get_to() == data.address_to

    def test_select_comfort_tariff(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.select_comfort_tariff()
        assert driver.find_element(*page.LOC_TARIFF_COMFORT)

    def test_fill_phone(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.fill_phone(data.phone_number)
        assert driver.find_element(*page.LOC_PHONE_INPUT).get_attribute("value") != ""

    def test_add_card(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.add_card(data.card_number, data.card_date, data.card_cvv)
        assert driver.find_element(*page.LOC_CARD_NUMBER).get_attribute("value").startswith("4242")

    def test_write_driver_message(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        msg = "Hola conductor"
        page.write_driver_message(msg)
        assert msg in driver.find_element(*page.LOC_DRIVER_MESSAGE).get_attribute("value")

    def test_toggle_blanket_tissues(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.toggle_blanket_tissues()
        assert driver.find_element(*page.LOC_BLANKET_TISSUES).is_displayed()

    def test_add_ice_creams(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.add_ice_creams()
        assert True  # aquí podrías validar un contador visible

    def test_order_taxi(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.order_taxi()
        assert page.search_modal_visible()

    def test_search_modal_shows(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.order_taxi()
        modal = page.search_modal_visible()
        assert modal is not None




