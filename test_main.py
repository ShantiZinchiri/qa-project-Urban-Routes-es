import data
from selenium import webdriver
from urban_routes import UrbanRoutesPage
import pytest

class TestUrbanRoutes:
    driver = None

    @classmethod
    def setup_class(cls):
        """Configura el controlador de Chrome una vez para toda la clase de prueba."""
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        chrome_options = ChromeOptions()
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(5) # Espera implícita para mayor estabilidad

    def test_full_taxi_order_flow(self):
        """
        Prueba completa que cubre todo el flujo de pedir un taxi,
        desde establecer la ruta hasta esperar la confirmación del conductor.
        """
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)

        # Paso 1: Configurar la dirección
        routes_page.set_route(data.address_from, data.address_to)
        assert routes_page.get_from() == data.address_from, "La dirección 'Desde' no se configuró correctamente."
        assert routes_page.get_to() == data.address_to, "La dirección 'Hasta' no se configuró correctamente."

        # Paso 2: Pedir un taxi y seleccionar la tarifa Comfort
        routes_page.request_comfort_cab()
        assert routes_page.get_selected_tariff() == "Comfort", "La tarifa 'Comfort' no fue seleccionada."

        # Paso 3: Rellenar el número de teléfono
        routes_page.set_phone_number(data.phone_number)
        assert routes_page.get_phone_in_field() == data.phone_number, "El número de teléfono no se guardó correctamente."

        # Paso 4: Agregar una tarjeta de crédito
        routes_page.set_credit_card_number(data.card_number, data.card_code)
        assert routes_page.get_card_optn() is not None, "La tarjeta de crédito no se agregó correctamente."

        # Pasos 5, 6 y 7: Rellenar opciones extra (mensaje, manta, helados)
        routes_page.fill_extra_options(data.message_for_driver)
        assert routes_page.get_comment_for_driver_in_field() == data.message_for_driver, "El mensaje para el conductor no se guardó."
        assert routes_page.is_blanket_and_handkerchief_checkbox_selected() is True, "La opción de manta y pañuelos no se seleccionó."
        assert routes_page.get_current_icecream_count_value() == "2", "No se pidieron 2 helados."

        # Paso 8: Pedir el taxi y verificar que aparece el modal de búsqueda
        routes_page.book_trip()
        assert "Buscar automóvil" in routes_page.get_order_screen_title(), "El modal de búsqueda de automóvil no apareció."

        # Paso 9 (Opcional): Esperar la información del conductor
        routes_page.wait_confirmation()
        assert "El conductor llegará en" in routes_page.get_order_screen_title(), "No se mostró la información de llegada del conductor."

    @classmethod
    def teardown_class(cls):
        """Cierra el controlador después de que todas las pruebas hayan terminado."""
        cls.driver.quit()
