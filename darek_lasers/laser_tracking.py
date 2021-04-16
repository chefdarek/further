import imutils
import numpy as np
import argparse
import cv2
import time

from pythonosc import udp_client


#OSC DATA SETUP
parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.1.1.1",
					help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=13000,
					help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

# cv2.namedWindow('Frame', cv2.WND_PROP_FULLSCREEN)
# cv2.setWindowProperty('Frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
vs = cv2.VideoCapture(0)
w = vs.get(cv2.CAP_PROP_FRAME_WIDTH)
h = vs.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(w,h)
# vs.set(3,w)
#
# vs.set(4,h)
# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping
while True:

	# define the lower and upper boundaries of the "green"
	# ball in the HSV color space, then initialize the
	# list of tracked points
	greenLower = np.array([25, 52, 72])
	greenUpper = np.array([102, 255, 255])
	#pts = deque()
	# grab the current frame
	frame = vs.read()
	# handle the frame from VideoCapture or VideoStream
	frame = frame[1]
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if frame is None:
		break
	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None
	# only proceed if at least one contour was found

	if len(cnts) > 0:

		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid\\\\

		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)

		# only proceed if the radius meets a minimum size\\\\

		if radius > 5:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			client.send_message("/toggle_particle", 1)
			print('toggled_particle on')
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)

			x_pos = (((-4)*(x - 0) / (640-0))+2)*-1
			y_pos = ((2*(y - 0) / (480-0))-1)*-1
			client.send_message("/x_data_", round(x_pos,2))
			client.send_message("/y_data_", round(y_pos,2))
			print('x', x, 'norm', x_pos, 'rounded', round(x_pos,2))
			print('y', y, 'norm', y_pos, 'rounded', round(y_pos,2))

		else:
			stop_guide = 0
			if stop_guide > 3:
				break
				stop_guide += 1
				client.send_message("/toggle_particle", 0)
				print('toggled_particle off')


	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):

		vs.release()
# close all windows
cv2.destroyAllWindows()