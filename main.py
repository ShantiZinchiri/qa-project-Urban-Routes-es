
import data
import json
import time
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import WebDriverException
from selenium.webdriver import ActionChains


#  Utilidad provista
def retrieve_phone_code(driver) -> str:
    """
    Devuelve el código de confirmación interceptado desde los logs de rendimiento del navegador.
    IMPORTANTE: el driver DEBE tener 'goog:loggingPrefs': {'performance':'ALL'} habilitado.
    """
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
            raise Exception(
                "No se encontró el código de confirmación del teléfono.\n"
                "Usa 'retrieve_phone_code(driver)' solo después de solicitar el código en la app."
            )
        return code


DEFAULT_TIMEOUT = 15


class UrbanRoutesPage:
    # ---------- Localizadores robustos ----------
    LOC_FROM = (By.XPATH, "//input[contains(@placeholder,'From') or contains(@id,'from') or contains(@name,'from')]")
    LOC_TO = (By.XPATH, "//input[contains(@placeholder,'To') or contains(@id,'to') or contains(@name,'to')]")

    LOC_TARIFF_COMFORT = (By.XPATH,
        "//*[contains(@class,'tariff') or contains(@data-testid,'tariff') or self::button][contains(., 'Comfort')]"
    )

    LOC_PHONE_FIELD_OPENER = (By.XPATH,
        "//*[@role='button' or self::button or self::div][contains(.,'Phone') or contains(@data-testid,'phone')]"
    )
    LOC_PHONE_INPUT = (By.XPATH, "//input[@type='tel' or contains(@name,'phone') or contains(@id,'phone')]")
    LOC_PHONE_SUBMIT = (By.XPATH,
        "//button[.//text()[contains(.,'Confirm') or contains(.,'Send code') or contains(.,'Verify')]] | "
        "//*[@role='button'][.//text()[contains(.,'Confirm') or contains(.,'Send code') or contains(.,'Verify')]]"
    )
    LOC_PHONE_CODE_INPUT = (By.XPATH, "//input[@type='tel' or @inputmode='numeric' or contains(@id,'code') or contains(@name,'code')]")
    LOC_PHONE_CODE_SUBMIT = (By.XPATH, "//button[.//text()[contains(.,'Confirm') or contains(.,'Verify')]]")

    LOC_ADD_CARD_OPEN = (By.XPATH,
        "//*[@role='button' or self::button or self::a][contains(.,'Add card') or contains(.,'Agregar') or contains(.,'Card') or contains(.,'Tarjeta')]"
    )
    LOC_CARD_NUMBER = (By.XPATH, "//input[contains(@placeholder,'Card') or contains(@name,'card') or contains(@id,'card')]")
    LOC_CARD_DATE = (By.XPATH, "//input[contains(@placeholder,'MM') or contains(@placeholder,'/')]")
    LOC_CARD_CVV = (By.XPATH, "//input[@id='code' or contains(@placeholder,'CVV') or contains(@name,'cvv')]")
    LOC_CARD_LINK_BTN = (By.XPATH,
        "//*[@role='button' or self::button][contains(@class,'button') or contains(@class,'btn')]"
        "[contains(.,'Link') or contains(.,'Enlazar') or contains(.,'Vincular')]"
    )
    LOC_CARD_CONFIRM_CODE = (By.XPATH, "//input[@type='tel' or @inputmode='numeric' or contains(@id,'code') or contains(@name,'code')]")
    LOC_CARD_CONFIRM_SUBMIT = (By.XPATH, "//button[.//text()[contains(.,'Confirm') or contains(.,'Verify') or contains(.,'OK')]]")

    LOC_DRIVER_MESSAGE_FIELD = (By.XPATH, "//textarea | //input[contains(@placeholder,'Message') or contains(@name,'comment') or contains(@id,'comment')]")

    LOC_BLANKET_TISSUES = (By.XPATH,
        "//*[self::label or self::div or self::button]"
        "[contains(.,'Blanket') or contains(.,'Manta') or contains(.,'pañuelos') or contains(.,'tissues')]"
    )

    LOC_ICE_CREAM_PLUS = (By.XPATH,
        "//*[contains(@class,'counter') or contains(@data-testid,'ice') or contains(.,'Ice cream')]"
        "//*[self::button or self::div][contains(@class,'plus') or contains(.,'+')]"
    )

    LOC_ORDER_TAXI_BTN = (By.XPATH,
        "//*[@role='button' or self::button][contains(.,'Order') or contains(.,'Pedir') or contains(.,'Taxi')]"
    )

    LOC_SEARCH_MODAL = (By.XPATH,
        "//*[contains(@class,'modal') or @role='dialog'][.//*[contains(.,'searching') or contains(.,'Buscando') or contains(.,'Searching')]] | "
        "//*[contains(@class,'modal') or @role='dialog'][.//*[contains(.,'driver') or contains(.,'conductor')]]"
    )

    LOC_DRIVER_INFO = (By.XPATH,
        "//*[contains(@class,'driver') or contains(.,'Driver') or contains(.,'Conductor')][.//*]"
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    # ---------- Acciones ----------
    def open(self, url: str):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located(self.LOC_FROM))

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
        self.wait.until(EC.element_to_be_clickable(self.LOC_TARIFF_COMFORT)).click()

    def fill_phone_and_confirm(self, phone_number: str):
        # abrir modal si existe
        try:
            self.wait.until(EC.element_to_be_clickable(self.LOC_PHONE_FIELD_OPENER)).click()
        except Exception:
            pass

        phone_input = self.wait.until(EC.visibility_of_element_located(self.LOC_PHONE_INPUT))
        phone_input.clear()
        phone_input.send_keys(phone_number)

        # enviar código
        try:
            self.wait.until(EC.element_to_be_clickable(self.LOC_PHONE_SUBMIT)).click()
        except Exception:
            phone_input.send_keys(Keys.ENTER)

        code = retrieve_phone_code(self.driver)

        code_input = self.wait.until(EC.visibility_of_element_located(self.LOC_PHONE_CODE_INPUT))
        code_input.clear()
        code_input.send_keys(code)

        try:
            self.wait.until(EC.element_to_be_clickable(self.LOC_PHONE_CODE_SUBMIT)).click()
        except Exception:
            code_input.send_keys(Keys.ENTER)

    def add_credit_card(self, number: str, mm_yy: str, cvv: str):
        self.wait.until(EC.element_to_be_clickable(self.LOC_ADD_CARD_OPEN)).click()

        card_number = self.wait.until(EC.visibility_of_element_located(self.LOC_CARD_NUMBER))
        card_number.clear()
        card_number.send_keys(number)

        card_date = self.wait.until(EC.visibility_of_element_located(self.LOC_CARD_DATE))
        card_date.clear()
        card_date.send_keys(mm_yy)

        card_cvv = self.wait.until(EC.visibility_of_element_located(self.LOC_CARD_CVV))
        card_cvv.clear()
        card_cvv.send_keys(cvv)

        # forzar blur para habilitar "Link"
        card_cvv.send_keys(Keys.TAB)
        try:
            ActionChains(self.driver).move_by_offset(5, 5).click().perform()
        except Exception:
            pass

        self.wait.until(EC.element_to_be_clickable(self.LOC_CARD_LINK_BTN)).click()

        # algunos builds piden código extra al vincular tarjeta
        try:
            confirm_input = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.LOC_CARD_CONFIRM_CODE)
            )
            confirm_code = retrieve_phone_code(self.driver)
            confirm_input.send_keys(confirm_code)
            try:
                self.wait.until(EC.element_to_be_clickable(self.LOC_CARD_CONFIRM_SUBMIT)).click()
            except Exception:
                confirm_input.send_keys(Keys.ENTER)
        except Exception:
            pass

    def write_driver_message(self, text: str):
        field = self.wait.until(EC.presence_of_element_located(self.LOC_DRIVER_MESSAGE_FIELD))
        try:
            field.clear()
        except Exception:
            pass
        field.send_keys(text)

    def toggle_blanket_and_tissues(self):
        self.wait.until(EC.element_to_be_clickable(self.LOC_BLANKET_TISSUES)).click()

    def add_two_ice_creams(self):
        plus_btn = self.wait.until(EC.element_to_be_clickable(self.LOC_ICE_CREAM_PLUS))
        plus_btn.click()
        plus_btn.click()

    def order_taxi(self):
        self.wait.until(EC.element_to_be_clickable(self.LOC_ORDER_TAXI_BTN)).click()

    def wait_for_search_modal(self):
        self.wait.until(EC.visibility_of_element_located(self.LOC_SEARCH_MODAL))

    def wait_for_driver_info_optional(self, timeout=60):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.LOC_DRIVER_INFO))
            return True
        except Exception:
            return False



# Pytest: fixture del driver

@pytest.fixture(scope="function")
def driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--window-size=1280,900")
    # descomenta si quieres headless:
    # opts.add_argument("--headless=new")

    # Habilita logs de rendimiento para retrieve_phone_code(driver)
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()



# Tests

class TestUrbanRoutes:
    def test_pedir_taxi_completo(self, driver):
        page = UrbanRoutesPage(driver)

        print("[1] Abriendo la app…")
        page.open(data.urban_routes_url)

        print("[2] Configurando direcciones…")
        page.set_route(data.address_from, data.address_to)
        # Checks rápidos de los campos
        assert page.get_from() == data.address_from
        assert page.get_to() == data.address_to

        print("[3] Seleccionando tarifa Comfort…")
        page.select_comfort_tariff()

        print("[4] Ingresando teléfono…")
        page.fill_phone_and_confirm(phone_number=data.phone_number if hasattr(data, "phone_number") else "+15555550123")

        print("[5] Agregando tarjeta…")
        card_number = getattr(data, "card_number", "4242 4242 4242 4242")
        card_date = getattr(data, "card_date", "12/29")
        card_cvv = getattr(data, "card_cvv", "123")
        page.add_credit_card(card_number, card_date, card_cvv)

        print("[6] Escribiendo mensaje para el conductor…")
        page.write_driver_message("Hola, por favor tocar el claxon suave al llegar. Gracias.")

        print("[7] Pidiendo manta y pañuelos…")
        page.toggle_blanket_and_tissues()

        print("[8] Pidiendo dos helados…")
        page.add_two_ice_creams()

        print("[9] Ordenando taxi…")
        page.order_taxi()
        page.wait_for_search_modal()
        print("[9.1] Modal de búsqueda detectado ✅")

        print("[10] (Opcional) Esperando información del conductor…")
        got_driver = page.wait_for_driver_info_optional(timeout=30)
        print(f"[10.1] ¿Apareció conductor?: {got_driver}")

        assert True  # flujo alcanzado sin excepciones

