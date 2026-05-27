from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import base64
from io import BytesIO
from matplotlib.figure import Figure
import mysql.connector
import threading
import time


def get_conn():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="vanaguard",
        password="gruppe7!",
        database="heste_data",
    )



def fetch_recent(limit=10):
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT timestamp, temperature, humidity, fan_on, window_open,
                   smoke_detected, horse_down_count
            FROM sensor_readings
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        for r in rows:
            if r.get("timestamp"):
                r["timestamp"] = r["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        return list(reversed(rows))
    finally:
        cursor.close()
        conn.close()


def fetch_latest():
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT timestamp, temperature, humidity, fan_on, window_open,
                   smoke_detected, horse_down_count
            FROM sensor_readings
            ORDER BY timestamp DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if row and row.get("timestamp"):
            row["timestamp"] = row["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        return row
    finally:
        cursor.close()
        conn.close()



def generate_chart(x_data, y_data, bottom=0.3):
    fig = Figure()
    ax = fig.subplots()
    fig.subplots_adjust(bottom=bottom)
    ax.tick_params(axis='x', rotation=45)
    ax.plot(x_data, y_data)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def get_charts():
    rows = fetch_recent(10)
    timestamps   = [str(r["timestamp"]) for r in rows]
    temperatures = [r["temperature"]    for r in rows]
    humidities   = [r["humidity"]       for r in rows]
    return {
        "temp_chart": generate_chart(timestamps, temperatures, bottom=0.3),
        "hum_chart":  generate_chart(timestamps, humidities,  bottom=0.4),
    }



app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
socketio = SocketIO(app)


state = {
    "alarm":     False,
    "battery":   None,
    "last_seen": None,
}




def poll_db(sio):
    while True:
        try:
            charts = get_charts()
            latest = fetch_latest()
            sio.emit("sensor_update", {**charts, "latest": latest})
        except Exception as e:
            print(f"[poll_db] error: {e}")
        time.sleep(5)




@app.route("/")
def home():
    return render_template("home.html")

@app.route("/yolo/")
def yolo():
    return render_template("yolo.html")

@app.route("/målinger/")
def målinger():
    return render_template("målinger.html")

@app.route("/brand_alarm/")
def brand_alarm():
    return render_template("brand_alarm.html")

@app.route("/index/")
def index():
    return render_template("index.html")




@app.route("/api/data/latest")
def api_latest():
    """Most recent sensor row as JSON."""
    row = fetch_latest()
    if row:
        row["timestamp"] = str(row["timestamp"])
    return jsonify(row)


@app.route("/api/data/history")
def api_history():
    """Last N rows; pass ?limit=N (default 10, max 200)."""
    limit = min(int(request.args.get("limit", 10)), 200)
    rows = fetch_recent(limit)
    for r in rows:
        r["timestamp"] = str(r["timestamp"])
    return jsonify(rows)




@app.route("/api/alarm", methods=["GET"])
def get_alarm():
    state["last_seen"] = time.time()
    return jsonify({"alarm": state["alarm"]})


@app.route("/api/alarm", methods=["POST"])
def set_alarm():
    data = request.get_json()
    state["alarm"] = bool(data.get("alarm", False))
    print(f"[ALARM] {'ON' if state['alarm'] else 'OFF'}")
    return jsonify({"ok": True, "alarm": state["alarm"]})




@app.route("/api/battery", methods=["POST"])
def receive_battery():
    data = request.get_json()
    pct = max(0, min(100, int(data.get("battery", 0))))
    state["battery"]   = pct
    state["last_seen"] = time.time()
    print(f"[BATTERY] {pct}%")
    return jsonify({"ok": True})


@app.route("/api/status", methods=["GET"])
def get_status():
    online = (
        state["last_seen"] is not None and
        (time.time() - state["last_seen"]) < 15
    )
    
    latest = fetch_latest() or {}
    if latest.get("timestamp"):
        latest["timestamp"] = str(latest["timestamp"])
    return jsonify({
        "alarm":   state["alarm"],
        "battery": state["battery"],
        "online":  online,
        **latest,
    })




@socketio.on("connect")
def on_connect():
    emit("sensor_update", get_charts())

@socketio.on("request_update")
def on_request_update():
    emit("sensor_update", get_charts())




if __name__ == "__main__":
    print("Starting DB poller thread...")
    threading.Thread(target=poll_db, args=(socketio,), daemon=True).start()

    print("Server starting...")
    socketio.run(app, host="0.0.0.0", debug=False)