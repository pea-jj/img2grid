from enum import Enum
rate = 2

class Color(Enum):
  RED = (0, 0, 255)
  YELLOW = (0, 255, 255)
  PURPLE = (240, 32, 160)
  ORANGE = (0, 97, 255)
  GREEN = (0, 255, 0)
  BLUE = (255, 105, 65)
  BROWN = (42, 42, 128)
  MIDNIGHTBLUE = (25, 25, 112)
  DEEPSKYBLUE = (0, 191, 255)

class AreaCategory(Enum):
  UNKNOW = 1
  OPERATION_BTN = 2
  GRID = 3
  PAGINATION = 4
  TEXT = 5
  FILTER = 6
  INPUT = 7
  SELECT = 8
  DOWNICON = 9
  TIME = 10


class CommonLimit():
  diffPix = 3 * rate # 误差距离
  safeSpace = 5 * rate # 安全距离 去除误差
  buttonWidthLimit = 300 * rate
  buttonHeightMaxLimit = 40 * rate
  buttonHeightMinLimit = 24 * rate
  paginationButtonHeight = 32 * rate
  paginationOffsetBottomRateLimit = 0.5
  offsetBottomLimit = 20 * rate # 底边距离 分页在底部
  gridRatewLimit = 0.9
  gridOffsetTopRateLimit = 0.3
  rateMaxLimit = 0.9
  buttonGrayMean = 84
  gridTop = 56 * rate # 表头高度
  columnSpaceThreshold= 80 * rate # 列之间分割距离阈值
  textPerimeterLimit = 50 * rate # text周长阈值
  simpleCntContainNumLimit = 70 # 轮廓点个数阈值
  textAreaLimit = 400 * rate * rate # text面积阈值
  filterGrayValue = 248 # filter底色
  formInputWidthMaxLimit = 400 * rate
  formInputWidthMinLimit = 130 * rate
  formItemHeight = 32 * rate
  formItemBackgroundGray = 255
  formItemLeftTextLimit = 20 * rate # formitem  距离label左边间距阈值
  formItemHeightMarginLimit = 20 * rate # fromitem距离上面的formitem 距离阈值

class ButtonSize(Enum):
  large = 40 * rate
  small = 24 * rate
  medium = 32 * rate

FormItemType = {
  "INPUT": 'input',
  "SELECT": 'select'
}