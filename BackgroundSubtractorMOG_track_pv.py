import argparse
import imutils
import time
import cv2
#import os
import sys
from picamera.array import PiRGBArray
from picamera import PiCamera
import json

shift=-40

minutes = 60*5 # 300second upload once
#f2=open("col2.txt","a")
file_read = open("/boot/id.txt", "r")
for line in file_read:
    node_id = int(line.rstrip("\n"))
    break
file_read.close()
print node_id

pplsizemin = 2000
pplsizemax = 8000
firstFramesize = 30000
threshold = 30
history = 80
ppl = 0
lastppl = 0
cX = 0
cY = 0

lastcX = 0
lastcY = 0
pX = 320
pY = 240
gate = 28

lineB=pY/2-gate+shift
lineR=pY/2+gate+shift

enter = " "
sumppl = 0
sumppl_in = 0
sumppl_out = 0
abreast = 10



# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera(resolution=(pX,pY), framerate=30)


camera.rotation = 270
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
cv2.ellipse(firstFrame,(pX/2,lineB+50),(pX/2,60),180,0,180,(255,0,0),3)
cv2.line(firstFrame,(0,lineR),(pX,lineR),(0,0,255),3)

while 10*i<pY:
	cv2.line(firstFrame,(0,10*i),(pX,10*i),(0,255,0),1)
	i = i+1
#cv2.imshow("firstFrame", firstFrame)
cv2.imwrite('/home/pi/Desktop/DataGather/firstFrame_full.jpg',firstFrame)
firstFrame = firstFrame[0:500, 80:300]
cv2.imwrite('/home/pi/Desktop/DataGather/firstFrame_line.jpg',firstFrame)

#camera =  cv2.imread("temp.bmp")
#firstFrame = camera
#firstFrame = cv2.equalizeHist(firstFrame)
fgbg = cv2.BackgroundSubtractorMOG()
	

	
cY_begin= [[0,0] for i in range(abreast)]
c_in    = [[0] for i in range(abreast)]
c_out   = [[0] for i in range(abreast)]
dir = 0

ticks_start = time.time()
print ("ticks_start :", ticks_start)


#num=0
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	ppl = 0

	path = 1
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
		
	image = frame.array[50:180, 0:300]
		
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (9, 9), 0)
	im_bw = fgbg.apply(gray, learningRate= 1.0/history)
	#gray = cv2.equalizeHist(gray)
	#print gray.dtype
	cv2.ellipse(image,(pX/2,lineB+50),(pX/2,60),180,0,180,(255,0,0),3)
	cv2.line(image,(0,lineR),(pX,lineR),(0,0,255),3)
	#cv2.line(image,(0,pY/2),(pX,pY/2),(255,0,0),3)

	
	'''
	if firstFrame is None:
		firstFrame = gray.copy()
		rawCapture.truncate(0)
		continue
	
	#cv2.accumulateWeighted(gray, avg, 0.5)
	#frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
	frameDelta = cv2.absdiff(gray, firstFrame)
	

	im_bw = frameDelta
	'''
	#im_bw = cv2.cvtColor(frameDelta, cv2.COLOR_RGB2GRAY)
	(thresh, im_bw) = cv2.threshold(im_bw, threshold, 255, 0)
	im_bw = cv2.dilate(im_bw, None, iterations=10)
	(cnts, _) = cv2.findContours(im_bw.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	#gray = cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR);
	for c in cnts:
		#print cv2.contourArea(c)
		
		'''
		if cv2.contourArea(c) >firstFramesize:
			firstFrame = None
			print "move"
			time.sleep(2)
			continue
		'''
		if (cv2.contourArea(c) < pplsizemin):
			continue

		
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
		cv2.putText(image, "T"+str(ppl), (x, y),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
		#print("x,y,w,h:",x,y,w,h)
		
		M = cv2.moments(c)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
		# draw the contour and center of the shape on the image
		cv2.drawContours(image, [c], -1, (0, 255, 0), -1)
		cv2.circle(image, (cX, cY), 7, (255, 255, 255), 1)
		#cv2.putText(image, "center", (cX - 20, cY - 20),
		#cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
				
		
		if ((abs(cY-pY/2-shift)<gate) and c_in[ppl][0]==0):
			c_in[ppl][0] = 1
			#cX_begin[ppl][0]=cX
			cY_begin[ppl][0]=cY
			#print ("in")
			#print cX_begin
			#print cY_begin
		if ((abs(cY-pY/2-shift)>gate) and c_out[ppl][0]==0 and c_in[ppl][0] ==1):
			c_out[ppl][0] = 1
			#cX_begin[ppl][1]=cX
			cY_begin[ppl][1]=cY
			#print ("out")
			#print cX_begin
			#print cY_begin
			dir = abs(cY_begin[ppl][0] - cY_begin[ppl][1])
			print dir,gate
			if (dir>gate):
				if  (cY<pY/2+shift):
					sumppl = sumppl +1
					enter = "++"
					sumppl_in = sumppl_in+1
				else:
					sumppl = sumppl -1
					enter = "--"
					sumppl_out = sumppl_out +1
				print("in: "+ str(sumppl_in)+"   out: "+str(sumppl_out)+"  sum :"+str(sumppl)+"   enter: "+str(enter) );
				with open("col.txt","a") as f:

	                                f.write("in: "+ str(sumppl_in)+"   out: "+str(sumppl_out)+"  sum :"+str(sumppl)+"   enter: "+str(enter) );	
#		f2.write("writed");
#		f2.close()
		'''
		while path<len(cX_begin[ppl])-1:
			cv2.line(image,(cX_begin[ppl][path],cY_begin[ppl][path]),(cX_begin[ppl][path+1],cY_begin[ppl][path+1]),(255,0,0),2)
			path = path +1
		'''
		if(c_in[ppl][0] == 1 and c_out[ppl][0] == 1):
			c_in[ppl][0] = 0
			c_out[ppl][0] = 0
			cY_begin[ppl][0] = 0
			cY_begin[ppl][1] = 0
		
		ppl = ppl+1
	
	
	#if sumppl != lastppl:
	#	print (sumppl)
	pc = "PPL"+str(ppl)
		
	cv2.putText(image, pc, (30, 60),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
	#cv2.putText(image, "X:"+str(cX), (10, image.shape[0] - 50),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
	#cv2.putText(image, "Y:"+str(cY), (10, image.shape[0] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
	#cv2.putText(image, "Enter:"+enter, (pX-80, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(image, "Sum:"+str(sumppl), (pX-80, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(image, "ppl_in:"+str(sumppl_in), (pX-80, 70),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(image, "ppl_out:"+str(sumppl_out), (pX-80, 90),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	
	lastppl = sumppl

	
	ticks_now = time.time()
	
	if(ticks_now-ticks_start) > minutes:
		print ("ticks_now :", ticks_now)
		ticks = int(round(time.time() * 1000))
		#ticks = ticks[:13]
		f = open('/home/pi/Desktop/DataGather/Data/ktph_'+ str(node_id) + '_' + str(ticks) +'.txt', 'w')
		data =[{"node_id":node_id,"date_time":str(ticks),"ppl_in":sumppl_in,"ppl_out":sumppl_out}]
		json.dump(data, f)
		print(data)
		f.close()
		print("Data recorded as "+ 'ppl_'+ str(node_id) + '_' + str(ticks_now) +'.txt')
		sumppl_in=0
		sumppl_out=0
		sumppl=0
		ticks_start = ticks_now
		
	
	#cv2.putText(gray, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),(10, gray.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.1, (0, 0, 255), 0.1)
	rawCapture.truncate(0)
	cv2.imshow("firstFrame", firstFrame)
	cv2.imshow("frame", image)
	#cv2.imshow("frameDelta", frameDelta)
	cv2.imshow("dilate", im_bw)
	cv2.waitKey (10)
	#time.sleep(waitcamera)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	#num = num+1
cv2.destroyAllWindows()

