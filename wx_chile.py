import socket
import time
import requests
import json
from datetime import datetime
import pytz

################################################
# APRS-WX-CE
# APRS Weather Station for Chile
# Author: CA2JAT - Valle de Elqui, Chile
# Inspired by: Python APRS WX by HP3ICC
# GitHub: https://github.com/ca2jat/APRS-WX-CE
# v1.3 - 2026
#
# Data sources:
#   Primary:  EMA DMC (Direccion Meteorologica de Chile)
#   Fallback: OpenWeatherMap
#
# Features:
#   - Real WX data from nearest DMC EMA station
#   - Automatic alerts: heat, frost, wind, rain
#   - Daily BLN bulletins with callsign-based time offset
#   - Fire risk level: BAJO/MEDIO/ALTO/EXTREMO
#   - Persistent state (survives restarts)
#   - Automatic retry on failed transmissions
################################################

# === USER CONFIGURATION ===

callsign   = "CA2JAT-13"            # Your callsign with SSID
latitude   = "30.01.94S"            # Format: DD.MM.mmN/S
longitude  = "070.41.86W"           # Format: DDD.MM.mmE/W

serverHost = "cx2sa.net"            # APRS server (Chile: cx2sa.net)
serverPort = 14580
every      = 30                     # Minutes between WX transmissions

TZ_LOCAL   = pytz.timezone("America/Santiago")  # Your timezone

# MeteoChile API (register at climatologia.meteochile.gob.cl)
mc_usuario  = "your@email.com"      # Your registered email
mc_token    = "YOUR_TOKEN"          # Your API token
mc_estacion = "300046"              # Nearest EMA station code
mc_comuna   = "Vicuña"              # Your commune name

# OpenWeatherMap fallback (register at openweathermap.org)
owm_api_key = "YOUR_OWM_API_KEY"    # Your OWM API key
owm_map_id  = "3868308"             # Your city ID
owm_lang    = "es"                  # Language: es, en, etc.

# WX Alert thresholds
ALERTA_CALOR    = 35.0              # °C heat alert
ALERTA_HELADA   = 2.0               # °C frost alert
ALERTA_VIENTO   = 40.0              # km/h wind alert
ALERTA_LLUVIA   = 5.0               # mm/h rain alert

# BLN bulletin schedule (local time hours)
# Each station gets a unique minute offset calculated from its callsign
# This prevents all stations from transmitting at the same time
BLN_HORAS = [9, 21]                 # Base hours: 9 AM and 9 PM

# Persistent state file
ESTADO_FILE = "/opt/python-wx/estado_dia.json"  # Linux
# ESTADO_FILE = "C:/python-wx/estado_dia.json"  # Windows

# === END USER CONFIGURATION ===

def calculate_aprs_passcode(callsign):
    cs = callsign.upper().split('-')[0]
    h  = 0x73e2
    for i, c in enumerate(cs):
        h ^= ord(c) << (8 if i % 2 == 0 else 0)
    return h & 0x7fff

def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

def knots_to_mph(kt):
    return kt * 1.15078

def knots_to_kmh(kt):
    return kt * 1.852

def calcular_offset_bln(callsign):
    """
    Calculates a unique minute offset (0-55) based on the callsign.
    This ensures each station transmits BLN at a different time,
    avoiding congestion when multiple stations are active.
    Example: CA2JAT-13 -> offset 39 -> BLN at 09:39 and 21:39
    """
    cs    = callsign.upper().replace("-", "")
    total = sum(ord(c) * (i + 1) for i, c in enumerate(cs))
    return total % 56

def cargar_estado():
    try:
        with open(ESTADO_FILE, "r") as f:
            d = json.load(f)
            d["bln_enviado"]     = set(d.get("bln_enviado", []))
            d["alertas_activas"] = set(d.get("alertas_activas", []))
            return d
    except:
        return {
            "temp_max": -99.0,
            "temp_min":  99.0,
            "viento_max": 0.0,
            "fecha": None,
            "bln_enviado": set(),
            "alertas_activas": set()
        }

def guardar_estado(ed):
    try:
        d = ed.copy()
        d["bln_enviado"]     = list(ed["bln_enviado"])
        d["alertas_activas"] = list(ed["alertas_activas"])
        with open(ESTADO_FILE, "w") as f:
            json.dump(d, f)
    except Exception as e:
        print(f"Error saving state: {e}")

def nivel_riesgo_incendio(temp_max, hum_min, viento_max):
    """
    Calculates fire risk level based on DMC criteria.
    Returns: BAJO / MEDIO / ALTO / EXTREMO
    """
    try:
        t = float(temp_max)   if temp_max   else 0
        h = float(hum_min)    if hum_min    else 100
        v = float(viento_max) if viento_max else 0
        puntos = 0
        if t >= 35:   puntos += 3
        elif t >= 30: puntos += 2
        elif t >= 25: puntos += 1
        if h < 15:    puntos += 3
        elif h < 30:  puntos += 2
        elif h < 50:  puntos += 1
        if v > 70:    puntos += 3
        elif v > 50:  puntos += 2
        elif v > 30:  puntos += 1
        if puntos >= 7:   return "EXTREMO"
        elif puntos >= 4: return "ALTO"
        elif puntos >= 2: return "MEDIO"
        else:             return "BAJO"
    except:
        return "?"

def enviar_aprs(sock_params, login, paquetes):
    """Sends APRS packets with automatic retry (3 attempts)."""
    host, port = sock_params
    for i, p in enumerate(paquetes):
        enviado = False
        for intento in range(3):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(15)
                sock.connect((host, port))
                sock.send(f"{login}\n".encode())
                time.sleep(1)
                sock.send(f"{p}\n".encode())
                time.sleep(0.5)
                sock.close()
                print(f"[OK] Packet {i+1}/{len(paquetes)}: {p[:80]}")
                enviado = True
                break
            except Exception as e:
                print(f"[RETRY {intento+1}] Error packet {i+1}: {e}")
                time.sleep(5)
        if not enviado:
            print(f"[FAILED] Could not send packet {i+1}: {p[:80]}")
        if i < len(paquetes) - 1:
            time.sleep(15)

password    = calculate_aprs_passcode(callsign)
address     = f"{callsign}>APZ000,TCPIP*:"
login       = f"user {callsign} pass {password} vers CA2JAT-WX 1.3"
latg        = latitude.replace(".", "", 1)
long        = longitude.replace(".", "", 1)
sock_params = (serverHost, serverPort)
estado_dia  = cargar_estado()
bln_offset  = calcular_offset_bln(callsign)

# ============================================================
# DATA SOURCES
# ============================================================

def get_datos_dmc():
    """Gets weather data from DMC EMA station."""
    url = (
        f"https://climatologia.meteochile.gob.cl/application/servicios/"
        f"getDatosRecientesEma/{mc_estacion}"
        f"?usuario={mc_usuario}&token={mc_token}"
    )
    r    = requests.get(url, timeout=15)
    data = r.json()
    u    = data["datosEstaciones"]["datos"][0]

    momento = datetime.strptime(u["momento"], "%Y-%m-%d %H:%M:%S")
    diff    = (datetime.utcnow() - momento).total_seconds() / 3600
    if diff > 2:
        raise Exception(f"DMC: data is {diff:.1f}h old")

    temp_c   = float(u["temperatura"].split()[0])
    temp_f   = celsius_to_fahrenheit(temp_c)
    humidity = min(int(float(u["humedadRelativa"].split()[0])), 99)
    pres     = float(u["presionNivelDelMar"].split()[0])
    deg      = str(int(float(u["direccionDelVientoPromedio10Minutos"].split()[0]))).zfill(3)
    wind_kt  = float(u["fuerzaDelVientoPromedio10Minutos"].split()[0])
    wind_mph = knots_to_mph(wind_kt)
    wind_kmh = knots_to_kmh(wind_kt)
    gust_raw = u.get("fuerzaDelViento10MinutosMax")
    gust_mph = knots_to_mph(float(gust_raw.split()[0])) if gust_raw else 0
    gust_kmh = knots_to_kmh(float(gust_raw.split()[0])) if gust_raw else 0
    rain_1h  = float(u.get("aguaCaidaDelMinuto", "0 mm").split()[0])
    rain_24h = float(u.get("aguaCaida24Horas",   "0 mm").split()[0])

    try:
        lumi = min(int(float(u["radiacionGlobalInst"].split()[0])), 999)
    except:
        lumi = 0

    wx_str = (
        f"{deg}/{str(int(wind_mph)).zfill(3)}"
        f"g{str(int(gust_mph)).zfill(3)}"
        f"t{str(int(temp_f)).zfill(3)}"
        f"r{str(int(rain_1h  / 25.4 * 100)).zfill(3)}"
        f"p{str(int(rain_24h / 25.4 * 100)).zfill(3)}"
        f"h{humidity}"
        f"b{str(int(pres * 10)).zfill(5)}"
        f"L{str(lumi).zfill(3)}"
        f"0 EMA {mc_comuna} DMC"
    )

    return {
        "wx_str": wx_str, "temp_c": temp_c,
        "wind_kmh": wind_kmh, "gust_kmh": gust_kmh,
        "rain_1h": rain_1h, "humidity": humidity,
        "pres": pres, "fuente": "DMC"
    }

def get_datos_owm():
    """Gets weather data from OpenWeatherMap (fallback)."""
    url  = (f"https://api.openweathermap.org/data/2.5/weather"
            f"?id={owm_map_id}&lang={owm_lang}&units=metric&appid={owm_api_key}")
    r    = requests.get(url, timeout=10)
    data = r.json()

    temp_c   = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    pres     = data["main"]["pressure"]
    wind_ms  = data["wind"]["speed"]
    wind_kmh = wind_ms * 3.6
    wind_mph = wind_ms * 2.237
    gust_ms  = data["wind"].get("gust", 0)
    gust_mph = gust_ms * 2.237
    gust_kmh = gust_ms * 3.6
    deg      = str(int(data["wind"]["deg"])).zfill(3)
    rain_1h  = data.get("rain", {}).get("1h", 0)
    desc     = data["weather"][0]["description"]
    clouds   = data["clouds"]["all"]
    is_day   = data["sys"]["sunrise"] < data["dt"] < data["sys"]["sunset"]
    lumi     = int(1000 * (1 - clouds / 100)) if is_day else 0

    wx_str = (
        f"{deg}/{str(int(wind_mph)).zfill(3)}"
        f"g{str(int(gust_mph)).zfill(3)}"
        f"t{str(int(celsius_to_fahrenheit(temp_c))).zfill(3)}"
        f"r{str(int(rain_1h / 25.4 * 100)).zfill(3)}"
        f"p000h{humidity}"
        f"b{str(int(pres * 10)).zfill(5)}"
        f"L{str(min(lumi, 999)).zfill(3)}"
        f"0 OWM:{desc}"
    )

    return {
        "wx_str": wx_str, "temp_c": temp_c,
        "wind_kmh": wind_kmh, "gust_kmh": gust_kmh,
        "rain_1h": rain_1h, "humidity": humidity,
        "pres": pres, "fuente": "OWM"
    }

def get_riesgo_incendio():
    """Gets fire risk data from DMC GeoServices."""
    url  = (f"https://climatologia.meteochile.gob.cl/application/geoservicios/"
            f"getRiesgoIncendio?usuario={mc_usuario}&token={mc_token}")
    r    = requests.get(url, timeout=15)
    data = r.json()
    for f in data.get("features", []):
        p = f.get("properties", {})
        if mc_comuna.lower() in str(p.get("comuna", "")).lower():
            return {
                "temp_max_hoy":      p.get("temperaturaMaximaHoy"),
                "temp_max_manana":   p.get("temperaturaMaximaManana"),
                "hum_min_hoy":       p.get("humedadMinimaHoy"),
                "hum_min_manana":    p.get("humedadMinimaManana"),
                "viento_max_hoy":    p.get("intensidadVientoMaximoHoy"),
                "viento_max_manana": p.get("intensidadVientoMaximoManana"),
            }
    return None

# ============================================================
# WX ALERTS
# ============================================================

def evaluar_alertas(datos):
    """Generates alert packets if thresholds are exceeded."""
    alertas = []
    now_key = datetime.now(TZ_LOCAL).strftime("%Y%m%d%H")

    def alerta(clave, msg):
        key = f"{clave}_{now_key}"
        if key not in estado_dia["alertas_activas"]:
            estado_dia["alertas_activas"].add(key)
            alertas.append(f"{address}>{msg}")
            print(f"[ALERT] {msg}")

    if datos["temp_c"] >= ALERTA_CALOR:
        alerta("calor",  f"ALERTA-WX: Calor extremo {datos['temp_c']:.1f}C en {mc_comuna}")
    if datos["temp_c"] <= ALERTA_HELADA:
        alerta("helada", f"ALERTA-WX: Riesgo helada {datos['temp_c']:.1f}C en {mc_comuna}")
    if datos["gust_kmh"] >= ALERTA_VIENTO:
        alerta("viento", f"ALERTA-WX: Viento fuerte {datos['gust_kmh']:.0f}km/h en {mc_comuna}")
    if datos["rain_1h"] >= ALERTA_LLUVIA:
        alerta("lluvia", f"ALERTA-WX: Lluvia intensa {datos['rain_1h']:.1f}mm/h en {mc_comuna}")

    return alertas

# ============================================================
# BLN BULLETINS
# ============================================================

def generar_bln(datos, riesgo):
    """Generates APRS BLN bulletin packets."""
    bln = []
    ed  = estado_dia

    # BLN0 - Daily summary
    bln0 = (f"WX {mc_comuna}: {datos['temp_c']:.1f}C "
            f"Max:{ed['temp_max']:.1f}C Min:{ed['temp_min']:.1f}C "
            f"HR:{datos['humidity']}% Vmax:{ed['viento_max']:.0f}km/h "
            f"[{datos['fuente']}]")
    bln.append(f"{address}:BLN0     :{bln0[:67]}")

    if riesgo:
        # BLN1 - Tomorrow's forecast
        tm  = riesgo.get("temp_max_manana", "?")
        hm  = riesgo.get("hum_min_manana",  "?")
        vm  = riesgo.get("viento_max_manana","?")
        bln1 = (f"Pronostico manana: TMax:{tm}C "
                f"HumMin:{hm}% Vmax:{vm}km/h DMC")
        bln.append(f"{address}:BLN1     :{bln1[:67]}")

        # BLN2 - Fire risk alert with level
        th    = riesgo.get("temp_max_hoy",   "?")
        hh    = riesgo.get("hum_min_hoy",    "?")
        vh    = riesgo.get("viento_max_hoy", "?")
        nivel = nivel_riesgo_incendio(th, hh, vh)
        bln2  = (f"Alerta Incendio: {nivel} "
                 f"TMax:{th}C HumMin:{hh}% Vmax:{vh}km/h")
        bln.append(f"{address}:BLN2     :{bln2[:67]}")
    else:
        bln.append(f"{address}:BLN1     :Datos pronostico DMC no disponibles")

    return bln

def verificar_bln(datos, riesgo):
    """Checks if it's time to send BLN with callsign-based offset."""
    ahora    = datetime.now(TZ_LOCAL)
    hora_now = ahora.hour
    min_now  = ahora.minute
    fecha    = ahora.strftime("%Y%m%d")

    # Daily reset
    if estado_dia["fecha"] != fecha:
        estado_dia.update({
            "fecha": fecha, "bln_enviado": set(),
            "temp_max": -99.0, "temp_min": 99.0,
            "viento_max": 0.0, "alertas_activas": set()
        })
        guardar_estado(estado_dia)

    # Check each configured BLN hour
    for hora_bln in BLN_HORAS:
        clave = f"{fecha}_{hora_bln}"
        if (hora_now == hora_bln and
                min_now >= bln_offset and
                clave not in estado_dia["bln_enviado"]):
            estado_dia["bln_enviado"].add(clave)
            guardar_estado(estado_dia)
            print(f"[BLN] Sending BLN offset:{bln_offset}min hour:{hora_bln}:{bln_offset:02d}")
            return generar_bln(datos, riesgo)
    return []

# ============================================================
# MAIN LOOP
# ============================================================

print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] APRS-WX-CE v1.3 starting... ({callsign})")
print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] BLN scheduled at: "
      f"{BLN_HORAS[0]:02d}:{bln_offset:02d} and {BLN_HORAS[1]:02d}:{bln_offset:02d} "
      f"(offset {bln_offset} min based on callsign)")

while True:
    try:
        try:
            datos = get_datos_dmc()
        except Exception as e_dmc:
            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] DMC failed: {e_dmc} -> OWM fallback")
            datos = get_datos_owm()

        if datos["temp_c"] > estado_dia["temp_max"]:
            estado_dia["temp_max"] = datos["temp_c"]
        if datos["temp_c"] < estado_dia["temp_min"]:
            estado_dia["temp_min"] = datos["temp_c"]
        if datos["gust_kmh"] > estado_dia["viento_max"]:
            estado_dia["viento_max"] = datos["gust_kmh"]
        guardar_estado(estado_dia)

        riesgo = None
        try:
            riesgo = get_riesgo_incendio()
        except Exception as e_ri:
            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Fire risk unavailable: {e_ri}")

        ts     = datetime.utcnow().strftime("%d%H%M")
        pkt_wx = f"{address}@{ts}z{latg}/{long}_{datos['wx_str']}"

        pkts_alerta = evaluar_alertas(datos)
        pkts_bln    = verificar_bln(datos, riesgo)

        enviar_aprs(sock_params, login, [pkt_wx] + pkts_alerta + pkts_bln)

        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] [{datos['fuente']}] "
              f"T:{datos['temp_c']:.1f}C Max:{estado_dia['temp_max']:.1f}C "
              f"Min:{estado_dia['temp_min']:.1f}C | "
              f"Alerts:{len(pkts_alerta)} BLN:{len(pkts_bln)}")

    except Exception as e:
        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] General error: {e}")

    time.sleep(every * 60)
