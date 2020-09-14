import cv2 as cv
import pytesseract
import numpy as np
import random
import time

from pytesseract import Output
from enums import AreaCategory, CommonLimit, ButtonSize, Color
from feature import CategoryFeature
np.set_printoptions(threshold=np.inf)

class ImgToGrid:
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

    self.cfs = self.calculateFeature(self.contours, self.originImg)
    self.toCategory(self.cfs, self.originImg)
    # # 绘制
    # self.tempImg = self.originImg.copy()
    # for cf in self.cfs:
    #   [x, y, w, h] = cf.rect
    #   cv.rectangle(self.tempImg, (x, y), (x + w, y + h), (0,0,255), 1)
    # cv.imwrite('./out/6_rect.jpg', self.tempImg)

    # self.noTextContours, self.textContours = self.detectTextContours(self.contours) # 待修改
    # cv.drawContours(image=self.tempImg, contours=self.noTextContours, contourIdx=-1, color=(255,255,0), thickness=1)
    # cv.drawContours(image=self.tempImg, contours=self.textContours, contourIdx=-1, color=(0,0,255), thickness=1)
    # cv.imwrite('./out/5_contours.jpg', self.tempImg)

    # self.textContoursFeature = self.calculateContoursFeature(self.textContours)
    # self.boundingRectList = self.toRect(self.noTextContours)
    # self.uniqBoundingRectList = self.toUniqRect(self.boundingRectList)
    # # 绘制
    # self.tempImg = self.originImg.copy()
    # for rect in self.uniqBoundingRectList:
    #   [x, y, w, h] = rect
    #   cv.rectangle(self.tempImg, (x, y), (x + w, y + h), (0,0,255), 1)
    # cv.imwrite('./out/6_rect.jpg', self.tempImg)

    # self.cfs = self.toCategory(self.uniqBoundingRectList, self.originImg)
    self.gridList, self.operationList, self.paginationList, self.textList = self.splitCategory(self.cfs)
    self.gridDict = self.handleGridFeature(self.gridList)
    self.gridToken = self.getGridToken(self.gridDict, self.originImg)
    self.getOperationToken(self.operationList, self.originImg)

  def toGray(self, data):
    return cv.cvtColor(data, cv.COLOR_BGR2GRAY)

  def toEdges(self, data):
    return cv.Laplacian(data, cv.CV_8U)

  def toThreshold(self, data):
    return cv.threshold(data, 0, 255, cv.THRESH_BINARY)

  def toContours(self, data):
    return cv.findContours(data, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

  def calculateFeature(self, data, img):
    imgHeight, imgWidth, imgAisle = img.shape
    feature_list = []
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
      contour_feature = {"perimeter": perimeter, "area": area, "cx": cx, "cy": cy }
      if len(cnt) < 4:
        continue
      x, y, w, h = cv.boundingRect(cnt)
      rect = [x, y, w, h]
      area = w * h
      length = (w + h) * 2
      rateArea = (w * h)/(imgWidth * imgHeight)
      ratewh = w / h # 宽长比
      ratew = w / imgWidth # 占整体图像高度比
      offset_bottom = imgHeight - y - h # 底边距离
      roi = img[y:y+h, x:x+w]
      roiGray = self.toGray(roi)
      mean, stddev = cv.meanStdDev(roiGray)
      hist = cv.calcHist([roiGray], [0], None, [256], [0, 256])
      min_val,max_val,min_indx,max_indx=cv.minMaxLoc(hist)
      max_indx_c, max_indx_value = max_indx
      cf = CategoryFeature(roi=roi, roiGray=roiGray, x=x, y=y, w=w, h=h, ratewh=ratewh, offset_bottom=offset_bottom, ratew=ratew, mean=mean[0,0], area=area, length=length, rateArea=rateArea, max_indx_value=max_indx_value, cnt_num=len(cnt), contour_feature=contour_feature, rect=rect)
      feature_list.append(cf)
    uniq_list = self.toUniqRect(feature_list)
    return uniq_list

  # def calculateContoursFeature(self, data):
  #   contours_feature_list = []
  #   for index, cnt in enumerate(data):
  #     perimeter = cv.arcLength(cnt, False)
  #     area = cv.contourArea(cnt) 
  #     M = cv.moments(cnt)
  #     if M['m00'] > 0:
  #       cx = int(M['m10']/M['m00'])
  #       cy = int(M['m01']/M['m00'])
  #     else:
  #       cx = 0
  #       cy = 0
  #     contours_feature_list.append({"perimeter": perimeter, "area": area, "cx": cx, "cy": cy })
  #   return contours_feature_list

  # 需要重构
  # def detectTextContours(self, data):
  #   imgHeight, imgWidth, imgAisle = self.originImg.shape
  #   no_text_contours = []
  #   text_contours = []
  #   for index, cnt in enumerate(data):
  #     perimeter = cv.arcLength(cnt, False)
  #     area = cv.contourArea(cnt) 
  #     if (perimeter > imgWidth * 0.9 or (perimeter > CommonLimit.textPerimeterLimit and len(cnt) < CommonLimit.simpleCntContainNumLimit and (area > CommonLimit.textAreaLimit or area == 0))):
  #       no_text_contours.append(cnt)
  #       continue
  #     text_contours.append(cnt)
  #   return no_text_contours, text_contours

  # def toRect(self, data):
  #   return [list(cv.boundingRect(cnt)) for cnt in data]

  def toUniqRect(self, data):
    uniqBoundingRectList = []
    for index, item in enumerate(data):
      flag = False
      for j in range(index + 1, len(data)):
        otherItem = data[j]
        if (self.isSameRange(item.rect, otherItem.rect)):
          flag = True
          break
      if (not flag):
        uniqBoundingRectList.append(item)
    return uniqBoundingRectList

  # 特征分类集合
  def toCategory(self, data, img):
    # imgHeight, imgWidth, imgAisle = img.shape
    # result = []
    for index, cf in enumerate(data):
      # [x, y, w, h] = rect
      # area = w * h
      # length = (w + h) * 2
      # rateArea = (w * h)/(imgWidth * imgHeight)
      # ratewh = w / h # 宽长比
      # ratew = w / imgWidth # 占整体图像高度比
      # offset_bottom = imgHeight - y - h # 底边距离
      # roi = img[y:y+h, x:x+w]
      # roiGray = self.toGray(roi)
      # mean, stddev = cv.meanStdDev(roiGray)
      # hist = cv.calcHist([roiGray], [0], None, [256], [0, 256])
      # min_val,max_val,min_indx,max_indx=cv.minMaxLoc(hist)
      # max_indx_c, max_indx_value = max_indx
      # cf = CategoryFeature(roi=roi, roiGray=roiGray, x=x, y=y, w=w, h=h, ratewh=ratewh, offset_bottom=offset_bottom, ratew=ratew, mean=mean[0,0], area=area, length=length, rateArea=rateArea, max_indx_value=max_indx_value)
      cf.calulateCategory()
      # print(cf.x,  cf.y, cf.w, cf.h, cf.category_type)
      # result.append(cf)
    # return result

  # 拆散子类目 grid合并
  def splitCategory(self, cfs):
    grid_list = []
    text_list = []
    operation_list = []
    pagination_list = []
    filter_list = []
    self.tempImg = self.originImg.copy()
    for cf in cfs:
      x = cf.x
      y = cf.y
      w = cf.w
      h = cf.h
      if (cf.category_type == AreaCategory.GRID):
        grid_list.append(cf)
        cv.rectangle(self.tempImg, (x, y), (x + w, y + h), Color.RED.value, 2)
      elif (cf.category_type == AreaCategory.TEXT):
        text_list.append(cf)
        cv.rectangle(self.tempImg, (x, y), (x + w, y + h), Color.GREEN.value, 2)
      elif (cf.category_type == AreaCategory.OPERATION_BTN):
        operation_list.append(cf)
        cv.rectangle(self.tempImg, (x, y), (x + w, y + h), Color.ORANGE.value, 2)
      elif (cf.category_type == AreaCategory.PAGINATION):
        pagination_list.append(cf)
        cv.rectangle(self.tempImg, (x, y), (x + w, y + h), Color.BROWN.value, 2)
      elif (cf.category_type == AreaCategory.FILTER):
        filter_list.append(cf)
        cv.rectangle(self.tempImg, (x, y), (x + w, y + h), Color.PURPLE.value, 2)
      else:
        pass
        cv.rectangle(self.tempImg, (x, y), (x + w, y + h), Color.BLUE.value, 2)
    cv.imwrite('./out/5_cf.jpg', self.tempImg)
    return grid_list, operation_list, pagination_list, text_list

  def handleGridFeature(self, grid_list):
    grid_dict = {}
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
    # 表格grid组件外接矩形
    x_left_top_t, y_left_top_t, x_right_bottom_t, y_right_bottom_t = self.findGridTopRect(x_left_top, y_left_top, x_right_bottom, y_right_bottom)
    # 获取column分割点
    centerList = self.findGridTopColumns(x_left_top_t, y_left_top_t, x_right_bottom_t, y_right_bottom_t)
    grid_dict['centerList'] = centerList
    grid_dict['cloumnsArea'] = [x_left_top_t, y_left_top_t, x_right_bottom_t, y_right_bottom_t]
    return grid_dict
 
  def findGridTopRect(self, x_left_top, y_left_top, x_right_bottom, y_right_bottom):
    return x_left_top, y_left_top, x_right_bottom,  y_left_top+CommonLimit.gridTop

  def findGridTopColumns(self, x_left_top, y_left_top, x_right_bottom, y_right_bottom):
    result = []
    for text_cf in self.textList:
      cx = text_cf.contour_feature.get('cx')
      cy = text_cf.contour_feature.get('cy')
      if cx > x_left_top and cx < x_right_bottom and cy > y_left_top and cy < y_right_bottom:
        result.append(text_cf.contour_feature)
    sortList = sorted(result, key=lambda feature: feature.get('cx'))
    centerList = []
    for index, feature in enumerate(sortList):
      if index == len(sortList) - 1:
        break
      after = sortList[index+1].get('cx')
      before = feature.get('cx')
      if (after - before > CommonLimit.columnSpaceThreshold):
        center = int((before + after)/2)
        centerList.append(center)
    return centerList

  def getGridToken(self, gridDict, img):
    centerList = gridDict.get('centerList')
    cloumnsArea = gridDict.get('cloumnsArea')
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
     
      roi = img[cloumnsArea[1]:cloumnsArea[3], before:current]
      code = pytesseract.image_to_string(roi, lang='chi_sim+eng')
      # 计算边框 待重构
      d = pytesseract.image_to_data(roi, output_type=Output.DICT, lang='chi_sim+eng')
      # print(d)
      delete_space_code = code.replace(' ','')
      columns_split.append({"area": [before, cloumnsArea[1], current, cloumnsArea[3]], "text": delete_space_code})
    print('gridtoken-------', columns_split)
    return columns_split  
      
  def getOperationToken(self, operationList, img):
    result = []
    for btnCf in operationList:
      roi = img[btnCf.y:btnCf.y+btnCf.h, btnCf.x:btnCf.x+btnCf.w]
      roiGray = self.toGray(roi)
      code = pytesseract.image_to_string(roiGray, lang='chi_sim+eng')
      delete_space_code = code.replace(' ','')
      size = CategoryFeature.approximateEnumSame(btnCf.h, ButtonSize)
      btn_type = 'primary' # 后续识别
      result.append({"text": delete_space_code, "size": size, "x-left": btnCf.x})
      # 排序
    print(result)

  def isSameRange(self, r1, r2):
    diffPix = CommonLimit.diffPix
    return abs(r1[0] - r2[0]) < diffPix/2 and abs(r1[1] - r2[1]) < diffPix/2 and abs(r1[2] - r2[2]) < diffPix/2 and abs(r1[3] - r2[3]) < diffPix/2

ImgToGrid('./in/a1.jpg').run()







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
