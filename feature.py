from enums import AreaCategory, CommonLimit

class CategoryFeature:
  def __init__(self, roi, roiGray, x, y, w, h, ratewh, offset_bottom, ratew, mean, area, length, rateArea, max_indx_value, cnt_num, contour_feature, rect):
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
    self.max_indx_value = max_indx_value
    self.cnt_num = cnt_num
    self.contour_feature = contour_feature
    self.rect = rect

  def calulateCategory(self):
    contour_feature = self.contour_feature
    if (contour_feature.get('perimeter') < CommonLimit.diffPix):
      self.category_type = AreaCategory.UNKNOW
      return
    if (contour_feature.get('perimeter') < CommonLimit.textPerimeterLimit and contour_feature.get('area') < CommonLimit.textAreaLimit):
      self.category_type = AreaCategory.TEXT
      return
    if (CategoryFeature.approximateSame(self.x, 0) or CategoryFeature.approximateSame(self.y, 0) or CategoryFeature.approximateSame(self.offset_bottom, 0)) or self.rateArea > CommonLimit.rateMaxLimit:
      self.category_type = AreaCategory.UNKNOW
    elif self.ratew > CommonLimit.gridRatewLimit and (CategoryFeature.approximateSame(self.max_indx_value, CommonLimit.filterGrayValue) and self.h > CommonLimit.gridTop * 2):
      self.category_type = AreaCategory.FILTER
    elif (self.ratew > CommonLimit.gridRatewLimit):
      print(self.x, self.y, self.w, self.h, self.max_indx_value)
      self.category_type = AreaCategory.GRID
    elif (CategoryFeature.approximateInRange(self.h, CommonLimit.buttonHeightMinLimit, CommonLimit.buttonHeightMaxLimit) and self.w < CommonLimit.buttonWidthLimit and CategoryFeature.approximateSame(self.max_indx_value, CommonLimit.buttonGrayMean) and self.offset_bottom > CommonLimit.offsetBottomLimit):
      self.category_type = AreaCategory.OPERATION_BTN
    elif (CategoryFeature.approximateSame(self.ratewh, 1, 0.1) and CategoryFeature.approximateSame(self.h, CommonLimit.paginationButtonHeight) and self.offset_bottom < CommonLimit.offsetBottomLimit):
      self.category_type = AreaCategory.PAGINATION
    else:
      self.category_type = AreaCategory.UNKNOW

  @staticmethod
  def approximateSame(*args):
    if (len(args) == 2):
      a, b = args
      return abs(a-b)<CommonLimit.diffPix
    else:
      a, b, x = args
      return abs(a-b)<x

  @staticmethod
  def approximateInRange(data, a, b):
    return data >= a - CommonLimit.diffPix and data <= b +CommonLimit.diffPix

  @staticmethod
  def approximateEnumSame(v, my_enum):
    r = []
    for item in my_enum:
      r.append({"diff": abs(item.value - v), "item": item})
    r.sort(key=lambda elem: elem["diff"])
    if r[0]["diff"] < CommonLimit.diffPix:
      return r[0]["item"].name
    else:
      return false