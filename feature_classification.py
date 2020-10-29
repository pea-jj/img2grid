import collections
# import pytesseract
from util import approximate_same, approximate_inrange, approximate_enumsame, is_same_range, is_contain_rect
from enums import AreaCategory, CommonLimit, Color
from img_process import ImgProess
import cv2 as cv


class FeatureClassification:
    def __init__(self, cnts, text_list, dropdown_cnt, img):
        self._cnts = cnts
        self._text_list = text_list
        self._img = img
        self._dropdown_cnt = dropdown_cnt

    def run(self):
        cfs = self.calculate_feature(self._cnts, self._img)
        cfs = self.replace_text(cfs)
        categorys_list = self.split_category(cfs)
        self.classification_by_structure(categorys_list)
        self.draw_classification(categorys_list)
        return categorys_list
    

    def calculate_feature(self, data, img):
        img_height, img_width, img_alias = img.shape
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
            contour_feature = {"perimeter": perimeter,
                               "area": area, "cx": cx, "cy": cy}
            if len(cnt) < 2 or perimeter < 6:
                continue
            x, y, w, h = cv.boundingRect(cnt)
            rect = [x, y, w, h]
            area = w * h
            length = (w + h) * 2
            rateArea = (w * h)/(img_width * img_height)
            ratewh = w / h  # 宽长比
            ratew = w / img_width  # 占整体图像高度比
            offset_bottom = img_height - y - h  # 底边距离
            offset_bottom_rate = offset_bottom/img_height
            offset_top_rate = y/img_height
            roi = img[y:y+h, x:x+w]
            roiGray = ImgProess('').to_gray(roi)
            mean, stddev = cv.meanStdDev(roiGray)
            hist = cv.calcHist([roiGray], [0], None, [256], [0, 256])
            min_val, max_val, min_indx, max_indx = cv.minMaxLoc(hist)
            max_indx_c, max_indx_value = max_indx
            cf = Feature(roi=roi, roiGray=roiGray, x=x, y=y, w=w, h=h, ratewh=ratewh, offset_bottom=offset_bottom, offset_bottom_rate=offset_bottom_rate, offset_top_rate=offset_top_rate, ratew=ratew,
                         mean=mean[0, 0], area=area, length=length, rateArea=rateArea, max_indx_value=max_indx_value, cnt_num=len(cnt), contour_feature=contour_feature, rect=rect, cnt=cnt)
            cf.calulate_category(self._dropdown_cnt)
            feature_list.append(cf)
        uniq_list = self.to_uniqRect(feature_list)
        return uniq_list

    def to_uniqRect(self, data):
        uniq_bounding_rect_list = []
        for index, item in enumerate(data):
            flag = False
            for j in range(index + 1, len(data)):
                other_item = data[j]
                if (is_same_range(item.rect, other_item.rect)):
                    flag = True
                    break
            if (not flag):
                uniq_bounding_rect_list.append(item)
        return uniq_bounding_rect_list

    def split_category(self, cfs):
        categorys_list = collections.OrderedDict()
        for cf in cfs:
            x = cf.x
            y = cf.y
            w = cf.w
            h = cf.h
            if cf.category_type in categorys_list:
                categorys_list[cf.category_type].append(cf)
            else:
                categorys_list[cf.category_type] = [cf]
           
        return categorys_list

    def draw_classification(self, categorys_list):
        color_list = list(Color)
        tempImg = self._img.copy()
        index = 0
        for value in categorys_list.values():
            for cf in value:
                x = cf.x
                y = cf.y
                w = cf.w
                h = cf.h
                cv.rectangle(tempImg, (x, y),
                                (x + w, y + h), color_list[index].value, 2)
                cv.putText(tempImg,str(cf.category_type.value),(x,y),cv.FONT_HERSHEY_COMPLEX,1,(0,0,255),1)
            index += 1
        cv.imwrite('./out/5_cf.jpg', tempImg)

    def classification_by_structure(self, categorys_list):
        """
        二次分类
        """
        for item in categorys_list.get(AreaCategory.INPUT):
            downicon_list = categorys_list.get(AreaCategory.DOWNICON)
            contain_downicon = False
            for icon in downicon_list:
                if is_contain_rect({"x": icon.x, "y": icon.y, "w": icon.w, "h": icon.h}, {"x": item.x, "y": item.y, "w": item.w, "h": item.h}):
                    contain_downicon = True
                    break
            if contain_downicon:
                item.category_type = AreaCategory.SELECT

    def replace_text(self, cfs):
        for item in self._text_list:
            coor = item.get('itemcoord')[0]
            text = item.get('itemstring')
            cfs = list(filter(lambda cf: not((cf.category_type == AreaCategory.TEXT or cf.category_type == AreaCategory.UNKNOW) and is_contain_rect({"x": cf.x, "y": cf.y, "w": cf.w, "h": cf.h}, {"x": coor['x'] -  CommonLimit.diffPix, "y": coor['y'] - CommonLimit.diffPix, "w": coor['width'] + 2 * CommonLimit.diffPix, "h": coor['height'] + 2 * CommonLimit.diffPix})), cfs))
            feature = Feature(x=coor['x'], y=coor['y'], w=coor['width'], h=coor['height'], text=text)
            feature.category_type = AreaCategory.TEXT
            cfs.append(feature)
        return cfs

class Feature:
    def __init__(self, x, y, w, h, rect=None, roi=None, roiGray=None, ratewh=None, offset_bottom=None, offset_bottom_rate=None, offset_top_rate=None, ratew=None, mean=None, area=None, length=None, rateArea=None, max_indx_value=None, cnt_num=None, contour_feature=None, cnt=None, text=None):
        self.roi = roi
        self.roiGray = roiGray
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.ratewh = ratewh
        self.offset_bottom = offset_bottom
        self.offset_bottom_rate = offset_bottom_rate
        self.offset_top_rate = offset_top_rate
        self.ratew = ratew
        self.mean = mean
        self.area = area
        self.length = length
        self.rateArea = rateArea
        self.max_indx_value = max_indx_value
        self.cnt_num = cnt_num
        self.contour_feature = contour_feature
        self.rect = rect
        self.cnt = cnt
        self.text = text

    def calulate_category(self, dropdown_cnt):
        contour_feature = self.contour_feature
        if (contour_feature.get('perimeter') < CommonLimit.diffPix):
            self.category_type = AreaCategory.UNKNOW
            return
        if (contour_feature.get('perimeter') < CommonLimit.textPerimeterLimit and contour_feature.get('area') < CommonLimit.textAreaLimit):
            match_value = cv.matchShapes(self.cnt, dropdown_cnt, 1, 0)
            if match_value < 0.06:
                self.category_type = AreaCategory.DOWNICON
                return
            self.category_type = AreaCategory.TEXT
            return
        if (approximate_same(self.x, 0) or approximate_same(self.y, 0) or approximate_same(self.offset_bottom, 0)) or self.rateArea > CommonLimit.rateMaxLimit:
            self.category_type = AreaCategory.UNKNOW
        elif self.ratew > CommonLimit.gridRatewLimit and approximate_same(self.max_indx_value, CommonLimit.filterGrayValue) and self.h > CommonLimit.gridTop * 2:
            self.category_type = AreaCategory.FILTER
        elif (self.ratew > CommonLimit.gridRatewLimit and self.offset_top_rate > CommonLimit.gridOffsetTopRateLimit):
            self.category_type = AreaCategory.GRID
        elif (not approximate_same(self.ratewh, 1, 0.1) and approximate_inrange(self.h, CommonLimit.buttonHeightMinLimit, CommonLimit.buttonHeightMaxLimit) and self.w < CommonLimit.buttonWidthLimit and approximate_same(self.max_indx_value, CommonLimit.buttonGrayMean) and self.offset_bottom > CommonLimit.offsetBottomLimit):
            self.category_type = AreaCategory.OPERATION_BTN
        elif (approximate_same(self.ratewh, 1, 0.1) and approximate_same(self.h, CommonLimit.paginationButtonHeight) and self.offset_bottom_rate < CommonLimit.paginationOffsetBottomRateLimit):
            self.category_type = AreaCategory.PAGINATION
        elif (approximate_same(self.h, CommonLimit.formItemHeight) and approximate_inrange(self.w, CommonLimit.formInputWidthMinLimit, CommonLimit.formInputWidthMaxLimit) and approximate_same(self.max_indx_value, CommonLimit.formItemBackgroundGray)):
            self.category_type = AreaCategory.INPUT
        else:
            self.category_type = AreaCategory.UNKNOW
