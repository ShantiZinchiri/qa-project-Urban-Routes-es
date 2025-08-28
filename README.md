**Proyecto de Pruebas Automatizadas: Urban Routes**

Este repositorio contiene una suite de pruebas automatizadas para la aplicación web "Urban Routes". El objetivo es verificar el flujo completo para pedir un taxi, desde la configuración de la ruta hasta la confirmación del conductor.

Las pruebas están desarrolladas en Python utilizando Selenium para la interacción con el navegador y Pytest como framework de ejecución.

**Justificación de la Estructura de Pruebas**:

Un Único Flujo End-to-End
Para este proyecto se optó por una estrategia de una única prueba integral (End-to-End) en lugar de múltiples pruebas unitarias pequeñas. La razón es la naturaleza secuencial del proceso que se está probando.

El acto de pedir un taxi es un flujo de usuario continuo, donde cada paso depende directamente del anterior:

No puedes seleccionar una tarifa si no has definido una ruta.

No puedes añadir un número de teléfono o método de pago hasta que has iniciado el proceso de pedido.

No puedes solicitar extras (como una manta o helados) si no has completado los pasos anteriores.

Una sola prueba que simule este viaje de principio a fin (test_full_taxi_order_flow) garantiza que el estado de la aplicación se mantiene coherentemente a lo largo de todo el proceso. Intentar separar esto en pruebas independientes fallaría, ya que cada prueba iniciaría un navegador limpio sin el contexto (la información) de los pasos previos.

Este enfoque nos permite validar la funcionalidad completa tal y como lo haría un usuario real, asegurando que la integración entre cada componente funciona correctamente.

⚙️ **Instalación y Configuración**

Para poder ejecutar las pruebas, necesitas tener Python 3 y Google Chrome instalados en tu sistema.

Clona el repositorio:

Bash

git clone <URL-de-tu-repositorio>
cd nombre-del-directorio
Crea un entorno virtual (recomendado):

Bash

python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
Instala las dependencias:
Todas las librerías necesarias se encuentran en el archivo requirements.txt.

Bash

pip install -r requirements.txt
Asegúrate de tener ChromeDriver:
La prueba necesita el WebDriver de Chrome para poder controlar el navegador. Selenium Manager usualmente se encarga de esto, pero si encuentras problemas, asegúrate de tenerlo descargado y accesible en el PATH de tu sistema.

▶ **Cómo Ejecutar las Pruebas**

Una vez configurado el entorno, puedes ejecutar la suite de pruebas con un simple comando desde la raíz del proyecto.

Bash

python3 -m pytest main.py -vv -s
pytest main.py: Le indica a Pytest que ejecute las pruebas contenidas en el archivo main.py.

-vv: Activa el modo "muy verboso" para obtener un reporte detallado de cada paso.

-s: Muestra en la consola cualquier salida, como los print(), en tiempo real.

Si todo es correcto, verás cómo se abre una ventana de Chrome que ejecuta automáticamente todos los pasos definidos en la prueba. Al final, la terminal te mostrará un resumen con == 1 passed ==.