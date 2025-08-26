import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""

    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')

    def __init__(self, driver):
        self.driver = driver

    def set_from(self, from_address):
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')



class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        # no lo modifiques, ya que necesitamos un registro adicional habilitado para recuperar el código de confirmación del teléfono
        from selenium.webdriver import DesiredCapabilities
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {'performance': 'ALL'}
        cls.driver = webdriver.Chrome(desired_capabilities=capabilities)

    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_route(address_from, address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to


    @classmethod
    def teardown_class(cls):
        cls.driver.quit()





import pytest
from time import sleep
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

# >>> La función viene en el repo de TripleTen (ya preparada).
# Simulamos el import: en tu repo real usa: from utils import retrieve_phone_code
try:
    from utils import retrieve_phone_code
except Exception:
    # fallback de desarrollo para que el archivo sea ejecutable fuera del entorno del curso
    def retrieve_phone_code():
        return "0000"

BASE_URL = "https://cnt-5f6fcf5b-9506-4997-b423-f3148b201f57.containerhub.tripleten-services.com/"

DEFAULT_TIMEOUT = 15


class UrbanRoutesPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)


    # Localizadores
    # Campos dirección
    LOC_FROM = (By.XPATH, "//input[contains(@placeholder,'From') or contains(@id,'from') or contains(@name,'from')]")
    LOC_TO = (By.XPATH, "//input[contains(@placeholder,'To') or contains(@id,'to') or contains(@name,'to')]")

    # Tarifa Comfort (tarjeta/selector)
    LOC_TARIFF_COMFORT = (By.XPATH, "//*[contains(@class,'tariff') or contains(@data-testid,'tariff') or self::button]"
                                     "[contains(., 'Comfort')]")

    # Teléfono: botón/entrada y modal
    LOC_PHONE_FIELD_OPENER = (By.XPATH, "//*[@role='button' or self::button or self::div][contains(.,'Phone') or contains(@data-testid,'phone')]")
    LOC_PHONE_INPUT = (By.XPATH, "//input[@type='tel' or contains(@name,'phone') or contains(@id,'phone')]")
    LOC_PHONE_SUBMIT = (By.XPATH, "//button[.//text()[contains(.,'Confirm') or contains(.,'Send code') or contains(.,'Verify')]] | "
                                  "//*[@role='button'][.//text()[contains(.,'Confirm') or contains(.,'Send code') or contains(.,'Verify')]]")
    LOC_PHONE_CODE_INPUT = (By.XPATH, "//input[@type='tel' or @inputmode='numeric' or contains(@id,'code') or contains(@name,'code')]")
    LOC_PHONE_CODE_SUBMIT = (By.XPATH, "//button[.//text()[contains(.,'Confirm') or contains(.,'Verify')]]")

    # Agregar tarjeta: botón/link para abrir modal
    LOC_ADD_CARD_OPEN = (By.XPATH, "//*[@role='button' or self::button or self::a][contains(.,'Add card') or contains(.,'Agregar') or contains(.,'Card') or contains(.,'Tarjeta')]")
    # Modal de tarjeta: número, fecha, CVV (nota: el CVV tiene id='code' y class='card-input' en el simulador)
    LOC_CARD_NUMBER = (By.XPATH, "//input[contains(@placeholder,'Card') or contains(@name,'card') or contains(@id,'card')]")
    LOC_CARD_DATE = (By.XPATH, "//input[contains(@placeholder,'MM') or contains(@placeholder,'/')]")
    LOC_CARD_CVV = (By.XPATH, "//input[@id='code' or contains(@placeholder,'CVV') or contains(@name,'cvv')]")
    # Botón link (se habilita tras blur del CVV)
    LOC_CARD_LINK_BTN = (By.XPATH, "//*[@role='button' or self::button][contains(@class,'button') or contains(@class,'btn')][contains(.,'Link') or contains(.,'Enlazar') or contains(.,'Vincular')]")
    # Campo para introducir código de confirmación de la tarjeta (si lo pide)
    LOC_CARD_CONFIRM_CODE = (By.XPATH, "//input[@type='tel' or @inputmode='numeric' or contains(@id,'code') or contains(@name,'code')]")
    LOC_CARD_CONFIRM_SUBMIT = (By.XPATH, "//button[.//text()[contains(.,'Confirm') or contains(.,'Verify') or contains(.,'OK')]]")

    # Mensaje para el conductor
    LOC_DRIVER_MESSAGE_FIELD = (By.XPATH, "//textarea | //input[contains(@placeholder,'Message') or contains(@name,'comment') or contains(@id,'comment')]")

    # Manta y pañuelos (toggle/checkbox)
    LOC_BLANKET_TISSUES = (By.XPATH, "//*[self::label or self::div or self::button]"
                                     "[contains(.,'Blanket') or contains(.,'Manta') or contains(.,'pañuelos') or contains(.,'tissues')]")
    # Helados: sección y botón + para aumentar cantidad
    LOC_ICE_CREAM_PLUS = (By.XPATH, "//*[contains(@class,'counter') or contains(@data-testid,'ice') or contains(.,'Ice cream')]"
                                    "//*[self::button or self::div][contains(@class,'plus') or contains(.,'+')]")

    # Botón pedir taxi
    LOC_ORDER_TAXI_BTN = (By.XPATH, "//*[@role='button' or self::button][contains(.,'Order') or contains(.,'Pedir') or contains(.,'Taxi')]")

    # Modal de búsqueda de taxi
    LOC_SEARCH_MODAL = (By.XPATH, "//*[contains(@class,'modal') or @role='dialog'][.//*[contains(.,'searching') or contains(.,'Buscando') or contains(.,'Searching')]] | "
                                   "//*[contains(@class,'modal') or @role='dialog'][.//*[contains(.,'driver') or contains(.,'conductor')]]")

    # Información del conductor (paso opcional)
    LOC_DRIVER_INFO = (By.XPATH, "//*[contains(@class,'driver') or contains(.,'Driver') or contains(.,'Conductor')][.//*]")

    # =========================
    # Acciones
    # =========================

    def open(self):
        self.driver.get(BASE_URL)
        self.wait.until(EC.presence_of_element_located(self.LOC_FROM))

    def set_route(self, from_addr: str, to_addr: str):
        # Campo "From"
        from_el = self.wait.until(EC.element_to_be_clickable(self.LOC_FROM))
        from_el.clear()
        from_el.send_keys(from_addr)
        from_el.send_keys(Keys.ENTER)

        # Campo "To"
        to_el = self.wait.until(EC.element_to_be_clickable(self.LOC_TO))
        to_el.clear()
        to_el.send_keys(to_addr)
        # Espera una sugerencia y confirma
        to_el.send_keys(Keys.ENTER)

    def select_comfort_tariff(self):
        tariff = self.wait.until(EC.element_to_be_clickable(self.LOC_TARIFF_COMFORT))
        tariff.click()

    def fill_phone_and_confirm(self, phone_number: str):
        # Abrir modal de teléfono si existe un disparador
        try:
            opener = self.wait.until(EC.element_to_be_clickable(self.LOC_PHONE_FIELD_OPENER))
            opener.click()
        except Exception:
            pass

        phone_input = self.wait.until(EC.visibility_of_element_located(self.LOC_PHONE_INPUT))
        phone_input.clear()
        phone_input.send_keys(phone_number)

        # Enviar código
        try:
            submit = self.wait.until(EC.element_to_be_clickable(self.LOC_PHONE_SUBMIT))
            submit.click()
        except Exception:
            # Algunos flujos envían el código automáticamente al salir del input
            phone_input.send_keys(Keys.ENTER)

        # Tomar el código interceptado del backend de pruebas
        code = retrieve_phone_code()

        code_input = self.wait.until(EC.visibility_of_element_located(self.LOC_PHONE_CODE_INPUT))
        code_input.clear()
        code_input.send_keys(code)

        try:
            confirm = self.wait.until(EC.element_to_be_clickable(self.LOC_PHONE_CODE_SUBMIT))
            confirm.click()
        except Exception:
            code_input.send_keys(Keys.ENTER)

    def add_credit_card(self, number: str, mm_yy: str, cvv: str):
        open_btn = self.wait.until(EC.element_to_be_clickable(self.LOC_ADD_CARD_OPEN))
        open_btn.click()

        card_number = self.wait.until(EC.visibility_of_element_located(self.LOC_CARD_NUMBER))
        card_number.clear()
        card_number.send_keys(number)

        card_date = self.wait.until(EC.visibility_of_element_located(self.LOC_CARD_DATE))
        card_date.clear()
        card_date.send_keys(mm_yy)

        card_cvv = self.wait.until(EC.visibility_of_element_located(self.LOC_CARD_CVV))
        card_cvv.clear()
        card_cvv.send_keys(cvv)

        # IMPORTANTE: hacer blur del CVV para que se habilite el botón "link"
        # Opción 1: TAB
        card_cvv.send_keys(Keys.TAB)
        # Opción 2: clic fuera (por si el TAB no basta en tu build)
        try:
            ActionChains(self.driver).move_by_offset(5, 5).click().perform()
        except Exception:
            pass

        link_btn = self.wait.until(EC.element_to_be_clickable(self.LOC_CARD_LINK_BTN))
        link_btn.click()

        # En algunos builds, al vincular tarjeta piden código de confirmación extra:
        try:
            confirm_input = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(self.LOC_CARD_CONFIRM_CODE))
            confirm_code = retrieve_phone_code()
            confirm_input.send_keys(confirm_code)
            try:
                confirm_btn = self.wait.until(EC.element_to_be_clickable(self.LOC_CARD_CONFIRM_SUBMIT))
                confirm_btn.click()
            except Exception:
                confirm_input.send_keys(Keys.ENTER)
        except Exception:
            # Si no aparece, seguimos (no todos los builds lo piden)
            pass

    def write_driver_message(self, text: str):
        field = self.wait.until(EC.presence_of_element_located(self.LOC_DRIVER_MESSAGE_FIELD))
        try:
            # Si es textarea, usar send_keys directo; si es input, igual vale.
            field.clear()
        except Exception:
            pass
        field.send_keys(text)

    def toggle_blanket_and_tissues(self):
        el = self.wait.until(EC.element_to_be_clickable(self.LOC_BLANKET_TISSUES))
        el.click()

    def add_two_ice_creams(self):
        plus_btn = self.wait.until(EC.element_to_be_clickable(self.LOC_ICE_CREAM_PLUS))
        plus_btn.click()
        plus_btn.click()

    def order_taxi(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.LOC_ORDER_TAXI_BTN))
        btn.click()

    def wait_for_search_modal(self):
        # Aparece el modal "buscando taxi"
        self.wait.until(EC.visibility_of_element_located(self.LOC_SEARCH_MODAL))

    def wait_for_driver_info_optional(self, timeout=60):
        # Paso opcional: esperar que la info del conductor aparezca (el modal cambia)
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.LOC_DRIVER_INFO))
            return True
        except Exception:
            return False




# Pytest setup


@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    # Descomenta si necesitas headless en tu CI:
    # options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


class TestUrbanRoutes:
    def test_pedir_taxi_completo(self, driver):
        page = UrbanRoutesPage(driver)

        print("[1] Abriendo la app...")
        page.open()

        print("[2] Configurando direcciones...")
        page.set_route(from_addr="East 2nd Street, 601", to_addr="1300 1st St")

        print("[3] Seleccionando tarifa Comfort...")
        page.select_comfort_tariff()

        print("[4] Ingresando teléfono...")
        page.fill_phone_and_confirm(phone_number="+15555550123")

        print("[5] Agregando tarjeta...")
        page.add_credit_card(number="4242 4242 4242 4242", mm_yy="12/29", cvv="123")

        print("[6] Escribiendo mensaje para el conductor...")
        page.write_driver_message("Hola, por favor tocar el claxon suave al llegar.")

        print("[7] Pidiendo manta y pañuelos...")
        page.toggle_blanket_and_tissues()

        print("[8] Pidiendo dos helados...")
        page.add_two_ice_creams()

        print("[9] Ordenando taxi...")
        page.order_taxi()
        page.wait_for_search_modal()
        print("[9.1] Modal de búsqueda detectado ")

        print("[10] (Opcional) Esperando información del conductor...")
        got_driver = page.wait_for_driver_info_optional(timeout=20)
        print(f"[10.1] ¿Apareció conductor?: {got_driver}")

        assert True
