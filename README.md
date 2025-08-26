# QA Project: Urban Routes

##  Descripción del Proyecto
Este proyecto contiene pruebas automatizadas de extremo a extremo para la aplicación **Urban Routes**, un simulador de pedidos de taxi.  
El objetivo es validar el flujo completo de reservar un viaje, incluyendo selección de direcciones, elección de tarifa, validación de teléfono, vinculación de tarjeta, configuración de preferencias y confirmación de pedido.

##  Tecnologías y Técnicas Utilizadas
- **Python 3.12**
- **pytest** para la ejecución y gestión de pruebas.
- **Selenium WebDriver** para la automatización del navegador.
- **WebDriverWait y Expected Conditions (EC)** para sincronización confiable.
- **XPath** como estrategia principal de localización de elementos.
- **ChromeDriver** (con opción a ejecutar en modo headless).
- Interceptación de **logs de performance** del navegador para obtener códigos de confirmación (teléfono y tarjeta).