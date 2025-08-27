@pytest.fixture(scope="function")
def driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--window-size=1280,900")
    # descomenta si quieres sin ventana:
    # opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # carga "eager": no espera todos los recursos
    opts.page_load_strategy = "eager"

    # necesario para retrieve_phone_code(driver)
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    drv = webdriver.Chrome(options=opts)
    drv.set_script_timeout(30)
    drv.set_page_load_timeout(30)
    yield drv
    drv.quit()



