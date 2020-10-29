from ocr import ocr
from img_process import ImgProess
from get_schema import GetSchema
from feature_classification import FeatureClassification
from render import Render

PROCESS_IMG_PATH = './in/mq.jpg'
DROPDOWN_ICON_PATH = './in/icon/arrow.jpg'
TMEPLATE_PATH = './template'
TEMPLATE_OUT_PATH = './template-out'

def main():
    text_list = get_text_list()
    if len(text_list) == 0:
        raise RuntimeError('ocr请求失败')
    contours, img = ImgProess(PROCESS_IMG_PATH).get_contours(True)
    dropdown_cnt = get_dropdown_contour()
    feature_classfication = FeatureClassification(cnts=contours, text_list=text_list, dropdown_cnt=dropdown_cnt, img=img)
    categorys_list = feature_classfication.run()
    schema = GetSchema(categorys_list=categorys_list, img=img).run()
    Render(TMEPLATE_PATH, TEMPLATE_OUT_PATH, schema)

def get_text_list():
    return ocr(PROCESS_IMG_PATH)

def get_dropdown_contour():
    cnts, img = ImgProess(DROPDOWN_ICON_PATH).get_contours(False)
    dropdown_cnt = cnts[0]
    return dropdown_cnt

if __name__ == "__main__":
    # execute only if run as a script
    main()
