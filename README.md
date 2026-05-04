# APRS-WX-CE 🌤️

**APRS Weather Station for Chile**  
*Estación Meteorológica APRS para Chile*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

> Inspired by [Python APRS WX](https://gitlab.com/hp3icc/python-aprs-wx) by **HP3ICC** 🇵🇦  
> Developed by **CA2JAT** — Valle de Elqui, Chile 🇨🇱

---

## Features / Características

- 📡 Sends real WX data to APRS network every 30 minutes
- 🌡️ Primary data source: **DMC EMA stations** (Dirección Meteorológica de Chile)
- 🔄 Automatic fallback to **OpenWeatherMap** if DMC is unavailable
- 🚨 Automatic alerts for: heat, frost, strong wind, heavy rain
- 📋 Daily bulletins (BLN) at 9 AM and 9 PM with forecast and fire risk
- 💾 Persistent state — survives service restarts
- 🔥 Fire risk data from DMC GeoServices

---

## Requirements / Requisitos

- Python 3.x
- Raspberry Pi / Orange Pi / any Linux SBC
- Internet connection

```bash
sudo apt-get install python3-requests python3-pytz
```

---

## Data Sources / Fuentes de Datos

### DMC (Primary)
Register at [climatologia.meteochile.gob.cl](https://climatologia.meteochile.gob.cl) to get your free API token.

Find your nearest EMA station code at:  
`https://climatologia.meteochile.gob.cl/application/requerimiento/producto/RE7003`

### OpenWeatherMap (Fallback)
Register at [openweathermap.org](https://openweathermap.org) for a free API key.  
Find your city ID by searching your city on the OWM website.

---

## Configuration / Configuración

Edit the `USER CONFIGURATION` section in `wx1.py`:

```python
callsign   = "CA2JAT-13"        # Your callsign with SSID
latitude   = "00.01.94S"        # Format: DD.MM.mmN/S
longitude  = "000.41.86W"       # Format: DDD.MM.mmE/W
serverHost = "cx2sa.net"        # APRS server

mc_usuario  = "your@email.com"  # DMC registered email
mc_token    = "YOUR_TOKEN"      # DMC API token
mc_estacion = "300046"          # Nearest EMA station code
mc_comuna   = "Vicuña"          # Your commune

owm_api_key = "YOUR_OWM_KEY"    # OWM API key
owm_map_id  = "3868308"         # OWM city ID
```

### Alert thresholds
```python
ALERTA_CALOR    = 35.0   # °C
ALERTA_HELADA   = 2.0    # °C
ALERTA_VIENTO   = 40.0   # km/h
ALERTA_LLUVIA   = 5.0    # mm/h
```

---

## Installation / Instalación

```bash
# Create directory
sudo mkdir /opt/python-wx
sudo cp wx1.py /opt/python-wx/

# Create systemd service
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

### Monitor logs
```bash
sudo journalctl -fu aprs-wx.service
```

---

## APRS Packet Format
CA2JAT-13>APZ000,TCPIP*::@031335zDDMM.mmS/DDDMM.mmW_ddd/sssgtttrRRRpPPPhHHbBBBBBLLLL0 comment
- **WX packet** every 30 minutes
- **BLN0** — Daily summary (temp, max, min, humidity, wind)
- **BLN1** — Tomorrow's forecast from DMC
- **BLN2** — Fire risk index from DMC

---

## APRS Servers / Servidores APRS

| Country | Server |
|---------|--------|
| Chile | `cx2sa.net:14580` |
| Panama | `panama.aprs2.net:14580` |
| Global | `rotate.aprs2.net:14580` |

---

## License

MIT License — Free to use, modify and distribute.  
Please keep the original credits in the script header.

---

*73 de CA2JAT 🇨🇱 — Valle de Elqui*
