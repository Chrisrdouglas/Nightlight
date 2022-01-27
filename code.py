import neopixel
import board
from analogio import AnalogIn
import rotaryio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
from time import sleep, monotonic

sw = board.GP20
dt = board.GP14
clk = board.GP13
photoResistorPin = board.GP26
neopixelDataPin = board.GP0

pin = DigitalInOut(sw)
pin.direction = Direction.INPUT
pin.pull = Pull.UP
switch = Debouncer(pin)

pixels = neopixel.NeoPixel(neopixelDataPin, 1)

photoResistor = AnalogIn(photoResistorPin)


encoder = rotaryio.IncrementalEncoder(clk, dt) # 18 is the blah pin on the . 17 is the blah2 pin on the rotary encoder
encoder.position = 20
encoder_max = 20
encoder_min = 0

wheelDirection = 1
last_position = None
last_button_position = True
last_color = (255, 255, 255)
t = 0  # tick counter for the colorwheel
last_time = 0
colorWheelIndex = 0

colorWheel = [(255, 255, 255),  # white
              (255, 255, 000),  # yellow
              (255, 165, 000),  # orange
              (255, 000, 000),  # red
              (255, 192, 203),  # pink
              (255, 000, 255),  # purple
              (000, 000, 255),  # blue
              (000, 255, 255),  # cyan
              (000, 255, 000),  # green
              ( 50, 205,  50),  # lime green
              ( -1,  -1,  -1),  # rainbow
              (000, 000, 000)]  # off

x = 6000 # adjust me to change the sensitivity to light


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)


while True:
    switch.update()
    write_color = pixels[0]
    if not switch.value and switch.value != last_button_position: #switch is normally high??
        colorWheelIndex += 1
        colorWheelIndex = colorWheelIndex % len(colorWheel)
        last_color = colorWheel[colorWheelIndex]
        if last_color == (-1,-1,-1):
            t = 0
    last_button_position = switch.value


    # check if the encoder has move
    encPos = encoder.position
    if last_position is None or last_position != encPos:
        if encPos > encoder_max:
            encPos = encoder_max
        elif encPos < encoder_min:
            encPos = encoder_min
    last_position = encPos


    brightness = encPos*0.05

    if last_color == (-1,-1,-1): # compute color from t
        now = monotonic()
        if now > last_time+5:
            last_time = now
            write_color = wheel(t)
            t += wheelDirection
            if t > 255:
                wheelDirection = -1
                t=255
            elif t < 0:
                wheelDirection = 1
                t = 0
    else:  # or we just tell it to keep the last color
        write_color = last_color
    
    print(photoResistor.value)
    if photoResistor.value > x:
       if pixels[0] != (0,0,0):
            pixels[0] = (0,0,0)
    else:
        if pixels[0] != last_color:
            pixels[0] = last_color
        if pixels.brightness != brightness:
            pixels.brightness = brightness
    sleep(0.05)





