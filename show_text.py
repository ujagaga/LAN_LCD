"""
pip install flask pyserial
"""

from flask import Flask, request, jsonify
import serial
import json
import threading
import time

# ---------------- Configuration ----------------

SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_BAUD = 115200
SERIAL_TIMEOUT = 1.0      # read timeout (seconds)
UART_RESPONSE_WAIT = 0.5  # how long to wait after sending

COLORS = {
    "BLACK":      "0000",
    "NAVY":       "000F",
    "BLUE":       "001F",
    "TEAL":       "07EF",
    "GREEN":      "07E0",
    "CYAN":       "07FF",
    "MAROON":     "7800",
    "RED":        "F800",
    "PURPLE":     "780F",
    "OLIVE":      "7BE0",
    "YELLOW":     "FFE0",
    "ORANGE":     "FD20",
    "PINK":       "F81F",
    "BROWN":      "79E0",
    "GRAY":       "8410",
    "DARKGRAY":   "4208",
    "LIGHTGRAY":  "C618",
    "WHITE":      "FFFF",
}

# -----------------------------------------------

app = Flask(__name__)
app.json.compact = False
serial_lock = threading.Lock()

# Open serial port ONCE
ser = serial.Serial(
    SERIAL_PORT,
    SERIAL_BAUD,
    timeout=SERIAL_TIMEOUT
)

# Disable Arduino auto-reset
time.sleep(1)  # allow Arduino to stabilize

def send_to_lcd(payload: dict):
    """
    Send JSON payload to Arduino over UART
    and read one-line response (if any).
    """
    message = json.dumps(payload, separators=(",", ":")) + "\n"

    with serial_lock:
        # Clear any stale input
        ser.reset_input_buffer()

        # Send command
        ser.write(message.encode("utf-8"))
        ser.flush()

        # Give Arduino time to respond
        time.sleep(UART_RESPONSE_WAIT)

        # Read response (non-blocking due to timeout)
        response = ser.readline().decode("utf-8", errors="ignore").strip()

    return response if response else None

def normalize_colors(payload: dict) -> dict:
    """
    Replace predefined color names with RGB565 hex values.
    Operates on fg and bg keys only.
    """
    normalized = payload.copy()

    for key in ("fg", "bg"):
        value = normalized.get(key)
        if not value:
            continue

        # Normalize case
        value_upper = value.upper()

        # Replace named color with hex value
        if value_upper in COLORS:
            normalized[key] = COLORS[value_upper]

    return normalized

def render_color_list():
    items = []
    for name, value in COLORS.items():
        items.append(f"<li><b>{name}</b> – {value}</li>")
    return "\n".join(items)

# ---------------- Routes ------------------------

@app.route("/", methods=["GET"])
def index():
    return f"""
    <h2>LAN LCD Controller</h2>

    <p>Send display commands to the LCD using JSON.</p>

    <h3>Supported keys</h3>
    <ul>
      <li><b>txt</b> – text to display</li>
      <li><b>fg</b> – foreground color (name or RGB565 hex)</li>
      <li><b>bg</b> – background color (name or RGB565 hex)</li>
      <li><b>size</b> – text size (1–5)</li>
    </ul>
    <p>Note: All keys are optional. If omitted, the previous value is reused.</p>

    <h3>Predefined colors</h3>
    <p>Colors are RGB565, 4-digit HEX codes:</p>
    <ul>
      {render_color_list()}
    </ul>

    <h3>Examples</h3>

    <p><b>GET:</b></p>
    <pre>/set/?txt=Hello&fg=WHITE&bg=BLUE&size=3</pre>

    <p><b>POST:</b></p>
    <pre>
POST /set/
Content-Type: application/json

{{
  "txt": "Hello",
  "fg": "WHITE",
  "bg": "0000",
  "size": 2
}}
    </pre>
    """


@app.route("/set/", methods=["GET", "POST"])
def set_display():
    try:
        if request.method == "GET":
            payload = {
                k: request.args.get(k)
                for k in ("txt", "fg", "bg", "size")
                if k in request.args
            }
            if not payload:
                return jsonify(error="No parameters provided"), 400
        else:
            payload = request.get_json(silent=True)
            if not payload:
                return jsonify(error="Invalid or missing JSON body"), 400

        normalized_payload = normalize_colors(payload)
        uart_response = send_to_lcd(normalized_payload)

        return jsonify(
            status="ok",
            sent=normalized_payload,
            uart_response=uart_response
        )

    except serial.SerialException as e:
        return jsonify(error="Serial error", detail=str(e)), 500

    except Exception as e:
        return jsonify(error="Internal error", detail=str(e)), 500

# ---------------- Entry Point -------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )
