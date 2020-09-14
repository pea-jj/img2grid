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

class AreaCategory(Enum):
  UNKNOW = 1
  OPERATION_BTN = 2
  GRID = 3
  PAGINATION = 4
  TEXT = 5
  FILTER = 6


class CommonLimit():
  diffPix = 3 * rate # 误差距离
  safeSpace = 5 * rate # 安全距离 去除误差
  buttonWidthLimit = 300 * rate
  buttonHeightMaxLimit = 40 * rate
  buttonHeightMinLimit = 24 * rate
  paginationButtonHeight = 30 * rate
  offsetBottomLimit = 20 * rate # 底边距离 分页在底部
  gridRatewLimit = 0.9
  rateMaxLimit = 0.9
  buttonGrayMean = 84
  gridTop = 40 * rate # 表头高度
  columnSpaceThreshold= 80 * rate # 列之间分割距离阈值
  textPerimeterLimit = 50 * rate # text周长阈值
  simpleCntContainNumLimit = 70 # 轮廓点个数阈值
  textAreaLimit = 400 * rate * rate # text面积阈值
  filterGrayValue = 248 # filter底色

class ButtonSize(Enum):
  large = 40 * rate
  small = 24 * rate
  medium = 32 * rate