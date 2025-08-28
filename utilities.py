from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

# Selectores relacionados con la navegación y la configuración inicial del taxi
from_field = (By.ID, 'from')
to_field = (By.ID, 'to')
request_cab_btn = (
    By.XPATH, "//div[@class='results-text']//button[@type='button']")
comfort_optn = (By.XPATH, "//*[contains(text(),'Comfort')]")
selected_tariff = (
    By.XPATH, "//div[@class='tariff-picker shown']//div[@class='tariff-cards']//div[@class='tcard active']//div[@class='tcard-title']")

# Selectores relacionados con el número de teléfono y el código de confirmación por SMS
phone_btn = (By.CLASS_NAME, "np-button")
phone_field = (By.CLASS_NAME, "np-text")
add_phone_dialog = (By.ID, "phone")
confirm_phone = (
    By.XPATH, "//div[@class='section active']//form//div[@class='buttons']//button[@type='submit']")
confirmation_code_area = (By.ID, "code")
confirm_code = (
    By.XPATH, "//div[@class='section active']//form//div[@class='buttons']//button[@type='submit']")

# Selectores relacionados con el número de tarjeta de crédito y el código
payment_btn = (By.CLASS_NAME, "pp-button")
credit_card_optn = (By.CLASS_NAME, "pp-plus")
credit_card_number_field = (By.ID, "number")
credit_card_code_field = (
    By.XPATH, "//div[@class='card-code-input']//input[@id='code']")
confirm_credit_card = (
    By.XPATH, "//div[@class='pp-buttons']//button[@type='submit']")
close_payment_modal_btn = (
    By.XPATH, "//div[@class='payment-picker open']//div[@class='modal']//div[@class='section active']//button[@class='close-button section-close']")
card_element_verify_if_exists = (
    By.XPATH, "//div[@class='pp-button filled']//img[@alt='card']")

# Selectores relacionados con opciones adicionales en el formulario de requisitos
requirements_form_open = (
    By.XPATH, "//div[@class='form']//div[@class='reqs open']")
comment_to_driver_field = (By.ID, "comment")
blanket_and_handkerchief_slider = (
    By.XPATH, "//div[@class='r-sw-container']/*[contains(text(),'Manta')]/..//div[@class='switch']")
icecream_counter_plus = (
    By.XPATH, "//div[contains(text(),'Helado')]/..//div[@class='counter-plus']")
icecream_counter_value = (
    By.XPATH, "//div[contains(text(),'Helado')]/..//div[@class='counter-value']")
blanket_and_handkerchief_checkbox = (
    By.XPATH, "//div[@class='r-sw-container']/*[contains(text(),'Manta')]/..//div[@class='switch']//input[@class='switch-input']")

# Selectores relacionados con la pantalla de búsqueda y confirmación
order_wait_screen = (
    By.XPATH, "//div[@class='order shown']")
order_wait_screen_title = (
    By.XPATH, "//div[@class='order shown']//div[@class='order-body']//div[@class='order-header']//div[@class='order-header-title']")
trip_confirmation = (
    By.XPATH, "//div[@class='order shown']//div[@class='order-body']//div[@class='order-header']//div[@class='order-number']")
book_cab_btn = (By.CLASS_NAME, 'smart-button-main')


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


# Espera explícita de Selenium para que los campos estén presentes, sean clicables o visibles
def wait_for_presence_input_field(driver, selector, wait_time=3):
  WebDriverWait(driver, wait_time).until(
      expected_conditions.presence_of_element_located(selector))


def wait_for_clickable_element(driver, selector, wait_time=3):
  WebDriverWait(driver, wait_time).until(
      expected_conditions.element_to_be_clickable(selector))


def wait_for_visible_element(driver, selector, wait_time=3):
  WebDriverWait(driver, wait_time).until(
      expected_conditions.visibility_of_element_located(selector))