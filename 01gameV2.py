from evdev import InputDevice, categorize, ecodes

import time
import _thread
import board

import neopixel

brightness = 0.1
pixel_pin = board.D18
num_pixels = 144
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=brightness, auto_write=False, pixel_order=ORDER)

minPixel = 0
maxPixel = 144

gamepad = InputDevice('/dev/input/event2')

cross = 304
circle = 305
triangle = 307
square = 308

enemies = [] # [delay, speed, enemiePos]
enemyColor = [255, 0, 0]
enemyDeadPosition = -5000

water = [] # [startpunt, lengte]
playerInWater = False

attackRange = 10
attackPositionPos = 0
attackPositionNeg = 0

playerPosition = 0
playerTotalLives = 3
playerCurrentLives = playerTotalLives
playerStartColor = [0, 255, 0]
playerCurrentColor = playerStartColor
playerMovementSpeed = 90 #waarde tussen 1 en 99
playerMoveDirection = 0
playerTotalElapsedSec = 0
round = 0
pause = False
canPlayerMove = True
isFinished = True

finishPosition = maxPixel - 1
finishColor = [128,0,128]


# helper function for substracting one colors
def subtractColor(color1, color2):
    # subtracts color 1 from color 2 to make a new color
    newColor = []
    tempColor = 0

    for i in range(len(color1)):
        if color1[i] >= color2[i]:
            tempColor = color1[i] - color2[i]
        else:
            tempColor = color2[i] - color1[i]
        if tempColor < 0:
            tempColor = 0
        newColor.append(tempColor)
    return newColor

# helper function for adding one colors
def addColor(color1, color2):
    # adds color 1 to color 2 to make a new color
    newColor = []
    tempColor = 0

    for i in range(len(color1)):
        tempColor = color1[i] + color2[i]
        if tempColor > 255:
            tempColor = 255
        newColor.append(tempColor)
    return newColor


def divideColor(color, number):
    # devide color 1 with number to make a new color
    newColor = []
    tempColor = 0

    for i in range(len(color)):
        tempColor = int(color[i] / number)
        newColor.append(tempColor)
    return newColor


def multiplyColor(color, number):
    # multiply color 1 with number to make a new color
    newColor = []
    tempColor = 0

    for i in range(len(color)):
        tempColor = int(color[i] * number)
        if tempColor > 255:
            tempColor = 255
        newColor.append(tempColor)
    return newColor

# def calcWater():
#     for droplet in water:
#         for i in range((droplet[0] - droplet[1]), (droplet[0]+1)):

def drawWater():
    x = 0
    for droplet in water:
        for x in range(droplet[1]):
            pixels[droplet[0]-x] = (0,0,255)


def inWater():
    global water
    global playerInWater
    for droplet in water:
        if droplet[0]-droplet[1] < playerPosition < droplet[0]:
            playerInWater = True
        else:
            playerInWater = False


def movePlayer(elapsedSec):
    global pause
    global playerPosition
    global playerMoveDirection
    global playerCurrentColor
    global canPlayerMove
    global minPixel
    global maxPixel
    global playerTotalElapsedSec
    playerTotalElapsedSecPast = False

    

    playerTotalElapsedSec += elapsedSec
    stepSize = 1

    # if playerInWater and playerMoveDirection == 1:
    #     time.sleep(playerMovementSpeed * 5)
    # elif playerInWater and playerMoveDirection == -1:
    #     time.sleep(playerMovementSpeed / 3)
    # elif not playerInWater and (playerMoveDirection == 1 or playerMoveDirection == -1):
    #     time.sleep(playerMovementSpeed)

    calculatedSpeed = ((100 - playerMovementSpeed) / 1000)

    if playerInWater and playerMoveDirection == 1:
        if playerTotalElapsedSec > calculatedSpeed * 5:
            playerTotalElapsedSec %= calculatedSpeed * 5
            playerTotalElapsedSecPast = True

    elif playerInWater and playerMoveDirection == -1:
        if playerTotalElapsedSec > calculatedSpeed / 3:
            playerTotalElapsedSec %= calculatedSpeed / 3
            playerTotalElapsedSecPast = True

    elif not playerInWater and (playerMoveDirection == 1 or playerMoveDirection == -1):
        if playerTotalElapsedSec > calculatedSpeed:
            playerTotalElapsedSec %= calculatedSpeed
            playerTotalElapsedSecPast = True

    if not pause and canPlayerMove and playerTotalElapsedSecPast:
        if playerMoveDirection != 0:
            if playerMoveDirection == 1 and playerPosition + stepSize < maxPixel:
                playerPosition = playerPosition + stepSize
                # pixels[playerPosition - stepSize] = (0, 0, 0)

            if playerMoveDirection == -1 and playerPosition - stepSize >= minPixel:
                playerPosition = playerPosition - stepSize
                # pixels[playerPosition + stepSize] = (0, 0, 0)

            for enemy in enemies:
                if enemy[2] == playerPosition:
                    playerPosition = playerPosition - stepSize
        #pixels[playerPosition] = playerCurrentColor
        

def finish():
    global playerPosition
    global pause
    global isFinished

    if playerPosition == finishPosition - 1 or playerPosition == finishPosition + 1:
        pause = True
        isFinished = True
        for i in range(maxPixel):
            pixels[i] = playerCurrentColor
        for i in range(maxPixel):
            pixels[i] = [0, 0, 0]
        playerPosition = 0


def rounds():
    global playerPosition
    global round
    global isFinished
    global pause
    global enemies
    global water

    if isFinished:
        round += 1
        isFinished = False
        pause = False
        playerPosition = 1
        pixels[playerPosition] = playerCurrentColor
        pixels[finishPosition] = finishColor
        del enemies[:]
        del water[:]

        if round == 1:
            enemies.append([5, 0.2, 40])
            enemies.append([2, 0.2, 45])
            water.append([60, 12]) # [startpunt, lengte]
        elif round == 2:
            enemies.append([5, 0.2, 40])
            enemies.append([2, 0.2, 45])
            enemies.append([5, 0.2, 50])
            enemies.append([2, 0.2, 55])


def moveEnemies():
    global enemies
    global playerPosition
    global enemyColor
    global pause
    movementSpeed = 0.5  # movement speed of the enemies, it's been calculated with 0.1 / movementSpeed at the end

    # go over the list of enemies and playerMoveDirection them x amount of positions ever y seconds
    if not pause:
        for enemy in range(len(enemies)):
            if playerPosition > enemies[enemy][2] and playerPosition != enemies[enemy][2] + 1 and enemies[enemy][2] != enemyDeadPosition:
                enemies[enemy][2] = calculatePosition(1, enemies[enemy][2])
            elif playerPosition < enemies[enemy][2] and playerPosition != enemies[enemy][2] - 1 and enemies[enemy][2] != enemyDeadPosition:
                enemies[enemy][2] = calculatePosition(-1, enemies[enemy][2])

    time.sleep(0.1 / movementSpeed)


def calculatePosition(steps, position):
    global enemyColor
    #prefPos = position # Get the position from now and safes it as the old position
    if (position + steps) < 0:
        position = 0
    elif (position + steps) > num_pixels - 1:
        position = num_pixels - 1
    else:
        position += steps
        #pixels[prefPos] = [0, 0, 0]
        #pixels[position] = addColor(pixels[position], enemyColor)
        # print("new color: (", newRed, ",", newGreen, ",", newBlue, ")")
    return position


def hitDetection():
    global playerPosition
    global canPlayerMove
    global playerTotalLives
    global playerCurrentLives
    global playerCurrentColor
    pushbackDistance = 10

    for enemy in enemies:
        if enemy[2] - 1 == playerPosition:
            canPlayerMove = False
            playerCurrentLives -= 1
            playerCurrentColor = multiplyColor(divideColor(playerCurrentColor, playerTotalLives), playerCurrentLives)
            # print(playerCurrentColor)

            # print("Damaged player front")
            for i in range(pushbackDistance):
                pixels[playerPosition] = subtractColor(playerCurrentColor, pixels[playerPosition])
                playerPosition = playerPosition - 1
                pixels[playerPosition] = addColor(playerCurrentColor, pixels[playerPosition])     
            canPlayerMove = True
        elif enemy[2] + 1 == playerPosition:
            canPlayerMove = False
            playerCurrentLives -= 1
            playerCurrentColor = multiplyColor(divideColor(playerCurrentColor, playerTotalLives), playerCurrentLives)

            # print("Damaged player back")
            for i in range(pushbackDistance):
                pixels[playerPosition] = subtractColor(playerCurrentColor, pixels[playerPosition])
                playerPosition = playerPosition + 1
                pixels[playerPosition] = addColor(playerCurrentColor, pixels[playerPosition])
            canPlayerMove = True


def attack():
    global attackPositionPos
    global attackPositionNeg
    global canPlayerMove
    canPlayerMove = False
    x = 0
    for en in enemies:
        # if en[2] - attackRange < playerPosition < en[2] + attackRange:
        if en[2] - attackRange < playerPosition:
            en[2] = enemyDeadPosition

    while x < attackRange:
        x += 1
        if playerPosition + x >= maxPixel:
            attackPositionPos = maxPixel - 1
        elif playerPosition - x < minPixel:
            attackPositionNeg = minPixel
        else:
            attackPositionPos = playerPosition + x
            attackPositionNeg = playerPosition - x
        time.sleep(0.01)
    time.sleep(0.1)
    attackPositionPos = 0
    attackPositionNeg = 0
    canPlayerMove = True


def drawAttack():
    if attackPositionPos != 0:
        pixels[attackPositionPos] = (0, 120, 250)
        # pixels[attackPositionNeg] = (0, 120, 250)


def playerDeath():
    global pause
    global round
    global playerCurrentLives
    global playerTotalLives
    global playerCurrentColor
    global playerStartColor
    global isFinished

    playerCurrentLives = playerTotalLives
    pause = True
    round = 0
    isFinished = True
    pixels.fill((255, 0, 0))
    time.sleep(0.5)
    pixels.fill((0, 0, 0))
    time.sleep(0.5)

    pixels.fill((255, 0, 0))
    time.sleep(0.5)
    pixels.fill((0, 0, 0))
    time.sleep(0.5)
    
    pixels.fill((255, 0, 0))
    time.sleep(0.5)
    pixels.fill((0, 0, 0))
    time.sleep(0.5)
    playerCurrentColor = playerStartColor


def drawEnemies():
    for enemy in enemies:
        if enemy[2] != enemyDeadPosition:
            pixels[enemy[2]] = enemyColor


def th1(naam):
    global playerCurrentLives
    global pixels
    elapsedSec = 0
    while True:
        startTime = time.time()
        
        inWater()
        movePlayer(elapsedSec)
        finish()
        
        if playerCurrentLives == 0:
            playerDeath()
        
        rounds()
        elapsedSec = time.time() - startTime


def th2(naam):
    while True:
        moveEnemies()
        hitDetection()


def th3(naam):
    while True:
        pixels.fill((0, 0, 0))
        drawWater()
        drawAttack()
        pixels[playerPosition] = playerCurrentColor
        pixels[finishPosition] = finishColor
        drawEnemies()

        pixels.show()


_thread.start_new_thread(th1, ("UpdatePlayer",))
_thread.start_new_thread(th2, ("UpdateEnemies",))
_thread.start_new_thread(th3, ("Draw",))

for event in gamepad.read_loop():
    if event.type == 3:  # A stick is moved
        if event.code == 17:  # up and down arrow
            if event.value == 1:
                # print('down')
                playerMoveDirection = -1
            elif event.value == -1:
                # print('up')
                playerMoveDirection = 1
            else:
                playerMoveDirection = 0

        # if event.code == 16:  # left and right arrows
        #     if event.value == 1:
        #         print('right')
        #     if event.value == -1:
        #         print('left')

    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            if event.code == cross:
                attack()
            # elif event.code == circle:
            #     print("circle")
            # elif event.code == triangle:
            #     print("triangle")
            # elif event.code == square:
            #     print("square")