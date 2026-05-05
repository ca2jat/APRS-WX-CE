# APRS-WX-CE 🌤️

**Estación Meteorológica APRS para Chile**

[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

> Inspirado en [Python APRS WX](https://gitlab.com/hp3icc/python-aprs-wx) de **HP3ICC** 🇵🇦  
> Desarrollado por **CA2JAT** — Valle de Elqui, Chile 🇨🇱

---

## Características

- 📡 Envía datos meteorológicos reales a la red APRS cada 30 minutos
- 🌡️ Fuente principal de datos: **Estaciones EMA del DMC** (Dirección Meteorológica de Chile)
- 🔄 Fallback automático a **OpenWeatherMap** si el DMC no está disponible
- 🚨 Alertas automáticas por: calor extremo, helada, viento fuerte y lluvia intensa
- 📋 Boletines diarios (BLN) a las 9 AM y 9 PM con pronóstico y riesgo de incendio
- 💾 Estado persistente — sobrevive reinicios del servicio
- 🔥 Datos de riesgo de incendio desde los GeoServicios del DMC

---

## Requisitos

- Python 3.x
- Raspberry Pi / Orange Pi / cualquier SBC con Linux
- Conexión a internet

```bash
sudo apt-get install python3-requests python3-pytz
```

---

## Fuentes de Datos

### DMC (Fuente Principal)
Regístrate en [climatologia.meteochile.gob.cl](https://climatologia.meteochile.gob.cl) para obtener tu token API gratuito.

Encuentra el código de tu estación EMA más cercana en:  
`https://climatologia.meteochile.gob.cl/application/requerimiento/producto/RE7003`

### OpenWeatherMap (Fallback)
Regístrate en [openweathermap.org](https://openweathermap.org) para obtener tu API key gratuita.  
Encuentra el ID de tu ciudad buscándola en el sitio web de OWM.

---

## Configuración

Edita la sección **CONFIGURACIÓN DEL USUARIO** en `wx1.py`:

```python
callsign   = "CA2JAT-13"        # Tu indicativo con SSID
latitude   = "30.01.94S"        # Formato: GG.MM.mmN/S
longitude  = "070.41.86W"       # Formato: GGG.MM.mmE/W
serverHost = "cx2sa.net"        # Servidor APRS de tu país

mc_usuario  = "tu@correo.com"   # Correo registrado en DMC
mc_token    = "TU_TOKEN"        # Token API del DMC
mc_estacion = "300046"          # Código de la EMA más cercana
mc_comuna   = "Vicuña"          # Tu comuna

owm_api_key = "TU_API_KEY_OWM"  # API key de OpenWeatherMap
owm_map_id  = "3868308"         # ID de ciudad en OWM
```

### Umbrales de Alerta
```python
ALERTA_CALOR    = 35.0   # °C
ALERTA_HELADA   = 2.0    # °C
ALERTA_VIENTO   = 40.0   # km/h
ALERTA_LLUVIA   = 5.0    # mm/h
```

---

## Instalación

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

## Formato del Paquete APRS
CA2JAT-13>APZ000,TCPIP*::@DDHHMMZ/LATLON_ddd/vvvgGGGtTTTrRRRpPPPhHHbBBBBBLLLL0 comentario
- **Paquete WX** cada 30 minutos con datos reales de la EMA
- **BLN0** — Resumen diario (temperatura actual, máxima, mínima, humedad, viento)
- **BLN1** — Pronóstico de mañana desde el DMC
- **BLN2** — Índice de riesgo de incendio desde el DMC

---

## Servidores APRS

| País | Servidor |
|------|----------|
| Chile | `cx2sa.net:14580` |
| Panamá | `panama.aprs2.net:14580` |
| Argentina | `rotate.aprs2.net:14580` |
| Global | `rotate.aprs2.net:14580` |

---

## Licencia

Licencia MIT — Libre para usar, modificar y distribuir.  
Por favor mantén los créditos originales en el encabezado del script.

---

*73 de CA2JAT 🇨🇱 — Valle de Elqui*
