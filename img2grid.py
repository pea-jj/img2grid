import cv2 as cv
import pytesseract
import numpy as np
import random
import time
from enums import AreaCategory
from feature import CategoryFeature

class ImgToGrid:
  diffPix = 4 # 误差距离
  colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)] # 绘制颜色数组
  gridTop = 40
  columnSpaceThreshold= 80

  def __init__(self, inputImgPath):
    self.inputImgPath = inputImgPath

  def run(self):
    self.originImg = cv.imread(self.inputImgPath)
    imgHeight, imgWidth, imgAisle = self.originImg.shape
    print('shape-------', imgWidth, imgHeight)
    self.tempImg = self.originImg.copy()
    self.grayImg = self.toGray(self.originImg)
    cv.imwrite('./out/1_gray-img.jpg', self.grayImg)

    self.edges = self.toEdges(self.grayImg)
    cv.imwrite('./out/2_edges.jpg', self.edges)

    ret, self.thresh = self.toThreshold(self.edges)
    cv.imwrite('./out/3_thresh.jpg', self.thresh)

    self.contours, hierarchy= self.toContours(self.thresh)
    cv.drawContours(image=self.tempImg, contours=self.contours, contourIdx=-1, color=(0,255,0), thickness=1)
    cv.imwrite('./out/4_contours.jpg', self.tempImg)

    self.noTextContours, self.textContours = self.detectTextContours(self.contours) # 待修改
    cv.drawContours(image=self.tempImg, contours=self.noTextContours, contourIdx=-1, color=(255,255,0), thickness=1)
    cv.drawContours(image=self.tempImg, contours=self.textContours, contourIdx=-1, color=(0,0,255), thickness=1)
    cv.imwrite('./out/5_contours.jpg', self.tempImg)

    self.textContoursFeature = self.calculateContoursFeature(self.textContours)
    self.boundingRectList = self.toRect(self.noTextContours)
    self.uniqBoundingRectList = self.toUniqRect(self.boundingRectList)
    # 绘制
    self.tempImg = self.originImg.copy()
    for rect in self.uniqBoundingRectList:
      [x, y, w, h] = rect
      cv.rectangle(self.tempImg, (x, y), (x + w, y + h), (0,0,255), 1)
    cv.imwrite('./out/6_rect.jpg', self.tempImg)

    self.cfs = self.toCategory(self.uniqBoundingRectList, self.originImg)
    self.gridList, self.gridDict, self.operationList, self.paginationList = self.splitCategory(self.cfs)
    self.getGridToken(self.gridDict, self.originImg)

  def toGray(self, data):
    return cv.cvtColor(data, cv.COLOR_BGR2GRAY)

  def toEdges(self, data):
    return cv.Laplacian(data, cv.CV_8U)

  def toThreshold(self, data):
    return cv.threshold(data, 0, 255, cv.THRESH_BINARY)

  def toContours(self, data):
    return cv.findContours(data, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

  def calculateContoursFeature(self, data):
    contours_feature_list = []
    for index, cnt in enumerate(data):
      perimeter = cv.arcLength(cnt, False)
      area = cv.contourArea(cnt) 
      M = cv.moments(cnt)
      if M['m00'] > 0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
      else:
        cx = 0
        cy = 0
      contours_feature_list.append({"perimeter": perimeter, "area": area, "cx": cx, "cy": cy })
    return contours_feature_list

  # 需要重构
  def detectTextContours(self, data):
    no_text_contours = []
    text_contours = []
    for index, cnt in enumerate(data):
      perimeter = cv.arcLength(cnt, False)
      area = cv.contourArea(cnt) 
      if (perimeter > 1000 or (perimeter > 50 and len(cnt) < 70 and (area > 400 or area == 0))):
        # print(perimeter, area)
        no_text_contours.append(cnt)
        continue
      text_contours.append(cnt)
    return no_text_contours, text_contours

  def toRect(self, data):
    return [list(cv.boundingRect(cnt)) for cnt in data]

  def toUniqRect(self, data):
    uniqBoundingRectList = []
    for index, rect in enumerate(data):
      flag = False
      for j in range(index + 1, len(data)):
        otherRect = data[j]
        if (self.isSameRange(rect, otherRect)):
          flag = True
          break
      if (not flag):
        uniqBoundingRectList.append(rect)
    return uniqBoundingRectList

  # 特征分类集合
  def toCategory(self, data, img):
    imgHeight, imgWidth, imgAisle = img.shape
    result = []
    for index, rect in enumerate(data):
      [x, y, w, h] = rect
      area = w * h
      length = (w + h) * 2
      rateArea = (w * h)/(imgWidth * imgHeight)
      ratewh = w / h # 宽长比
      ratew = w / imgWidth # 占整体图像高度比
      offset_bottom = imgHeight - y - h # 底边距离
      roi = img[y:y+h, x:x+w]
      roiGray = self.toGray(roi)
      mean, stddev = cv.meanStdDev(roiGray)
      cf = CategoryFeature(roi=roi, roiGray=roiGray, x=x, y=y, w=w, h=h, ratewh=ratewh, offset_bottom=offset_bottom, ratew=ratew, mean=mean[0,0], area=area, length=length, rateArea=rateArea)
      cf.calulateCategory()
      result.append(cf)
    return result

  # 拆散子类目 grid合并
  def splitCategory(self, cfs):
    grid_list = []
    operation_list = []
    pagination_list = []
    grid_dict = {}

    for cf in cfs:
      if (cf.category_type == AreaCategory.GRID):
        grid_list.append(cf)
      elif (cf.category_type == AreaCategory.OPERATION_BTN):
        operation_list.append(cf)
      elif (cf.category_type == AreaCategory.PAGINATION):
        pagination_list.append(cf)
    x_left_top = y_left_top = x_right_bottom = y_right_bottom = -1
    for item in grid_list:
      item_x_left_top = item.x
      item_y_left_top = item.y
      item_x_right_bottom = item.x + item.w
      item_y_right_bottom = item.y + item.h
      if (x_left_top < 0 or x_left_top > item_x_left_top):
        x_left_top = item_x_left_top
      if (y_left_top < 0 or y_left_top > item_y_left_top):
        y_left_top = item_y_left_top
      if (x_right_bottom < 0 or x_right_bottom < item_x_right_bottom):
        x_right_bottom = item_x_right_bottom
      if (y_right_bottom < 0 or y_right_bottom < item_y_right_bottom):
        y_right_bottom = item_y_right_bottom
    print('grid rect', x_left_top, y_left_top, x_right_bottom, y_right_bottom)
    x_left_top_t, y_left_top_t, x_right_bottom_t, y_right_bottom_t = self.findGridTopRect(x_left_top, y_left_top, x_right_bottom, y_right_bottom)
    print('grid rect top', x_left_top_t, y_left_top_t, x_right_bottom_t, y_right_bottom_t)
    # 获取column分割点
    centerList = self.findGridTopColumns(x_left_top_t, y_left_top_t, x_right_bottom_t, y_right_bottom_t)
    grid_dict['centerList'] = centerList
    grid_dict['cloumnsArea'] = [x_left_top_t, y_left_top_t, x_right_bottom_t, y_right_bottom_t]
    return grid_list, grid_dict, operation_list, pagination_list
 
  def findGridTopRect(self, x_left_top, y_left_top, x_right_bottom, y_right_bottom):
    return x_left_top, y_left_top, x_right_bottom,  y_left_top+self.gridTop

  def findGridTopColumns(self, x_left_top, y_left_top, x_right_bottom, y_right_bottom):
    result = []
    for feature in self.textContoursFeature:
      cx = feature.get('cx')
      cy = feature.get('cy')
      if cx > x_left_top and cx < x_right_bottom and cy > y_left_top and cy < y_right_bottom:
        result.append(feature)
    sortList = sorted(result, key=lambda feature: feature.get('cx'))
    centerList = []
    for index, feature in enumerate(sortList):
      if index == len(sortList) - 1:
        break
      after = sortList[index+1].get('cx')
      before = feature.get('cx')
      if (after - before > self.columnSpaceThreshold):
        center = int((before + after)/2)
        centerList.append(center)
    return centerList

  def getGridToken(self, gridDict, img):
    centerList = gridDict.get('centerList')
    cloumnsArea = gridDict.get('cloumnsArea')
    print('rect column,', cloumnsArea)
    columns_split = []
    for index in range(len(centerList) + 1):
      if index < 1:
        before = cloumnsArea[0]
      else:
        before = centerList[index - 1]
      if index < len(centerList):
        current = centerList[index]
      else:
        current = cloumnsArea[2]
      columns_split.append([before, cloumnsArea[1], current, cloumnsArea[3]])
      print([before, cloumnsArea[1], current, cloumnsArea[3]])
      roi = img[cloumnsArea[1]:cloumnsArea[3], before:current]
      code = pytesseract.image_to_string(roi, lang='chi_sim+eng')
      print(code)
      cv.imshow(str(index), roi)
    cv.waitKey()
      



  def isSameRange(self, r1, r2):
    diffPix = self.diffPix
    return abs(r1[0] - r2[0]) < diffPix and abs(r1[1] - r2[1]) < diffPix and abs(r1[2] - r2[2]) < diffPix and abs(r1[3] - r2[3]) < diffPix

  def isGridContourRect(self, rect, img):
    width = rect[3]
    w, h, aisle = img.shape
    # print(width, w)
    return width > w * 0.9
    

ImgToGrid('./in/sheji.png').run()







# diffPix = 4

# colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

# img = cv.imread('./sheji.png')
# code = pytesseract.image_to_string(img, lang='chi_sim+eng')
# print(code)
# print('原图属性', img.shape)
# # 灰度
# gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# # 边缘
# edges = cv.Laplacian(gray, cv.CV_8U)
# # 二值化
# ret, thresh = cv.threshold(edges, 0, 255, cv.THRESH_BINARY)
# # 直线
# # lines = cv.HoughLinesP(thresh, 1, np.pi/180, 30, minLineLength=6, maxLineGap=5)
# # for lin e in lines:
# #     x1, y1, x2, y2 = line[0]
# #     cv.line(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
# # cv.imwrite('houghlines.jpg', img)

# # 轮廓
# contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
# print('contours数量', len(contours))
# new_contours = []
# for index, cnt in enumerate(contours):
#   perimeter = cv.arcLength(cnt,False)
#   area = cv.contourArea(cnt) 
#   if (perimeter < 50 or len(cnt) > 100 or area < 400):
#     continue
#   # print(perimeter, area, len(cnt))
#   new_contours.append(cnt)
# # cv.drawContours(img, new_contours, 24, (0, 0, 255), 2)

# boundingRectList = []

# for index, cnt in enumerate(new_contours):
#   x, y, w, h = cv.boundingRect(cnt)
#   # print(index, x, y, w, h)
#   boundingRectList.append([x, y, w, h])

# def sameRange(r1, r2):
#   return abs(r1[0] - r2[0]) < diffPix and abs(r1[1] - r2[1]) < diffPix and abs(r1[2] - r2[2]) < diffPix and abs(r1[3] - r2[3]) < diffPix

# uniqBoundingRectList = []
# for index, rect in enumerate(boundingRectList):
#   flag = False
#   for j in range(index + 1, len(boundingRectList)):
#     otherRect = boundingRectList[j]
#     if (sameRange(rect, otherRect)):
#       flag = True
#       break
#   if (not flag):
#     uniqBoundingRectList.append(rect)

# for index, rect in enumerate(uniqBoundingRectList):
#   [x, y, w, h] = rect
#   cv.rectangle(img, (x, y), (x+w, y+h), colors[index % 5])

# print(len(uniqBoundingRectList))

# cv.imwrite('contours.jpg', img)
# # cv.drawContours(img, contours, -1, (0,0,255), 3)
# cv.imshow('img', img)

# # cv.imshow('thresh', thresh)
# # cv.imshow('line', 'houghlines.jpg')
# cv.waitKey(0)
# # cv.destroyAllWindows()
