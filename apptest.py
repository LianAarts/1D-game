from flask import Flask, render_template, request

app = Flask(__name__)

# Simple test for NeoPixels on Raspberry Pi
import time
import board
import neopixel

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D12

# The number of NeoPixels
num_pixels = 144

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, auto_write=True, pixel_order=ORDER
)

@app.route("/")
def action(deviceName, action, i=0):
    if deviceName == 'led':
        if action == "up":
            i += 1
        if action == "down":
            i -=1

    pixels[i]((0, 255, 0))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)(debug=True, port=80, host='192.168.2.2')

