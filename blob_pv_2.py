+++import argparse
import imutils
import time
import cv2
import numpy as np
import sys
from picamera.array import PiRGBArray
from picamera import PiCamera

shift=-30

pplsizemin = 50
pplsizemax = 2000
history = 20
ppl = 0
lastppl = 0
cX = 0
cY = 0

pX = 320
pY = 240
gate = 40


lineB=pY/2-gate+shift
lineR=pY/2+gate+shift

enter = " "
sumppl = 0
abreast = 10

fgbg = cv2.BackgroundSubtractorMOG()
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3, 3)) 
	
c_in    = [0 for i in range(abreast)]
c_out   = [0 for i in range(abreast)]
cY_temp  = [0 for i in range(abreast)]
getpplno =0
getpplflag =0

######

##  hairLower = (0, 0, 40)
##hairUpper = (255, 255, 255)

hairLower = (63, 90, 0)
hairUpper = (87, 255, 255)



# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera(resolution=(pX,pY), framerate=30)


#camera.rotation = 180
time.sleep(2)

'''
# Set ISO to the desired value
camera.iso = 100
# Wait for the automatic gain control to settle
# Now fix the values
camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g
# Turn the camera's LED off
camera.led = False
'''

rawCapture = PiRGBArray(camera, size=(pX,pY))

i = 0
camera.capture('firstFrame.jpg')
firstFrame = cv2.imread('firstFrame.jpg')
cv2.line(firstFrame,(0,lineB),(pX,lineB),(255,0,0),3)
cv2.line(firstFrame,(0,lineR),(pX,lineR),(0,0,255),3)

while 10*i<pY:
	cv2.line(firstFrame,(0,10*i),(pX,10*i),(0,255,0),1)
	i = i+1
cv2.imshow("firstFrame", firstFrame)

#camera =  cv2.imread("temp.bmp")
#firstFrame = camera
#firstFrame = cv2.equalizeHist(firstFrame)
fgbg = cv2.BackgroundSubtractorMOG()
	

	
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):


	image = frame.array
	#####src_hsv = cv2.cvtColor(image,cv2.CV_BGR2HSV)
	cv2.line(image,(0,lineB),(pX,lineB),(255,0,0),3)
	cv2.line(image,(0,lineR),(pX,lineR),(0,0,255),3)
	
	ppl = 0
	getpplflag = 0
	temppl  = [0 for i in range(abreast)]

	image_crop = image[lineB:lineR, 0:pX]
	hsv = cv2.cvtColor(image_crop, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, hairLower, hairUpper)
	image_mask = cv2.erode(mask, kernel, iterations=5)
	image_mask = cv2.dilate(mask,kernel, iterations=5)
	
	gray = cv2.GaussianBlur(image_mask, (9, 9), 0)
	im_bw = fgbg.apply(gray, learningRate=1.0/history)
	
	(cnts, _) = cv2.findContours(im_bw.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	center = None
	
	for c in cnts:
		#print cv2.contourArea(c)
		#print ppl
		if (cv2.contourArea(c) < pplsizemin or cv2.contourArea(c) > pplsizemax):
			continue
			
		((x, y), radius) = cv2.minEnclosingCircle(c)
		#print radius
		M = cv2.moments(c)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
		center = (cX,cY+pY/2-gate+shift)
		if radius > 6 and radius<30:
			ppl = ppl+1
			cv2.circle(image, (int(x), int(y)+pY/2-gate+shift), int(radius),(0, 255, 255), 2)
			cv2.circle(image, center, 5, (0, 0, 255), -1)
		
		
		'''
		if ppl != lastppl:
			if cY<gate:
				temppl[ppl] = -1
			else:
				temppl[ppl] =  1
		'''	
				
		
		if(c_in[ppl]!=0 and c_out[ppl]!=0 ):
			c_in = [0 for i in range(abreast)]
			c_out = [0 for i in range(abreast)]
			
		if (c_in[ppl]==0 and cY!=0):
			if (cY<gate and cY_temp[ppl]<cY):
				c_in[ppl] = -1
				#print ("in -1")
			if (cY>gate and cY_temp[ppl]>cY):
				c_in[ppl] = 1
				#print ("in 1")
		if (c_in[ppl]!=0 and cY!=0):
			if(c_in[ppl] ==-1 and cY>gate):
				c_out[ppl] = -1
				#print ("out -1")
				sumppl = sumppl -1
				enter = "--"
				getpplflag = 1
			if(c_in[ppl] ==1 and cY<gate):
				c_out[ppl] = 1
				#print ("out 1")
				sumppl = sumppl +1
				enter = "++"	
				getpplflag = 1				
		lastppl = ppl
		cY_temp[ppl] = cY
		
		'''
		if (c_in[ppl]==0 and cY<gate):
			c_in[ppl] = -1
			print ("in -1")
			#print cY

		if  (c_in[ppl] ==-1 and cY>gate):
			c_out[ppl] = -1
			print ("out -1")
			sumppl = sumppl -1
			enter = "--"

		if (c_in[ppl]==0 and cY>gate):
			c_in[ppl] = 1
			print ("in 1")

		if  (c_in[ppl] ==1 and cY<gate):
			c_out[ppl] = 1
			print ("out 1")
			sumppl = sumppl +1
			enter = "++"
			
		if(c_in[ppl] !=0 and c_out[ppl]!=0):
			cY_pts= [[0,0] for i in range(abreast)]
			c_in    = [0 for i in range(abreast)]
			c_out   = [0 for i in range(abreast)]
		'''				
			
		'''	
		print ('ppl '+str(ppl))
		print ('lastppl '+str(lastppl))

		
		lastppl = ppl
			
		if(ppl == 0):
			cY_pts= [[0,0] for i in range(abreast)]
			c_in    = [[0] for i in range(abreast)]
			c_out   = [[0] for i in range(abreast)]
			lastppl = 0
		'''
	'''
	for j in range(0,2):
		for i in range(1, len(pts[j])-1):
			if pts[j][i] is None or pts[j][i+1] is None:
				continue
			thickness = int(np.sqrt(buffer / float(i + 1)) * 2.5)
			cv2.line(image, pts[j][i], pts[j][i+1], (0, 0, 255), thickness)
	'''
	
	'''
	if ppl != lastppl:
		for i in range(0, len(temppl)-1):
			sumppl = sumppl + temppl[i]
	'''
	pc = "PPL"+str(ppl)
		
	cv2.putText(image, pc, (30, 60),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
	cv2.putText(image, "X:"+str(cX), (10, image.shape[0] - 50),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
	cv2.putText(image, "Y:"+str(cY), (10, image.shape[0] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
	cv2.putText(image, "Enter:"+enter, (pX-80, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(image, "Sum:"+str(sumppl), (pX-80, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	if getpplflag ==1:
		cv2.imwrite('getppl'+str(getpplno)+'.jpg',image)
		getpplno = getpplno + 1
	
	rawCapture.truncate(0)
	#cv2.imshow("firstFrame", firstFrame)
	cv2.imshow("image_mask", image_mask)
	cv2.imshow("image", image)
	cv2.imshow("dilate", im_bw)
	cv2.waitKey (50)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cv2.destroyAllWindows()



