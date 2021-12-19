#!/usr/bin/env python3
# coding=utf8
from ppadb.client import Client
from PIL import Image
import numpy
import time
import threading, queue
import yagmail
import random
from twocaptcha import TwoCaptcha
import requests

try:
    import winsound
except ImportError:
    import os
    def playsound(frequency,duration):
					print("\a")
else:
    def playsound(frequency,duration):
					winsound.Beep(frequency,duration)

import pytesseract as tess
from sys import platform
tess.pytesseract.tesseract_cmd = r"C:\Users\Daniel\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
if platform == "win32":
    tess.pytesseract.tesseract_cmd = r'C:\Users\Daniel\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
else:
    tess.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

from difflib import SequenceMatcher
import time
import cv2
from random import randrange
import tkinter as tk
import sys
import imagehash
import os
from os import system
import matplotlib.pyplot as plt
from scipy import ndimage
import pprint
import webbrowser
import pyautogui
#Create folder if doesnt exist
try:
    os.makedirs('screenshots')
except OSError as e:
    print("")

#relative path so .exe works in every computer
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

os.system("")

#text colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# beep = help pressed
# boop = 1st attack
# boop boop = new Attack
# boop beep = healing
# beep boop beep = sending email

# Global Vars
inReset = False
inAttack = False
inFarm = False
updateRunning = False
inEmail = False
inTap = False
questionEnded = False
lookingForQuestion = False
updating = False

imageG = numpy.zeros((1080, 1920, 4)) #default image holder
clarionCall = False
midTerm=False

nHelps = 0
nIterations = 0

obj1LastXPixel=0
obj2LastXPixel=0
obj1FirstXPixel=0
obj2FirstXPixel=0

xRes = 1920
yRes = 1080

getTextFromImageQueue=queue.Queue() #queue storing values from threads (equivalent to a queue of return var from functions)

adb = Client(host='localhost', port=5037)
devices = adb.devices()
if len(devices) == 0:
    print('no device attached')
    quit()

#Prolly a good idea to have only 1 device while running this
device = devices[0]

#0 to 1 rate of how similar a is to b
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

#screenshots whole screen and cuts the part where theres the captcha and its info to a png
def screenshotOfCaptcha():
	xLocal=0
	yLocal=0
	image = device.screencap() #take screenshot
	with open(resource_path('captchaDirty.png'), 'wb') as f:
		f.write(image)
	image = Image.open(resource_path('captchaDirty.png'))
	image = numpy.array(image, dtype=numpy.uint8) #get screenshot data in rgba

	xTotalPixels = round((0.66 - 0.34) * xRes)
	#print(xTotalPixels)
	yTotalPixels = round((0.87 - 0.125) * yRes)
	#print(round(0.95*xRes)-10)
	newImage = numpy.zeros((yTotalPixels+10, xTotalPixels+10, 4)) #newImage is the same kind of array of the screenshot's data
	for x in range(round(0.34*xRes), round(0.66*xRes)-10):
		xLocal+=1
		yLocal=0
		for y in range(round(0.125*yRes), round(0.87*yRes)-10):
			yLocal+=1
			#print(xLocal, ",", yLocal, " = ",image[y][x])
			newImage[yLocal][xLocal] = image[y][x]
	#saving new image with the dimensions and content of the captcha inside the screenshot
	newImage = numpy.array(newImage, dtype=numpy.uint8)
	im = Image.fromarray(newImage)
	randomN = randrange(20)
	im = im.resize((450, 580), Image.ANTIALIAS)
	ran= "captcha.png"
	#print(ran)
	im.save(resource_path(ran))
	return

#opens the captcha png and its info to extract the objects needed to a png
def captchaToObjects():
	global obj1FirstXPixel
	global obj1LastXPixel
	global obj2FirstXPixel
	global obj2LastXPixel
	global lookingForQuestion
	obj1FirstXPixel=0
	obj1LastXPixel=0
	obj2FirstXPixel=0
	obj2LastXPixel=0
	xLocal=0
	yLocal=0

	image = Image.open(resource_path('captcha.png'))
	image = numpy.array(image, dtype=numpy.uint8)

	#dimensions of the objects location (static at the momment)
	xTotalPixels = round(449 - 210)
	yTotalPixels = round(72-2)

	blackOnce = False

	#print("------------------------------")
	newImage = numpy.zeros((yTotalPixels+2, xTotalPixels+2, 4)) #image of the objects "placeholder"
	#populate newImage with the pixels of the objects from captcha while also checking if theres only 2 objects
	for x in range(210, 410):
		xLocal+=1
		yLocal=0
		onWhite=True
		#print(newImage[35][xLocal-1][0])
		if (xLocal-1>2):
			#print(newImage[30][xLocal-1][0])
			if (newImage[30][xLocal-1][0]>250):
				#print("white",xLocal-1)
				if (obj1FirstXPixel != 0 and obj1LastXPixel == 0):
					#print("ob1 ends")
					obj1LastXPixel=xLocal-1
				if(obj2FirstXPixel != 0 and obj2LastXPixel ==0):
					#print("ob2 ends")
					obj2LastXPixel=xLocal-1
			if (newImage[30][xLocal-1][0]<50):
				#print("black ",xLocal-1)
				if (obj1FirstXPixel == 0):
					#print("ob1 starts")
					obj1FirstXPixel=xLocal-1
				if (blackOnce == True and newImage[35][xLocal-1][0] != 0.0):
					#print("ob3 starts") #ob3 start, therefore theres more than 2 objects, re-roll the captcha to find an easier one
					print("looks like there are too many objects, re-rolling...")
					tap(.16,.85)
					tap(.50,.65)
					time.sleep(6)
					lookingForQuestion = True
					return
				if (obj2LastXPixel != 0):
					blackOnce = True
				if (obj1LastXPixel != 0 and obj2FirstXPixel == 0):
					#print("ob2 comeca")
					obj2FirstXPixel = xLocal-1
		for y in range(2, 72):
			yLocal+=1
			#print(xLocal, ",", yLocal, " = ",image[y][x])
			newImage[yLocal][xLocal] = image[y][x]

	#config image with objects and save it
	newImage = numpy.array(newImage, dtype=numpy.uint8)
	im = Image.fromarray(newImage)
	randomN = randrange(20)
	ran= "ob1and2.png"
	im.save(resource_path(ran))

	#usually each image is cropped too thin, so i give it a little room
	obj1LastXPixel = obj1LastXPixel+15
	obj2LastXPixel = obj2LastXPixel+15
	obj1FirstXPixel = obj1FirstXPixel-15
	obj2FirstXPixel = obj2FirstXPixel-15
	return


#get individual image of one object from the image with the objects
def getObj(objN):

	image = Image.open(resource_path('ob1and2.png'))
	image = numpy.array(image, dtype=numpy.uint8) #get data in rgba

	#obj Y is always the same but X depends on the values found in captchaToObjects()
	if(objN == "1"):
		xTotalPixels = round(obj1LastXPixel - obj1FirstXPixel)
	else:
		xTotalPixels = round(obj2LastXPixel - obj2FirstXPixel)
	yTotalPixels = round(50)
	xLocal=0
	yLocal=0
	newImage = numpy.zeros((yTotalPixels+2, xTotalPixels+2, 4)) #image of the object "placeholder"
	#populate new image with the right dimensions and pixels of each object from the ob1and2.png
	if(objN == "1"):
		for x in range(obj1FirstXPixel, obj1LastXPixel):
			xLocal+=1
			yLocal=0
			for y in range(5, 55):
				yLocal+=1
				#print(xLocal, ",", yLocal, " = ",image[y][x])
				newImage[yLocal][xLocal] = image[y][x]
	else:
		for x in range(obj2FirstXPixel, obj2LastXPixel):
			xLocal+=1
			yLocal=0
			for y in range(5, 55):
				yLocal+=1
				#print(xLocal, ",", yLocal, " = ",image[y][x])
				newImage[yLocal][xLocal] = image[y][x]

	#config new obN.png
	newImage = numpy.array(newImage, dtype=numpy.uint8)
	im = Image.fromarray(newImage)
	randomN = randrange(20)
	ran= "ob"+objN+".png"
	#print(ran)
	im.save(resource_path(ran))
	return
#In order to get the best result possible, isolate the puzzle image from captcha from all its irrelevand info
def getPuzzleImageFromCaptcha():

	image = Image.open(resource_path('captcha.png'))
	image = numpy.array(image, dtype=numpy.uint8) #get data in rgba

	#image dimensions (static atm)
	xTotalPixels = round(440)
	yTotalPixels = round(500-75)

	xLocal=0
	yLocal=0
	newImage = numpy.zeros((yTotalPixels+2, xTotalPixels+2, 4)) #clean captcha image "placeholder"
	for x in range(0, 440):
		xLocal+=1
		yLocal=0
		for y in range(75, 500):
			yLocal+=1
			#print(xLocal, ",", yLocal, " = ",image[y][x])
			newImage[yLocal][xLocal] = image[y][x]

	#config captchaClean.png
	newImage = numpy.array(newImage, dtype=numpy.uint8)
	im = Image.fromarray(newImage)
	randomN = randrange(20)
	ran= "captchaClean.png"
	im.save(resource_path(ran))
	print("End of get puzzle")
	return

#algorithm where the match between the obN.png and the captchaClean.png is found
def findObj(objN,whiteBG):
	print("finobj begins")
	maxValue=0
	maxI=0
	maxj=0
	maxX=0
	px=0
	py=0

	tempres = []
	tempres.append(0)
	#try six different cv2.Threshold values (basically change contrast and light)
	for x in range(6):
		#print("X: "+str(x)+"/6")
		img = cv2.imread("captchaClean.png",0)
		retval, img = cv2.threshold(img, x*40,230, cv2.THRESH_TOZERO)
		img = cv2.resize(img,(100,100),fx=1.1,fy=1.1, interpolation=cv2.INTER_CUBIC)
		cv2.imwrite("screenshots/captcha.png",img)

		method = cv2.TM_SQDIFF_NORMED
		#print("ob"+objN+".png")
		template = cv2.imread("ob"+objN+".png", 0)
		#cv2.imshow('image', template)
		#every other X change from black and white to white and black, higher chance of success this way
		if x % 2 != 0:
			whiteBG = False
			template = cv2.bitwise_not(template)
		else:
			whiteBG = True

		#every 10 iterations make the obN bigger
		for i in range (10):
			if(i != 0):
				template = cv2.imread("template.png", 0)
			#cv2.imshow('image2', template)
			template = cv2.resize(template,(100,100),fx=1.1,fy=1.1, interpolation=cv2.INTER_CUBIC)

			#cv2.imshow('image', template)

			#every 36 iterations rotate objN 10º
			for j in range (36):
				img = cv2.imread('screenshots/captcha.png', 0)
				img2 = cv2.imread('screenshots/captcha.png', 1)
				#cv2.imshow('image2', img)
				template=rotate_image(template, 10,whiteBG)
				cv2.imwrite("template/tmpl"+str(i)+"angle"+str(j*10)+".png",template)

				w, h = template.shape[::-1]	#width and height of the template

				img3 = img2.copy()

				res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED) #result of the match between the template and the captchaClean using TM_CCOEFF_NORMED method
				
				if res[0][0] > 0.8:
					tempres.append(res[0][0])



				min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

				top_left = max_loc #coordinates of the top left corner of the match of the template within the captchaClean
				bottom_right = (top_left[0] + w, top_left[1] + h)

				cv2.rectangle(img2, top_left, bottom_right, (0, 255, 0), 2) #draw a rectangle on what seems the best match

				#every time theres a better match than the previously best match, update it and store it's max values
				if (numpy.amax(res) > maxValue):
					maxValue= numpy.amax(res)
					px=top_left[0]*1.3  + w # X position where ROKBOT has to tap (there has a resizing of the captcha, so it has to be resized here by 1.3)
					py=top_left[1]*1.3 + h # Y position where ROKBOT has to tap (there has a resizing of the captcha, so it has to be resized here by 1.3)
					maxI = i
					maxJ = j
					maxX = x
					cv2.imwrite("bestMatch"+objN+".png",img2)

	#once finished, tap the location with the best match
	#print(tempres)


	tap(((py)+(yRes*0.213))/yRes,((px)+(xRes*0.34))/xRes)

	print(((py)+(yRes*0.213))/yRes, " ",((px)+(xRes*0.34))/xRes)
	print(str(maxValue)+" "+str(maxI)+" "+str(maxJ)+" "+str(maxX))

	if tempres != [0]:
		print("captcha")
		return True
	else:
		print("no captcha")
		return False




#check if the tapped results give a success notification, if not, re-roll to new captcha

def checkCaptchaSuccess(whiteBG):
	print("here")
	image = device.screencap() #take screenshot
	with open(resource_path('resultCaptcha.png'), 'wb') as f:
		f.write(image)
	image = Image.open(resource_path('resultCaptcha.png'))
	image = numpy.array(image, dtype=numpy.uint8) #get screenshot data in rgba
	if (checkPixel(0.77,0.55,222,113,91,image) == True):
		#if (checkPixel(0.5194,0.6729,222,113,91,image) != True):
		tap(.16,.85)
		tap(.50,.65)
		time.sleep(6)
		testCaptcha(whiteBG)
	return

def testCaptcha(whiteBG):
	captcha = False
	global lookingForQuestion
	print("screenshoting captcha")
	screenshotOfCaptcha()
	print("Extracting objects from captcha")
	captchaToObjects()
	if (lookingForQuestion == True):
		lookingForQuestion = False
		testCaptcha(False)
		return
	print("Extracting object 1")
	getObj("1")
	print("Extracting object 2")
	getObj("2")
	print("Extracting image from captcha")
	getPuzzleImageFromCaptcha()
	print("Searching object 1 in image from captcha")
	captcha = findObj("1",whiteBG)
	#print("Searching object 2 in image from captcha")
	#findObj("2",whiteBG)
	if captcha == True:
		print("capthca spotted")
		screenshotOfCaptcha()
		time.sleep(1)
		SolveCaptcha()
		#captcha solver here

	tap(.8,.6)
	checkCaptchaSuccess(whiteBG)
	return
	"""tap(.16,.85)
	tap(.50,.65)
	time.sleep(6)
	lookingForQuestion = False
	testCaptcha(False)"""

def rotate_image(image, angle,whiteBG):
	image_center = tuple(numpy.array(image.shape[1::-1]) / 2)
	rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
	if (whiteBG == True):
		result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LANCZOS4, borderValue=(255,255,255))
	else:
		result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT)
	return result

#setting what the MAX R, G or B should be given a color value
def setMax(color):
	if(color >= 225):
		return (255)
	else:
		return (color + 25)

#setting what the MIN R, G or B should be given a color value
def setMin(color):
	if(color <= 25):
		return (0)
	else:
		return (color - 25)

#check if pixel color is within 25 units (positive or negative) in R G and B vectors
def checkPixel (yPos, xPos, colorR, colorG, colorB, image):
	colorRMax = setMax(colorR)
	colorRMin = setMin(colorR)

	colorGMax = setMax(colorG)
	colorGMin = setMin(colorG)

	colorBMax = setMax(colorB)
	colorBMin = setMin(colorB)

	if ((image[round(yPos*yRes)][round(xPos*xRes)][0] >= colorRMin and image[round(yPos*yRes)][round(xPos*xRes)][0] <= colorRMax) and (image[round(yPos*yRes)][round(xPos*xRes)][1] >= colorGMin and image[round(yPos*yRes)][round(xPos*xRes)][1] <= colorGMax) and (image[round(yPos*yRes)][round(xPos*xRes)][2] >= colorBMin and image[round(yPos*yRes)][round(xPos*xRes)][2] <= colorBMax)):
		return True



#Dynamic tap
def tap (yPos, xPos):
	global inTap
	inTap = True
	playsound(2500, 200)
	cmd = 'input touchscreen swipe '+ str(round(xPos*xRes))+ ' '+ str(round(yPos*yRes))+' '+ str(round(xPos*xRes))+' '+ str(round(yPos*yRes))+' 10 '
	print (cmd)
	device.shell(cmd)
	time.sleep(.1)
	inTap = False

#if there's a victory, find and attack new barb
def attack():
	global inAttack
	global inEmail

	print(" preparing attack")
	playsound(500, 200)
	time.sleep(0.1)
	playsound(500, 200)

	inAttack=True
	device.shell(f'input touchscreen swipe 50 820 50 820 200')#tap magnifying glass
	time.sleep(1)
	device.shell(f'input touchscreen swipe 400 750 400 750 10 ')#tap search button
	time.sleep(1)
	device.shell(f'input touchscreen swipe 960 540 960 540 100 ')#tap barb
	time.sleep(1)

	image = device.screencap() #take screenshot
	with open(resource_path('screen2.png'), 'wb') as f:
		f.write(image)
	image = Image.open(resource_path('screen2.png'))
	image = numpy.array(image, dtype=numpy.uint8) #get screenshot data in rgba

	#print(image[round(0.1343*yRes)][round(0.8692*xRes)], " ", checkPixel(0.1343,0.8692,230,0,0,image))
	if (checkPixel(0.66,0.66,230,60,50,image) == None): # if red attack button doesnt appear
		attack()
	if (checkPixel(0.66,0.66,230,60,50,image) == True):
		device.shell(f'input touchscreen swipe 1380 723 1380 723 100 ')#tap attack button
		time.sleep(1)
		device.shell(f'input touchscreen swipe 1830 320 1830 320 100 ') #tap army i want
		time.sleep(1)
		device.shell(f'input touchscreen swipe 1530 460 1530 460 100 ') #tap march button

		inAttack=False




#receives the coordinates of the beggining and end of X and Y in order to crop the screensho, framing only the text we want to extract
def getTextFromImage(xBeggining, xEnd, yBeggining, yEnd, isTitle):
	global imageG
	image = imageG
	xLocal=-1
	yLocal=-1
	xTotalPixels = round((xEnd - xBeggining) * xRes)
	yTotalPixels = round((yEnd - yBeggining) * yRes)

	newImage = numpy.zeros((yTotalPixels+10, xTotalPixels+10, 4)) #newImage is the same kind of array of the screenshot's data

	start = time.time()
	#copy every pixel's color in the given coordinates and paste them, in the respective order, in the newImage's data array, starting at 0
	for x in range(round(xBeggining*xRes), round(xEnd*xRes)):
		xLocal+=1
		yLocal=0
		for y in range(round(yBeggining*yRes), round(yEnd*yRes)):
			yLocal+=1
			#print(xLocal, ",", yLocal, " = ",image[y][x])
			newImage[yLocal][xLocal] = image[y][x]

	end = time.time()
	print("It took me: ", str(end - start), "s to crop image")
	start = time.time()
	#formating the newImage array to the screenshot's type
	newImage = numpy.array(newImage, dtype=numpy.uint8)
	im = Image.fromarray(newImage)
	randomN = randrange(20)
	ran= "screenshots/reading"+str(randomN)+ ".png"
	#print(ran)
	im.save(resource_path(ran))

	#now that we saved the cropped image with the text on it, we need to apply some filters, making it easier for tess to extract its string
	img = cv2.imread(resource_path(ran),0)
	# since the tittle color is black and the options is white, we need different values to filter it
	if (isTitle == True):
		retval, img = cv2.threshold(img, 140,90, cv2.THRESH_BINARY)
	if (isTitle == False):
		retval, img = cv2.threshold(img, 215,250, cv2.THRESH_BINARY)
		img = cv2.bitwise_not(img) #invert colors, so tess can read it black on white (other way around gives much more innacurate results)
	img = cv2.resize(img,(0,0),fx=3,fy=3, interpolation=cv2.INTER_CUBIC) #scaling up helps with accuracy
	#Blurring edges makes them less sharp, tess likes that
	img = cv2.GaussianBlur(img,(11,11),0)
	img = cv2.medianBlur(img,5)
	end = time.time()
	print("It took me: ", str(end - start), "s to edit the image")

	#cv2.imshow('asd',img)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()

	question = tess.image_to_string(img, lang='eng')
	getTextFromImageQueue.put(question.lower())



#receives an answer from chooseAnswer() and checks which option is the most similar
def searchOption(question,bestQuestion, answer,A,B,D,C):
	global questionEnded
	print(bcolors.WARNING  +"\nTrying: ",answer, "\n" + bcolors.ENDC)
	start = time.time()
	answers = similar(answer,A),similar(answer,B),similar(answer,C),similar(answer,D) #stores the rate of similarity (0.0 to 1.0) of each option vs answer on this array

	#searches for the biggest value (most similar option to its answer) and its id
	bestOption = answers[0]
	idBestOption = 0
	for i in range (4):
		print (i, " - ", answers[i])
		if (bestOption<answers[i]):
			bestOption = answers[i]
			idBestOption=i
	end = time.time()
	print("It took me: ", str(end - start), "s to find the best option")
	#if the best option isn't similar enough to the answer, then something went wrong, but the user can still click manually
	if (bestOption < .6):
		webbrowser.open('https://www.google.com/search?q='+question, new=2)
		print(bcolors.FAIL +"Im not sure which option is it, but the answer is either ",answer, " or check the google page I opened"+ bcolors.ENDC)
		questionEnded = True
	#if the best option is similar enough, tap it prgrammatically
	else:
		if (idBestOption == 0):
			print(bcolors.OKGREEN +"It's A - : ",A + bcolors.ENDC)
			threading.Thread(target=tap, args=[.48,.3]).start()
			questionEnded = True
		elif (idBestOption == 1):
			print(bcolors.OKGREEN +"It's: B - ",B + bcolors.ENDC)
			threading.Thread(target=tap, args=[.48,.7]).start()
			questionEnded = True
		elif (idBestOption == 2):
			print(bcolors.OKGREEN +"It's: C - ",C + bcolors.ENDC)
			threading.Thread(target=tap, args=[.61,.3]).start()
			questionEnded = True
		elif (idBestOption == 3):
			print(bcolors.OKGREEN +"It's: D - ",D + bcolors.ENDC)
			threading.Thread(target=tap, args=[.61,.7]).start()
			questionEnded = True
		else:
			print(bcolors.FAIL  +"ROKBOT didn't find an option found with this answer, check his tries, theres probably the right answer there, slightly different to the options in the display\n" + bcolors.ENDC)
			questionEnded = True
	print ("\n Thread Count: ", threading.active_count())
	print("\n ----------------------------------------------------------------------\n")


def lockQuestion():
	while (questionEnded == False):
		time.sleep(0.01)
		lockQuestion()

	return

def startCaptcha():
	start = time.time()
	tap(.2,.7)
	tap(.5,.6)
	time.sleep(1)
	testCaptcha(False)
	end = time.time()
	print("It took me: ", str(end - start), "s to find 1 object")

	tap(.9,.5)

	tap(0.1,0.1)

	time.sleep(.5)

	tap(0.1,0.1)



#not currently working
def checkIfInGame():
	time.sleep(1)
	if(device.shell("pidof com.lilithgame.roc.gp") == ""):
		device.shell("monkey -p com.lilithgame.roc.gp 1")
		#exec(open("rok.py").read())
		os.system("python rok.py")
		sys.exit("Error message")
	threading.Thread(target=checkIfInGame, args=[]).start()
	return

#multitouch try
def swipe(xStart,yStart,xEnd,yEnd):
	threading.Thread(target=swipeAux, args=[xEnd,yEnd]).start()
	cmd = 'input touchscreen swipe '+ str(round(xStart*0.01*xRes))+ ' '+ str(round(yStart*0.01*yRes))+' '+ str(round(xStart*0.01*xRes))+ ' '+ str(round(yStart*0.01*yRes))+' 500'
	device.shell(cmd)
	return

def swipeAux(xEnd,yEnd):
	time.sleep(0.2)
	cmd = 'input touchscreen swipe ' + str(round(xEnd)+150)+' '+ str(round(yEnd)+43)+ ' '+str(round(xEnd)+150)+' '+ str(round(yEnd)+43)+ ' 500'
	device.shell(cmd)
	return

def startPuzzle():

	img = cv2.imread('completedPuzzle.png', 0)
	img2 = cv2.imread('completedPuzzle.png', 1)
	#position of the area of puzzle piece we want to search
	xEnd = .8755
	xBeggining = .8469
	yEnd = .16
	yBeggining = .114

	for i in range(35):
		start = time.time()
		image = device.screencap() #take screenshot
		#35 puzzle pieces, search for each piece in the puzzleCompleted.png
		with open(resource_path('puzzleGame.png'), 'wb') as f:
			f.write(image)

		image = Image.open(resource_path('screengt2.png'))
		image = numpy.array(image, dtype=numpy.uint8) #get screenshot data in rgba
		xLocal=-1
		yLocal=-1
		xTotalPixels = round((xEnd - xBeggining) * xRes)
		yTotalPixels = round((yEnd - yBeggining) * yRes)

		newImage = numpy.zeros((yTotalPixels, xTotalPixels, 4)) #newImage is the same kind of array of the screenshot's data


		#copy every pixel's color in the given coordinates and paste them, in the respective order, in the newImage's data array, starting at 0
		for x in range(round(xBeggining*xRes), round(xEnd*xRes)-1):
			xLocal+=1
			yLocal=0
			for y in range(round(yBeggining*yRes), round(yEnd*yRes)-1):
				yLocal+=1
				#print(xLocal, ",", yLocal, " = ",image[y][x])
				newImage[yLocal][xLocal] = image[y][x]

		#formating the newImage array to the screenshot's type
		newImage = numpy.array(newImage, dtype=numpy.uint8)
		im = Image.fromarray(newImage)
		ran= "piece"+str(i)+ ".png"
		#print(ran)
		im.save(resource_path(ran))

		#35 puzzle pieces, search for each piece in the puzzleCompleted.png
		template = cv2.imread('piece'+str(i)+'.png', 0)
		template = cv2.resize(template,(0,0),fx=1.49,fy=1.49, interpolation=cv2.INTER_LINEAR)
		cv2.imwrite(resource_path(ran),template)
		w, h = template.shape[::-1]	#width and height of the template

		res = cv2.matchTemplate(img,template,cv2.TM_CCORR_NORMED) #result of the match between the template and the completedPuzzle using TM_CCORR_NORMED method
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

		top_left = max_loc[0], max_loc[1] #coordinates of the top left corner of the match of the template within the captchaClean
		bottom_right = (top_left[0] + (w), top_left[1]+ (h))
		cv2.rectangle(img, top_left, bottom_right, (0, 255, 255), -1) #draw a rectangle on what seems the best match
		px=round((top_left[0]+bottom_right[0])/2)
		py=round((top_left[1]+bottom_right[1])/2)

		# Show the final image with the matched area.
		cv2.imshow('Detected',img)
		cv2.imshow('template',template)
		cv2.waitKey(100)
		#here i attempt to use multitouch in adb (that way i could, theoretically, call an input swipe and a tap at the same time to place the piece in the right position, that way i didn't have to place the piece with the swipe, which has a sort of "ruberband" animation, which produces innacurate placements of the pieces, once it travels to fast)
		threading.Thread(target=swipe, args=[86,14,px,py]).start()
		time.sleep(0.7)
		end = time.time()

		print("It took me: ", str(end - start), "s to find 1 object")


def attackMarauder():
	cmd = 'input touchscreen swipe  800 500 850 500 500'
	device.shell(cmd)
	tap(.5,.5) #tap marauder
	tap(.6,.3) #tap attack Button
	tap(.20,.80) #tap new troops button
	tap(.9,.75) #tap march button

def zoomOut():
	pyautogui.keyDown('down')
	time.sleep(0.5)
	pyautogui.keyUp('down')

def makeTroops():
	tap(.06,.25) #barraks
	tap(.2,.5) #button troops
	cmd = 'input text 592'
	device.shell(cmd)

	tap(.2,.6)
	tap(.2,.6)
	cmd = 'input text 311'
	device.shell(cmd)

	tap(.2,.7)
	tap(.2,.7)


def getImagePls():
	for i in range (10000):
		xEnd = .13
		xBeggining = .06
		yEnd = .905
		yBeggining = .875
		image = device.screencap() #take screenshot
		with open(resource_path('screenPls.png'), 'wb') as f:
			f.write(image)

		image = Image.open(resource_path('screenPls.png'))
		image = numpy.array(image, dtype=numpy.uint8) #get screenshot data in rgba
		xLocal=-1
		yLocal=-1
		xTotalPixels = round((xEnd - xBeggining) * xRes)
		yTotalPixels = round((yEnd - yBeggining) * yRes)

		newImage = numpy.zeros((yTotalPixels, xTotalPixels, 4)) #newImage is the same kind of array of the screenshot's data


		#copy every pixel's color in the given coordinates and paste them, in the respective order, in the newImage's data array, starting at 0
		for x in range(round(xBeggining*xRes), round(xEnd*xRes)-1):
			xLocal+=1
			yLocal=0
			for y in range(round(yBeggining*yRes), round(yEnd*yRes)-1):
				yLocal+=1
				print(xLocal, ",", yLocal, " = ",image[y][x])
				newImage[yLocal][xLocal] = image[y][x]

		#formating the newImage array to the screenshot's type
		newImage = numpy.array(newImage, dtype=numpy.uint8)
		im = Image.fromarray(newImage)
		ran= "screenPlsClean.png"
		#print(ran)
		im.save(resource_path(ran))
		img = cv2.imread(resource_path(ran),0)
		retval, img = cv2.threshold(img, 215,250, cv2.THRESH_BINARY)
		img = cv2.bitwise_not(img) #invert colors, so tess can read it black on white (other way around gives much more innacurate results)
		img = cv2.resize(img,(0,0),fx=3,fy=3, interpolation=cv2.INTER_CUBIC) #scaling up helps with accuracy
		#Blurring edges makes them less sharp, tess likes that
		img = cv2.GaussianBlur(img,(11,11),0)
		img = cv2.medianBlur(img,5)
		cv2.imshow('template',img)
		cv2.waitKey(1)
		#cv2.imshow('asd',img)
		#cv2.waitKey(0)
		#cv2.destroyAllWindows()
		content = tess.image_to_string(img, lang='eng')
		print(content)
		if ("pls"  in content.lower() or "plz"  in content.lower() or "please"  in content.lower()):
			print("oi")
			device.shell(f'input touchscreen swipe 300 600 300 500 500')  #tap city
			tap(.65,.10)
			#do stuff
			time.sleep(10)
			tap(.95,.115)
		else:
			device.shell(f'input touchscreen swipe 300 600 300 570 500')  #tap city
		#time.sleep(2)
		"""if ("pls" or "plz" or "please" in content.lower()):
			tap(.75,.10)
			#do stuff
			time.sleep(10)
			tap(.95,.115)"""
#every 1s take a screenshot and analyse it

def SolveCaptcha():
	i = 0
	print("lol")
	url = 'http://2captcha.com/in.php'
	files = {'file' : open('captcha.png', 'rb')}
	data = {'key': '090b372ea0fa1e8d50659047ae9c3646', 'method' : 'post'}
	r = requests.post(url, files=files, data=data) 

	time.sleep(200)

	while(not r.ok):
		time.sleep(5)
		i= i + 1
		print("i = {}".format(i))

	print(r)



#graphical interface initializations
window = tk.Tk()
getImagePlsBtn = tk.Button(text="getImagePls", command=getImagePls)
getImagePlsBtn.pack()
makeTroopsBtn = tk.Button(text="Givetitle", command=makeTroops)
makeTroopsBtn.pack()
startCaptchaBtn = tk.Button(text="Captcha", command=startCaptcha)
startCaptchaBtn.pack()
window.mainloop()
