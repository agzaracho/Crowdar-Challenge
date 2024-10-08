import os
import pytest
from playwright.sync_api import sync_playwright
import allure

def pytest_addoption(parser):
    parser.addoption(
        "--report", action="store", default="true", help="Genera el reporte html con Allure y lo abre al finalizar el set"
    )
    parser.addoption(
        "--browser-type", action="store", default="", help="Selecciona el navegador: chromium o firefox"
    )

# Fixture que obtiene el navegador de la línea de comandos o usa ambos por defecto
@pytest.fixture(scope="session")
def browser_types(pytestconfig):
    browser_type = pytestconfig.getoption("--browser-type")
    
    # Si no se especifica, usamos ambos navegadores
    if browser_type == "":
        return ["chromium", "firefox"]
    elif browser_type in ["chromium", "firefox"]:
        return [browser_type]
    else:
        raise ValueError(f"Navegador no soportado: {browser_type}")

# Fixture para lanzar el navegador
@pytest.fixture(params=["chromium", "firefox"])
def browser_type_launch(request, browser_types):
    # Solo ejecuta el navegador si está en la lista de los navegadores permitidos
    if request.param not in browser_types:
        pytest.skip(f"El navegador {request.param} no fue seleccionado.")
    
    with sync_playwright() as p:
        browser_type = request.param

        # Agregar el navegador como una etiqueta dinámica en Allure
        allure.dynamic.label("browser", browser_type)

        # Lanzar el navegador con slow_mo para todos los navegadores
        browser = p[browser_type].launch(slow_mo=500)
        yield browser
        browser.close()

@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    report_option = session.config.getoption("--report")
    pwdebug = os.getenv('PWDEBUG')

    # No generar el reporte si PWDEBUG está activado o si --report=false
    if report_option == "true" and pwdebug != "1":
        # Generar el reporte de Allure al finalizar las pruebas
        os.system('allure generate --clean ./allure-results -o ./allure-report')
        
        # Abrir el reporte de Allure en español
        os.system('allure serve allure-results --lang es')

