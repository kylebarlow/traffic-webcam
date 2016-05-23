#!/usr/bin/python3
import numpy
import cv2
import imutils
import time
import sys
import collections
import datetime
import math
import threading
import queue

video_resolution = (1920, 1080)
preview_frame_size = (960, 540)
camera_init_time = 3.0 # seconds

class CameraQueue:
    def __init__(self):
        self.stored_minutes = 5
        self.count_between_background_frames = 0
        self._init_camera()

        threading.Thread(target=self._camera_capture).start()

    def _camera_capture(self):
        while True:
            frame_grabbed_successfully, frame = self.camera.read()
            if frame_grabbed_successfully:
                self.frame_deque.append( (datetime.datetime.now(), frame) )
            else:
                self._init_camera()

    def _init_camera(self):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(3, video_resolution[0])
        self.camera.set(4, video_resolution[1])
        self.frame_rate = self.camera.get(5)
        self.frame_sleep_time = 1.01 / self.frame_rate
        self.frame_deque = collections.deque( maxlen = math.ceil(self.frame_rate) * 10 )
        time.sleep(camera_init_time)

    @property
    def most_recent_frame(self):
        while len(self.frame_deque) == 0:
            time.sleep( 2.0 / self.frame_rate )
        return self.frame_deque[-1][1]

    def sleep_till_next_frame(self):
        time.sleep( self.frame_sleep_time )

def main():
    cam = CameraQueue()
    time.sleep( camera_init_time + 0.5 )
    cv2.startWindowThread()
    cv2.namedWindow("Feed")
    fgbg = cv2.createBackgroundSubtractorMOG2( detectShadows = True )
    while True:
        frame = cam.most_recent_frame
        fgbg_mask = fgbg.apply(frame)
        preview_frame = cv2.resize(fgbg_mask, preview_frame_size, interpolation=cv2.INTER_AREA)
        cv2.imshow("Feed", preview_frame)
        cam.sleep_till_next_frame()

if __name__ == '__main__':
    main()
