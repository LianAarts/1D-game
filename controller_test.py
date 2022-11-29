from evdev import InputDevice, categorize, ecodes

print("ACGAM R1 - pad mapping")

#creates object 'gamepad' to store the data
gamepad = InputDevice('/dev/input/event2')

#button code variables (change to suit your device)
cross = 304
circle = 305
triangle = 307
square = 308
up = 17
down = 114
left = 16
right = 163
playpause = 164

#loop and filter by event code and print the mapped label
for event in gamepad.read_loop():
    if event.type == 3:  # A stick is moved
        if event.code == 17:  # up and down arrows
            if event.value == 1:
                print('down')
            if event.value == -1:
                print('up')
        if event.code == 16:  # left and right arrows
            if event.value == 1:
                print('right')
            if event.value == -1:
                print('left')
    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            if event.code == cross:
                print("x")
            elif event.code == circle:
                print("circle")
            elif event.code == triangle:
                print("triangle")
            elif event.code == square:
                print("square")
            elif event.code == playpause:
                print("option")
            elif event.code == up:
                print("up")
            elif event.code == down:
                print("down")
            elif event.code == left:
                print("left")
            elif event.code == right:
                print("right")