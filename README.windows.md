# APRS-WX-CE en Windows 🪟

Guía de instalación paso a paso para usuarios Windows.
No se requiere experiencia previa con Python ni con la línea de comandos.

---

## Requisitos

- Windows 7 / 8 / 10 / 11
- Conexión a internet
- Indicativo de radioaficionado
- Cuenta gratuita en [climatologia.meteochile.gob.cl](https://climatologia.meteochile.gob.cl) (datos del DMC)
- Cuenta gratuita en [openweathermap.org](https://openweathermap.org) (respaldo si el DMC falla)

---

## Paso 1 — Instalar Python

1. Abra el navegador y vaya a: https://www.python.org/downloads/
2. Haga click en el botón amarillo **Download Python 3.x.x** y abra el archivo descargado.
3. **MUY IMPORTANTE:** antes de presionar *Install Now*, marque la casilla **"Add Python to PATH"** que está en la parte inferior de la ventana.
4. Presione **Install Now**, espere a que termine y presione **Close**.

Para verificar la instalación:

1. Presione las teclas **Windows + R**, escriba `cmd` y presione Enter.
2. En la ventana negra escriba lo siguiente y presione Enter:

```
python --version
```

Debe responder algo como `Python 3.12.0`.

---

## Paso 2 — Descargar APRS-WX-CE

1. Vaya a: https://github.com/ca2jat/APRS-WX-CE
2. Haga click en el botón verde **Code** y luego en **Download ZIP**.
3. Guarde el archivo en el escritorio, haga click derecho sobre él y elija **Extraer todo → Extraer**.
4. Se creará la carpeta **APRS-WX-CE-main** en el escritorio.

---

## Paso 3 — Obtener el token del DMC

1. Vaya a https://climatologia.meteochile.gob.cl y cree una cuenta con su correo.
2. Ingrese a su cuenta y anote su **Token API** (una cadena de letras y números).
3. Para encontrar la estación EMA más cercana, busque su ubicación en el visor de estaciones del DMC y anote el código de 6 dígitos (ejemplo: `300046` corresponde a Vicuña).

---

## Paso 4 — Obtener la API key de OpenWeatherMap

Se usa solo como respaldo cuando el DMC no está disponible.

1. Vaya a https://openweathermap.org y presione **Sign Up**.
2. Una vez registrado, abra su perfil → **My API Keys** y anote la clave.
3. Busque su ciudad en el sitio. El número al final de la URL es el ID de su ciudad (ejemplo: `3871336` es Santiago).

---

## Paso 5 — Configurar el script

1. Abra la carpeta **APRS-WX-CE-main**.
2. Click derecho sobre **wx_chile.py** → **Abrir con** → **Bloc de notas**.
3. Busque la sección **CONFIGURACIÓN DEL USUARIO** y cambie solo los valores entre comillas:

```python
callsign   = "CE1XXX-13"       # Su indicativo con SSID
latitude   = "33.27.00S"       # Formato GG.MM.mmN/S
longitude  = "070.40.00W"      # Formato GGG.MM.mmE/W
serverHost = "cx2sa.net"       # Servidor APRS

mc_usuario  = "su@correo.com"  # Correo registrado en el DMC
mc_token    = "SU_TOKEN"       # Token del DMC
mc_estacion = "300046"         # Código de su EMA más cercana
mc_comuna   = "Su Comuna"      # Su comuna

owm_api_key = "SU_API_KEY"     # API key de OpenWeatherMap
owm_map_id  = "3871336"        # ID de su ciudad en OWM
```

4. **Cambie también la ruta del archivo de estado para Windows.** Busque esta línea:

```python
ESTADO_FILE = "/opt/python-wx/estado_dia.json"
```

y reemplácela por:

```python
ESTADO_FILE = "C:/python-wx/estado_dia.json"
```

5. Guarde con **Ctrl+S** y cierre el Bloc de notas.

> Nota: evite tildes y la letra ñ en los textos que se transmiten por APRS
> (por ejemplo, escriba "Vicuna" en lugar de "Vicuña"). Algunas estaciones
> las muestran como caracteres extraños.

### ¿Cómo escribo mi latitud y longitud?

El formato es grados, minutos enteros y centésimas de minuto, separados por puntos.
Ejemplo para Santiago (-33.45°, -70.66°):

```
latitude  = "33.27.00S"
longitude = "070.39.60W"
```

Puede obtener sus coordenadas exactas en Google Maps con click derecho sobre su ubicación.

---

## Paso 6 — Instalar

1. En la carpeta **APRS-WX-CE-main** haga doble click en **instalar.bat**.
2. Si Windows muestra una advertencia de seguridad, presione **Más información → Ejecutar de todas formas**.
3. Verá el avance en una ventana negra. Debe terminar con "Instalacion completada".
4. Presione cualquier tecla para cerrar.

El instalador crea la carpeta `C:\python-wx`, copia los archivos, instala las dependencias (`requests` y `pytz`) y agrega el inicio automático con Windows.

---

## Paso 7 — Iniciar APRS-WX-CE

1. Abra la carpeta `C:\python-wx` y haga doble click en **iniciar.bat**.
2. Se abrirá una ventana negra con los mensajes del programa:

```
APRS-WX-CE v1.3 iniciando... (CE1XXX-13)
BLN programados: 09:14 y 21:14
[OK] Paquete 1/1: CE1XXX-13>APZ000,TCPIP*:@...
[DMC] T:22.5C Max:22.5C Min:10.2C | Alertas:0 BLN:0
```

**No cierre esa ventana.** Si la cierra, el programa se detiene. Puede minimizarla.

---

## Inicio automático con Windows

El instalador deja una copia de `iniciar.bat` en la carpeta de inicio de Windows, de modo que APRS-WX-CE arranca solo al encender el computador.

- Para verificarlo: presione **Windows + R**, escriba `shell:startup` y presione Enter. Debe aparecer el archivo **APRS-WX-CE.bat**.
- Para desactivar el inicio automático, elimine ese archivo.

---

## ¿A qué hora salen mis boletines BLN?

Cada estación calcula un minuto de envío propio a partir de su indicativo, para que no todas transmitan a las 09:00 y 21:00 en punto y se congestione la red. El horario es siempre el mismo para su indicativo.

Para conocerlo, abra `cmd` y ejecute este comando (cambie `CE1XXX13` por su indicativo sin el guión):

```
python -c "cs='CE1XXX13'; o=sum(ord(c)*(i+1) for i,c in enumerate(cs))%56; print('BLN manana: 09:%02d' % o); print('BLN noche:  21:%02d' % o)"
```

También lo muestra el programa al iniciar, en la línea "BLN programados".

---

## Qué transmite el programa

| Paquete | Contenido |
|---------|-----------|
| WX (cada 30 min) | Temperatura, humedad, presión, viento, lluvia y radiación solar de la EMA del DMC |
| BLN0 | Resumen del día: temperatura actual, máxima, mínima, humedad y viento máximo |
| BLN1 | Pronóstico de mañana: temperatura máxima, humedad mínima y viento máximo |
| BLN2 | Alerta de incendio: nivel BAJO, MEDIO, ALTO o EXTREMO |
| Alertas WX | Solo si se superan los umbrales: calor, helada, viento fuerte o lluvia intensa |

Umbrales de alerta por defecto (modificables en `wx_chile.py`):

| Alerta | Umbral |
|--------|--------|
| Calor extremo | `ALERTA_CALOR = 35.0` °C |
| Riesgo de helada | `ALERTA_HELADA = 2.0` °C |
| Viento fuerte | `ALERTA_VIENTO = 40.0` km/h |
| Lluvia intensa | `ALERTA_LLUVIA = 5.0` mm/h |

---

## Solución de problemas

**"Python no esta instalado"**
Vuelva al Paso 1. Si instaló Python sin marcar "Add Python to PATH", desinstálelo y vuelva a instalarlo marcando esa casilla.

**"Error instalando dependencias"**
Abra `cmd` como administrador y ejecute: `python -m pip install requests pytz`

**La ventana se abre y se cierra de inmediato**
Hay un error en la configuración. Abra `cmd` y ejecute:
```
cd C:\python-wx
python wx_chile.py
```
El error aparecerá en pantalla.

**Aparece "DMC fallo"**
El programa está usando OpenWeatherMap como respaldo. Revise el correo, el token y el código de estación del DMC.

**No aparece nada en aprs.fi**
Revise el indicativo y el formato de las coordenadas. Espere hasta 30 minutos para la primera transmisión.

**Los BLN no salen a la hora esperada**
Verifique que el reloj y la zona horaria del computador estén correctos (hora de Chile).

---

## Más información

- Proyecto: https://github.com/ca2jat/APRS-WX-CE
- Consultas: abra un issue en GitHub o escriba por APRS a CA2JAT-13

---

*73 de CA2JAT 🇨🇱 — Valle de Elqui*
