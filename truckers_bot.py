
import requests, time, json, subprocess, threading, queue

API = "https://api.weather.gov/alerts/active"
HEADERS = {"User-Agent":"TruckersBotV8"}

ALERT_FILTER = [
"Tornado Warning",
"Tornado Watch",
"Severe Thunderstorm Warning",
"Severe Thunderstorm Watch",
"Flash Flood Warning",
"Flash Flood Watch",
"Flood Warning",
"High Wind Warning",
"Wind Advisory",
"Blizzard Warning",
"Winter Storm Warning",
"Ice Storm Warning",
"Dense Fog Advisory",
"Fire Weather Watch",
"Red Flag Warning",
"Dust Storm Warning",
"Special Weather Statement"
]

seen=set()
speech_queue = queue.Queue()

def voice_worker():
    while True:
        text = speech_queue.get()
        try:
            subprocess.run(["python","jenny_voice.py", text])
        except Exception as e:
            print("Voice error:", e)
        speech_queue.task_done()

threading.Thread(target=voice_worker, daemon=True).start()

def speak(event, area):
    message = f"Attention truck drivers. {event} issued for {area}. Use caution if traveling."
    speech_queue.put(message)

def poll():
    r=requests.get(API, headers=HEADERS, timeout=15)
    return r.json().get("features", [])

print("Truckers Bot V8 running...")

# Startup briefing – speak last 5 alerts
try:
    initial_alerts = poll()

    # sort by newest first
    initial_alerts.sort(key=lambda x: x["properties"].get("sent",""), reverse=True)

    recent = initial_alerts[:5]

    for a in recent:
        p = a["properties"]
        event = p.get("event","Unknown")

        if event not in ALERT_FILTER:
            continue

        ident = p.get("id")
        seen.add(ident)

        area = p.get("areaDesc","Unknown").split(";")[0]

        print("STARTUP ALERT:", event, area)

        speak(event, area)

except Exception as e:
    print("Startup error:", e)

while True:
    try:
        alerts = poll()

        for a in alerts:

            p=a["properties"]
            event=p.get("event","Unknown")
            ident=p.get("id")

            if event not in ALERT_FILTER:
                continue

            if ident in seen:
                continue

            seen.add(ident)

            area=p.get("areaDesc","Unknown").split(";")[0]
            polygon=a.get("geometry")

            print("NEW ALERT:", event, area)

            speak(event, area)

            display = {
                "event":event,
                "area":area,
                "headline":p.get("headline","")
            }

            with open("warning_data.json","w") as f:
                json.dump(display,f,indent=2)

            zoom = {
                "event":event,
                "area":area,
                "polygon":polygon
            }

            with open("zoom_alert.json","w") as f:
                json.dump(zoom,f,indent=2)

        time.sleep(10)

    except Exception as e:
        print("Error:",e)
        time.sleep(10)
