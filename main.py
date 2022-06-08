import pyautogui
import csv
import random
from random import randrange
from random import uniform
import time

#   https://www.zillow.com/homes/for_sale/house_type/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22west%22%3A-96.05292561737528%2C%22east%22%3A-95.85208180634012%2C%22south%22%3A30.178543182514066%2C%22north%22%3A30.29748398165441%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sch%22%3A%7B%22value%22%3Afalse%7D%2C%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A13%7D

# print(pyautogui.size())
# print(pyautogui.position())

def sleep(seconds=randrange(3, 5)):
    time.sleep(seconds)

def shortSleep():
    time.sleep(uniform(0.1, 0.5))

def longSleep():
    time.sleep(randrange(5, 7))

def searchZip():
    pyautogui.moveTo(100, 205)
    shortSleep()
    pyautogui.click()
    shortSleep()
    pyautogui.press('backspace', presses=5)
    shortSleep()
    pyautogui.typewrite(zip)
    shortSleep()
    pyautogui.press('return')
    longSleep()

def moveMapAroundCurrentRegion():
    pyautogui.moveTo(randrange(580, 620), randrange(580, 620), duration=uniform(0.01, 1))
    pyautogui.scroll(200)
    pyautogui.scroll(200)
    sleep()
    moveMap('up')
    moveMap('right')
    moveMap('down')
    moveMap('down')
    moveMap('left')
    moveMap('left')
    moveMap('up')
    moveMap('up')


def moveMap(direction="up"):
    pyautogui.moveTo(randrange(580, 620), randrange(580, 620))
    shortSleep()
    PRIMARY = (450, 500)
    SECONDARY = (-20, 20)
    if (direction == 'up'):
        pyautogui.dragRel(randrange(SECONDARY[0], SECONDARY[1]), randrange(PRIMARY[0], PRIMARY[1]), button="right", duration=uniform(0.7, 1))
    elif(direction == 'down'):
        pyautogui.dragRel(randrange(SECONDARY[0], SECONDARY[1]), randrange(-PRIMARY[1], -PRIMARY[0]), button="right", duration=uniform(0.7, 1))
    elif(direction == 'right'):
        pyautogui.dragRel(randrange(-PRIMARY[1], -PRIMARY[0]), randrange(SECONDARY[0], SECONDARY[1]), button="right", duration=uniform(0.7, 1))
    elif(direction == 'left'):
        pyautogui.dragRel(randrange(PRIMARY[0], PRIMARY[1]), randrange(SECONDARY[0], SECONDARY[1]), button="right", duration=uniform(0.7, 1))
    shortSleep()

def mapCrawler(screenLengths):
    for row in range(20):
        for col in range(screenLengths):
            if (row % 2 == 0):
                moveMap('right')
            else:
                moveMap('left')
            print(f'{row}, {col}')
        moveMap('down')





zipcodes = []
with open('zipcodes.tsv', 'r') as tsvin:
    for zip in csv.reader(tsvin, delimiter='\t'):
        zipcodes.append(zip[0])
random.shuffle(zipcodes)

for zip in zipcodes:
    # searchZip()
    # moveMapAroundCurrentRegion()
    mapCrawler(50)



