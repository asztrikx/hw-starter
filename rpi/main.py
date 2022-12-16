from flask import send_from_directory
import json
import sqlite3
import threading
from datetime import datetime
from math import ceil

import serial
from flask import Flask, jsonify
from flask_cors import CORS

ser = serial.Serial("/dev/ttyS0", 9600)
api = Flask(__name__)
CORS(api)


@api.route('/<path:path>', methods=['GET'])
def index(path):
    return send_from_directory('public', path)


@api.route('/data', methods=['GET'])
def get():
    return jsonify({
        "temperature": lastTemperature,
        "light": lastLight,
    })


@api.route('/dataAll', methods=['GET'])
def getAll():
    con = sqlite3.connect("sensor.db")
    cur = con.cursor()
    res = cur.execute("SELECT date, sensorType, value FROM data")
    rows = res.fetchall()
    structs = []
    for row in rows:
        structs.append({
            "date": row[0],
            "sensorType": row[1],
            "value": row[2],
        })
    cur.close()
    con.close()
    return jsonify(structs)


def uartRead():
    global con
    con = sqlite3.connect("sensor.db")
    while True:
        jsonData = ser.readline()
        # try:
        data = json.loads(jsonData)
        handleTemperatureVoltage(data["temperature"])
        handleLightVoltage(data["light"])
        # except:
        #    print("data read error")
        #    continue


lastTemperature = 1000
lastTemperatureStoreDate = ""


def handleTemperatureVoltage(temperatureVoltage):
    #print("Temp voltage: " + str(temperatureVoltage))
    temperatureVoltage *= 1.7
    # 7.686*X + 808.4
    temperature = (temperatureVoltage - 808.4) / 7.686
    global lastTemperature, lastTemperatureStoreDate
    lastTemperature = temperature

    if (currentDate() != lastTemperatureStoreDate):
        lastTemperatureStoreDate = currentDate()
        storeData("temperature", temperature)


lastLight = 600
lastLightStoreDate = ""


def handleLightVoltage(lightVoltage):
    #print("Light voltage: " + str(lightVoltage))
    light = lightVoltage
    global lastLight, lastLightStoreDate
    lastLight = light

    handleLightLeds(light)

    if (currentDate() != lastLightStoreDate):
        lastLightStoreDate = currentDate()
        storeData("light", light)


def storeData(sensorType, value):
    data = [
        currentDate(), sensorType, value,
    ]
    cur = con.cursor()
    cur.execute("""
        INSERT INTO data (date, sensorType, value)
        VALUES (?,?,?)
    """, data)
    con.commit()
    cur.close()


def handleLightLeds(light):
    lightMin = 995
    lightMax = 1020
    ledCount = 6

    unit = (lightMax - lightMin) / ledCount
    x = min(light, lightMax)
    x = max(light, lightMin)
    led = ceil((x - lightMin) / unit)

    ledControl = {
        "ledGreen0": led >= 1,
        "ledGreen1": led >= 2,
        "ledYellow0": led >= 3,
        "ledYellow1": led >= 4,
        "ledRed0": led >= 5,
        "ledRed1": led >= 6,
    }
    ser.write((json.dumps(ledControl) + "\n\r").encode())


def currentDate():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    threading.Thread(target=uartRead).start()
    api.run(host='0.0.0.0', port=80)
