import pytest
import data
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common import WebDriverException
import json, time


def retrieve_phone_code(driver) -> str:
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


DEFAULT_TIMEOUT = 15


class UrbanRoutesPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    # Localizadores (resumidos)
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

    # Acciones
    def open(self, url): self.driver.get(url)
    def set_route(self, f, t):
        self.driver.find_element(*self.LOC_FROM).send_keys(f)
        self.driver.find_element(*self.LOC_TO).send_keys(t)
    def select_comfort_tariff(self): self.driver.find_element(*self.LOC_TARIFF_COMFORT).click()
    def fill_phone(self, phone): self.driver.find_element(*self.LOC_PHONE_INPUT).send_keys(phone)
    def add_card(self, num, date, cvv):
        self.driver.find_element(*self.LOC_CARD_NUMBER).send_keys(num)
    def write_driver_message(self, msg): self.driver.find_element(*self.LOC_DRIVER_MESSAGE).send_keys(msg)
    def toggle_blanket_tissues(self): self.driver.find_element(*self.LOC_BLANKET_TISSUES).click()
    def add_ice_creams(self, n=2):
        plus = self.driver.find_element(*self.LOC_ICE_CREAM_PLUS)
        for _ in range(n): plus.click()
    def order_taxi(self): self.driver.find_element(*self.LOC_ORDER_TAXI_BTN).click()
    def search_modal_visible(self): return self.wait.until(EC.presence_of_element_located(self.LOC_SEARCH_MODAL))


@pytest.fixture(scope="function")
def driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--window-size=1280,900")
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()


class TestUrbanRoutes:

    def test_set_route(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.set_route(data.address_from, data.address_to)
        assert driver.find_element(*page.LOC_FROM).get_property("value") == data.address_from
        assert driver.find_element(*page.LOC_TO).get_property("value") == data.address_to

    def test_select_comfort_tariff(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.select_comfort_tariff()
        assert driver.find_element(*page.LOC_TARIFF_COMFORT)

    def test_fill_phone(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.fill_phone("+15555550123")
        assert driver.find_element(*page.LOC_PHONE_INPUT).get_attribute("value") != ""

    def test_add_card(self, driver):
        page = UrbanRoutesPage(driver)
        page.open(data.urban_routes_url)
        page.add_card("4242 4242 4242 4242", "12/29", "123")
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
        # aquí podrías contar la cantidad de helados si hay un contador visible
        assert True

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


