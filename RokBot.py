import queue
import time
import threading
import Title_Order
from ppadb.client import Client
from PIL import Image
import numpy
from twocaptcha import TwoCaptcha
import os
import sys
from random import randrange
import cv2

class RokBot:

  api_key = os.getenv('APIKEY_2CAPTCHA', '2b744fbb13dd4685311c2ca09f472acf')
  solver = TwoCaptcha(api_key, defaultTimeout=120, pollingInterval=5)

  xRes = 1920
  yRes = 1080

  getTextFromImageQueue=queue.Queue()

  adb = Client(host='localhost', port=5037)
  devices = adb.devices()
  device = devices[0]

  inTap = False
  lookingForCaptcha = False
  isProcessingTitle = False

  def __init__(self):
    
    self.queue = queue.Queue()
    threading.Thread(target=self.captchaSolver, daemon=True).start()

  def start(self):
    if len(self.devices) == 0:
      print('no device attached')
      quit()

    os.system("")

    while True:
      order = self.queue.get()
      self.log('Task received.')
      self.processRequest(order)
      self.queue.task_done()

  def processRequest(self, order):

    self.log(f'Giving title {order.title} to user {order.orderer}')

    while self.lookingForCaptcha:
        time.sleep(1)

    self.isProcessingTitle = True
    success = False
    check = False
    i=0
    Xtitle = 0
    Ytitle = 0


    # Search coords
    self.tap(.06,.25) 
    self.tap(.2,.5)
    X = int(order.X)
    X = X + 1

    cmd = 'input text ' + str(X)
    self.device.shell(cmd)

    self.tap(.2,.6)
    self.tap(.2,.6)
    
    cmd = 'input text ' + order.Y
    self.device.shell(cmd)

    self.tap(.2,.7)
    self.tap(.2,.7)

    time.sleep(1) #delay so map has time to move


    while check == False:

      if i == 0:
        print("try tap city 1")
        self.tap(0.484,0.426)
      
      if i == 1:
        print("try 2")
        self.tap(0.526,0.426)

      if i == 2:
        print("try 3")
        self.tap(0.526,0.485)

      if i == 3:
        print("try 4")
        self.tap(0.526,0.367)

      if i == 4:
        print("try 5")
        self.tap(0.484,0.485)

      if i == 5:
        print("try 6")
        self.tap(0.484,0.367)

      if i == 6:
        print("try 7")
        self.tap(0.432,0.367)   

      if i == 7:
        print("try 8")
        self.tap(0.484,0.426) 

      if i == 8:
        print("try 9")
        self.tap(0.484,0.485) 
      
      i = i + 1

      time.sleep(0.5)

      self.Screenshot()

      time.sleep(0.5)

      check, Xtitle, Ytitle = self.CheckCity()

  
      if i == 9:
        print("Fail")
        check = True


    if i != 9:
      print("success")

    Xtap = (Xtitle-554)/(1690)
    Ytap = (Ytitle-554)/(1690)
    self.tap(Ytap,Xtap)

    self.giveTitle(order)

    self.tap(0.895,0.5)

    self.tap(0.1,0.1)

    time.sleep(1)

    self.tap(0.95,0.95)
    
    self.log('Request finished')

    self.isProcessingTitle = False

  def log(self, message):
    prefix = 'RoK Bot: '
    print(prefix + message)
  
  # This function is supose to run in another thread. It is a infine loop 
  # with 7.5min (450 seconds) interval (configurable).
  def captchaSolver(self, interval=450):
    time.sleep(10)
    while True:
      while self.isProcessingTitle:
        time.sleep(1)
      self.startCaptcha()
      time.sleep(interval)

      self.lookingForCaptcha = False




  def giveTitle(self,order):
    if order.title == "justice":
      print("justice")
      self.tap(0.545,0.23) #Justice coord
    if order.title == "duke":
      print("duke")
      self.tap(0.545,0.41) #Duke
    if order.title == "architect":
      print("architect")
      self.tap(0.545,0.58) #Architect
    if order.title == "scientist":
      print("scientist")
      self.tap(0.545,0.763) #Scinetist

    self.tap(0.895,0.5)

  def resource_path(self,relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

  def Screenshot(self):
    image = self.device.screencap()
    with open(self.resource_path('Citycheck.png'), 'wb') as f:
      f.write(image)
    return

  def CheckCity(self):

    method = cv2.TM_SQDIFF_NORMED

    image = cv2.imread('Citycheck.png')

    template = cv2.imread('Citymatch.png')

    result = cv2.matchTemplate(image, template, method)

    mn,_,mnLoc,_ = cv2.minMaxLoc(result)

    MPx,MPy = mnLoc

    trows,tcols = template.shape[:2]

    cv2.rectangle(image, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)

 

    crop_img1 = image[MPy:MPy+trows,MPx:MPx+tcols]

    res = cv2.matchTemplate(crop_img1,template,cv2.TM_CCOEFF_NORMED)


    if res[0][0] > 0.8:
      print("success")
      return True,MPx+tcols,MPy+trows

    else:
      print("fail")
      return False, 0, 0


  #screenshots whole screen and cuts the part where theres the captcha and its info to a png. Also saves a copy as JPG for capthca solving service (png too big)
  def screenshotOfCaptcha(self):
    xLocal=0
    yLocal=0
    image = self.device.screencap()
    with open(self.resource_path('captchaDirty.png'), 'wb') as f:
      f.write(image)
    image = Image.open(self.resource_path('captchaDirty.png'))
    image = numpy.array(image, dtype=numpy.uint8) #get screenshot data in rgba

    xTotalPixels = round((0.66 - 0.34) * self.xRes)
    yTotalPixels = round((0.87 - 0.125) * self.yRes)

    newImage = numpy.zeros((yTotalPixels+10, xTotalPixels+10, 4)) #newImage is the same kind of array of the screenshot's data

    for x in range(round(0.34*self.xRes), round(0.66*self.xRes)-10):
        xLocal+=1
        yLocal=0
        for y in range(round(0.125*self.yRes), round(0.87*self.yRes)-10):
          yLocal+=1
          newImage[yLocal][xLocal] = image[y][x]

    newImage = numpy.array(newImage, dtype=numpy.uint8)
    im = Image.fromarray(newImage)
    randomN = randrange(20)
    im = im.resize((450, 580), Image.ANTIALIAS)
    ran = "captcha.png"

    im.save(self.resource_path(ran))

    im1 = Image.open('captcha.png')
    rgb_im = im1.convert('RGB')
    rgb_im.save('2captcha.jpg')

    return



  #In order to get the best result possible, isolate the puzzle image from captcha from all its irrelevand info
  def getPuzzleImageFromCaptcha(self):
      image = Image.open(self.resource_path('captcha.png'))
      image = numpy.array(image, dtype=numpy.uint8) #get data in rgba
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
          newImage[yLocal][xLocal] = image[y][x]

      newImage = numpy.array(newImage, dtype=numpy.uint8)
      im = Image.fromarray(newImage)
      ran= "captchaClean.png"
      im.save(self.resource_path(ran))
      print("End of get puzzle")
      return

  #Dynamic tap
  def tap (self,yPos, xPos):
    self.inTap = True
	
    cmd = 'input touchscreen swipe '+ str(round(xPos*self.xRes))+ ' '+ str(round(yPos*self.yRes))+' '+ str(round(xPos*self.xRes))+' '+ str(round(yPos*self.yRes))+' 10 '
    #print (cmd)
    self.device.shell(cmd)
    time.sleep(.1)
    self.inTap = False

  #used to convert coords from 2captcha to bot
  def mathman(self,X,Y):
    Xr = 0.365+(0.635-0.365)*((X-30)/(360))
    Yr = 0.4+(0.87-0.4)*((Y-210)/(540-210))-0.008
    return Xr, Yr

  #kinda stuck in the code, needs to be surgically removed
  def rotate_image(self,image, angle,whiteBG):
    image_center = tuple(numpy.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    if (whiteBG == True):
      result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LANCZOS4, borderValue=(255,255,255))
    else:
      result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT)
    return result

  #returns True if captcha is found in the screenshot
  def findObj(self,whiteBG):
    print("finobj begins")
    maxValue=0
    tempres = []
    tempres.append(0)

    for x in range(6):
      img = cv2.imread("captchaClean.png",0)
      img = cv2.resize(img,(100,100),fx=1.1,fy=1.1, interpolation=cv2.INTER_CUBIC)
      cv2.imwrite("screenshots/captcha.png",img)
      template = cv2.imread("Template.png", 0)

      if x % 2 != 0:
        whiteBG = False
        template = cv2.bitwise_not(template)
      else:
        whiteBG = True    

      for i in range (10):
        if(i != 0):
          template = cv2.imread("template.png", 0)
        template = cv2.resize(template,(100,100),fx=1.1,fy=1.1, interpolation=cv2.INTER_CUBIC)

        for j in range (36):
          img = cv2.imread('screenshots/captcha.png', 0)
          img2 = cv2.imread('screenshots/captcha.png', 1)
          template=self.rotate_image(template, 10,whiteBG)

          cv2.imwrite("template/tmpl"+str(i)+"angle"+str(j*10)+".png",template)
    
          w, h = template.shape[::-1]	#width and height of the template

          res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED) #result of the match between the template and the captchaClean using TM_CCOEFF_NORMED method

          if res[0][0] > 0.8:
            tempres.append(res[0][0])
        
          min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

          top_left = max_loc #coordinates of the top left corner of the match of the template within the captchaClean
          bottom_right = (top_left[0] + w, top_left[1] + h)

          cv2.rectangle(img2, top_left, bottom_right, (0, 255, 0), 2) #draw a rectangle on what seems the best match

    if tempres != [0]:
      print("captcha")
      return True
    else:
      print("no captcha")
      return False

  #Basically a copy of findObj. Needs to be surgically removed from code and use one of the with filename parameter.
  def Check(self,whiteBG):
    maxValue=0

    tempres = []
    tempres.append(0)
    for x in range(6):
      img = cv2.imread("captcha.png",0)
      retval, img = cv2.threshold(img, x*40,230, cv2.THRESH_TOZERO)
      img = cv2.resize(img,(100,100),fx=1.1,fy=1.1, interpolation=cv2.INTER_CUBIC)
      cv2.imwrite("screenshots/captcha.png",img)
      method = cv2.TM_SQDIFF_NORMED
      template = cv2.imread("Check.png", 0)

      if x % 2 != 0:
        whiteBG = False
        template = cv2.bitwise_not(template)
      else:
        whiteBG = True
      
      for i in range (10):
        if(i != 0):
          template = cv2.imread("check.png", 0)
        template = cv2.resize(template,(100,100),fx=1.1,fy=1.1, interpolation=cv2.INTER_CUBIC)

        for j in range (36):
          img = cv2.imread('screenshots/captcha.png', 0)
          img2 = cv2.imread('screenshots/captcha.png', 1)
          template=self.rotate_image(template, 10,whiteBG)
          cv2.imwrite("template/tmpl"+str(i)+"angle"+str(j*10)+".png",template)

          w, h = template.shape[::-1]	#width and height of the template
          img3 = img2.copy()
          res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED) #result of the match between the template and the captchaClean using TM_CCOEFF_NORMED method
          print(res)
          if res[0][0] > 0.45:
            tempres.append(res[0][0])
          
          min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
          top_left = max_loc #coordinates of the top left corner of the match of the template within the captchaClean
          bottom_right = (top_left[0] + w, top_left[1] + h)
          cv2.rectangle(img2, top_left, bottom_right, (0, 255, 0), 2) #draw a rectangle on what seems the best match

    print(tempres)
    if tempres != [0]:
      print("captcha")
      return True
    else:
      print("no captcha")
      return False

  #Finish later
  def SolveCaptcha(self):
    try:
      result = self.solver.coordinates('2captcha.jpg', lang='en')
    except Exception as e:
      if 'ERROR_CAPTCHA_UNSOLVABLE':
        self.tap(0.95,0.4)

      self.SolveCaptcha()
      self.screenshotOfCaptcha()

      if self.Check(False) == True:
        return
    else:
      results = result.values()
      coords = list(results)
      Tcoords = coords[1].split(':')
      Tcoords2 = Tcoords[1].split(';')

      for i in Tcoords2:
        value = i.split(',')
        x = value[0].split('=')
        y = value[1].split('=')

        Xc, Yc = self.mathman(float(x[1]),float(y[1]))
        print("X = {}, Y = {}".format(Xc,Yc))
        self.tap(Yc,Xc)

      self.tap(0.95,0.6)
      time.sleep(3)
      self.screenshotOfCaptcha()

      if self.Check(False) == True:
        print("Captcha not solved")
        self.SolveCaptcha()
      return

  #initial captha solving
  def TestCaptcha(self, whiteBG):
    captcha = False
    self.screenshotOfCaptcha()
    self.getPuzzleImageFromCaptcha()
    captcha = self.findObj(whiteBG)

    if captcha == True:
      print("capthca spotted")
      self.screenshotOfCaptcha()
      time.sleep(1)
      self.SolveCaptcha()
    return

  #Starts the capthca solving
  def startCaptcha(self):

    self.lookingForCaptcha = True

    start = time.time()
    self.tap(.2,.75)
    self.tap(.5,.55)

    time.sleep(1)
    self.TestCaptcha(False)

    end = time.time()
    print("It took me: ", str(end - start), "s to find 1 object")

    self.tap(.9,.5)

    self.tap(0.1,0.1)
    time.sleep(.5)
    self.tap(0.1,0.1)
    
    self.lookingForCaptcha = False

#bala bla
