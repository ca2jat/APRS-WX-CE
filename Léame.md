# APRS-WX-CE 🌤️

**Estación Meteorológica APRS para Chile**

[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

> Inspirado en [Python APRS WX](https://gitlab.com/hp3icc/python-aprs-wx) de **HP3ICC** 🇵🇦  
> Desarrollado por **CA2JAT** — Valle de Elqui, Chile 🇨🇱

> 🪟 [Guía de instalación para Windows disponible aquí](README.windows.md)  
> 🇬🇧 [English version available here](README.en.md)

---

## Características

- 📡 Envía datos meteorológicos reales a la red APRS cada 30 minutos
- 🌡️ Fuente principal de datos: **Estaciones EMA del DMC** (Dirección Meteorológica de Chile)
- 🔄 Fallback automático a **OpenWeatherMap** si el DMC no está disponible
- 🚨 Alertas automáticas por: calor extremo, helada, viento fuerte y lluvia intensa
- 📋 Boletines diarios (BLN) con horario único por indicativo para evitar congestión en la red
- 💾 Estado persistente — sobrevive reinicios del servicio
- 🔥 Nivel de riesgo de incendio: BAJO / MEDIO / ALTO / EXTREMO desde el DMC
- 🔁 Reintento automático en transmisiones fallidas

---

## Requisitos

- Python 3.x
- Raspberry Pi / Orange Pi / cualquier SBC con Linux (o Windows)
- Conexión a internet
- Indicativo de radioaficionado

```bash
sudo apt-get install python3-requests python3-pytz
```

---

## Fuentes de Datos

### DMC — Fuente Principal
Regístrate en [climatologia.meteochile.gob.cl](https://climatologia.meteochile.gob.cl) para obtener tu token API gratuito.

Encuentra el código de tu estación EMA más cercana en:  
`https://climatologia.meteochile.gob.cl/application/requerimiento/producto/RE7003`

### OpenWeatherMap — Respaldo
Regístrate en [openweathermap.org](https://openweathermap.org) para obtener tu API key gratuita.  
Encuentra el ID de tu ciudad buscándola en el sitio web de OWM.

---

## Configuración

Edita la sección `CONFIGURACIÓN DEL USUARIO` en `wx1.py`:

```python
indicativo   = "CA2JAT-13"         # Tu indicativo con SSID
latitud      = "30.01.94S"         # Formato: GG.MM.mmN/S
longitud     = "070.41.86W"        # Formato: GGG.MM.mmE/W
servidorHost = "cx2sa.net"         # Servidor APRS de tu país

mc_usuario   = "tu@correo.com"     # Correo registrado en DMC
mc_token     = "TU_TOKEN"          # Token API del DMC
mc_estacion  = "300046"            # Código de tu EMA más cercana
mc_comuna    = "Vicuña"            # Tu comuna

owm_api_key  = "TU_API_KEY_OWM"   # API key de OpenWeatherMap
owm_ciudad_id = "3868308"          # ID de tu ciudad en OWM
```

### Umbrales de Alerta
```python
ALERTA_CALOR    = 35.0   # °C
ALERTA_HELADA   = 2.0    # °C
ALERTA_VIENTO   = 40.0   # km/h
ALERTA_LLUVIA   = 5.0    # mm/h
```

### Horario de Boletines BLN
Cada estación calcula automáticamente su propio minuto de envío basado en su indicativo. Esto evita que múltiples estaciones transmitan sus boletines al mismo tiempo, reduciendo la congestión en la red APRS.

Por ejemplo:
| Indicativo | Hora BLN mañana | Hora BLN noche |
|------------|-----------------|----------------|
| CA2JAT-13  | 09:39           | 21:39          |
| CE3ABC-13  | 09:14           | 21:14          |
| XQ2EK-7    | 09:07           | 21:07          |

---

## Instalación en Linux

```bash
# Crear directorio
sudo mkdir /opt/python-wx
sudo cp wx1.py /opt/python-wx/

# Crear servicio systemd
sudo bash -c 'cat > /lib/systemd/system/aprs-wx.service << EOF
[Unit]
Description=APRS WX Station
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/python-wx/wx1.py
WorkingDirectory=/opt/python-wx/
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable aprs-wx.service
sudo systemctl start aprs-wx.service
```

### Monitorear el servicio
```bash
sudo journalctl -fu aprs-wx.service
```

---

## Instalación en Windows

Consulta la guía detallada paso a paso en [README.windows.md](README.windows.md)

---

## Formato del Paquete APRS
