import RPi.GPIO as GPIO
import time
from flask import Flask, render_template, request
import board
import neopixel

pixel_pin = board.D18

num_pixels = 144

ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, auto_write=True, pixel_order=ORDER
)

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

i = 0

@app.route("/<deviceName>/<action>")
def action(deviceName, action):
    global i
    if deviceName == 'led':
        if action == "up":
            i = i+1
            pixels[i] = (255, 0, 0)
            pixels[i-1] = (0, 0, 0)
            time.sleep(0.5)


        if action == "down":
            i = i-1
            pixels[i] = (255, 0, 0)
            pixels[i+1] = (0, 0, 0)
            time.sleep(0.5)


    templateData = {
        'led': i,
    }
    return render_template('index.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

