import RPi.GPIO as GPIO
from time import sleep
from flask import Flask, render_template, request, redirect, url_for
from threading import Thread
from enum import Enum
from gpiozero import RGBLED, DistanceSensor, Device, Servo
from gpiozero.pins.pigpio import PiGPIOFactory


class State(Enum):
    OFF = 0
    AUTO = 1
    MANUAL = 2
    LED = 3
    TERMINATE = 4


def main_loop():
    while True:
        if state == State.TERMINATE:
            led.off()
            servo.detach()
        if state == State.AUTO:
            distance = ultrasonic.distance
            sleep(0.01)
            servo.min()
            sleep(distance)
            servo.mid()
            sleep(distance)
            servo.max()
        if state == State.MANUAL:
            speed = manual_speed
            if speed == 1: speed = 0.99
            servo.min()
            sleep(1-speed)
            servo.mid()
            sleep(1-speed)
            servo.max()
            sleep(1-speed+0.05)

        sleep(0.05)





app = Flask(__name__)
state = State.OFF
manual_speed = 0
colors = (0,0,0)

Device.pin_factory = PiGPIOFactory()
GPIO.setmode(GPIO.BCM)

servo = Servo(25)
led = RGBLED(red=17, green=27, blue=22)
ultrasonic = DistanceSensor(echo=24, trigger=23, max_distance=0.5)


@app.route("/")
def index():
    global state
    return render_template("index.html", state=str(state), speed=manual_speed)


@app.route("/setState/<new_state>", methods=["POST"])
def set_state(new_state):
    global colors, manual_speed, state

    data = request.json
    if new_state == "MANUAL":
        manual_speed = data["speed"]
        state = State.MANUAL
    elif new_state == "AUTO":
        state = State.AUTO
    elif new_state == "LED":
        if state == State.TERMINATE: state = State.OFF
        colors = (data["r"]/255, data["g"]/255, data["b"]/255)
        led.color = colors
        sleep(0.01)
        return "", 204

    state = State[new_state]
    return redirect(url_for("index"))


@app.route("/toggleProgram", methods=["POST"])
def terminate():
    global state
    state = State.TERMINATE
    return redirect(url_for("index"))

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    Thread(name="loop", target=main_loop).start()
    app.run(host="172.16.2.132", port=5000, debug=True)