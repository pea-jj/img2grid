import cv2 as cv
import numpy as np
import random
import time

from enums import AreaCategory, CommonLimit, ButtonSize, Color
np.set_printoptions(threshold=np.inf)


class ImgProess:
    def __init__(self, input_imgpath):
        self._input_imgpath = input_imgpath

    def get_contours(self, draw):
        origin_img = cv.imread(self._input_imgpath)
        temp_img = origin_img.copy()
        gray_img = self.to_gray(origin_img)
        edges = self.to_edges(gray_img)
        ret, thresh = self.to_threshold(edges)
        contours, hierarchy = self.to_contours(thresh)
        if draw:
            cv.imwrite('./out/1_gray-img.jpg', gray_img)
            cv.imwrite('./out/2_edges.jpg', edges)
            cv.imwrite('./out/3_thresh.jpg', thresh)
            cv.drawContours(image=temp_img, contours=contours,
                        contourIdx=-1, color=(255, 255, 0), thickness=1)
            cv.imwrite('./out/4_contours.jpg', temp_img)
        return contours, origin_img

    def to_gray(self, data):
        return cv.cvtColor(data, cv.COLOR_BGR2GRAY)

    def to_edges(self, data):
        return cv.Laplacian(data, cv.CV_8U)

    def to_threshold(self, data):
        return cv.threshold(data, 4, 255, cv.THRESH_BINARY)

    def to_contours(self, data):
        return cv.findContours(data, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
