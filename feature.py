from enums import AreaCategory

class CategoryFeature:
  diffPix = 4 # 误差距离
  safeSpace = 5 # 安全距离 去除误差

  def __init__(self, roi, roiGray, x, y, w, h, ratewh, offset_bottom, ratew, mean, area, length, rateArea):
    self.roi = roi
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    self.ratewh = ratewh
    self.offset_bottom = offset_bottom
    self.ratew = ratew
    self.mean = mean
    self.area = area
    self.length = length
    self.rateArea = rateArea
    # print( x, y, w, h, ratewh, offset_bottom, ratew, mean)

  def calulateCategory(self):
    if (self.x<self.safeSpace or self.y<self.safeSpace or self.offset_bottom<self.safeSpace):
      self.category_type = AreaCategory.UNKNOW
    if (self.ratew > 0.9 and self.rateArea < 0.9):
      self.category_type = AreaCategory.GRID
    elif (abs(self.h - 35) < self.diffPix and self.w < 300 and self.mean < 78+15 and self.mean > 78-15):
      self.category_type = AreaCategory.OPERATION_BTN
    elif (self.ratewh<1.0+0.2 and self.ratewh>1.0-0.2 and abs(self.h - 35) < self.diffPix and self.offset_bottom < 20):
      self.category_type = AreaCategory.PAGINATION
    else:
      self.category_type = AreaCategory.UNKNOW
