from img_process import ImgProess
from enums import AreaCategory, CommonLimit, ButtonSize, Color, FormItemType
from util import approximate_same, approximate_inrange, approximate_enumsame, is_same_range, is_contain_rect, reorganize

class GetSchema:
    def __init__(self, categorys_list, img):
        self._img = img
        self._grid_list = categorys_list.get(AreaCategory.GRID) or []
        self._operation_list = categorys_list.get(AreaCategory.OPERATION_BTN) or []
        self._paginationList = categorys_list.get(AreaCategory.PAGINATION) or []
        self._text_list = categorys_list.get(AreaCategory.TEXT) or []
        self._filter_list = categorys_list.get(AreaCategory.FILTER) or []
        self._input_list = categorys_list.get(AreaCategory.INPUT) or []
        self._select_list = categorys_list.get(AreaCategory.SELECT) or []

    def run(self):
        grid_schema = self.get_grid_schema()
        operation_schema = self.get_operation_schema()
        filter_schema = self.get_filter_schema()
        print(grid_schema, operation_schema, filter_schema)
        return {"grid_schema": grid_schema, "operation_schema": operation_schema, "filter_schema": filter_schema}
    
    def get_grid_core_area(self):
        grid_dict = {}
        x_left_top = y_left_top = x_right_bottom = y_right_bottom = -1
        for item in self._grid_list:
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
        x_left_top_t, y_left_top_t, x_right_bottom_t, y_right_bottom_t = self.find_grid_top_rect(
            x_left_top, y_left_top, x_right_bottom, y_right_bottom)
       
        # grid_dict['centerList'] = center_list
        grid_dict['cloumns'] = [x_left_top_t,
                                    y_left_top_t, x_right_bottom_t, y_right_bottom_t]
        return grid_dict

    def get_grid_schema(self):
        grid_dict = self.get_grid_core_area()
        columns_area = grid_dict.get('cloumns')
        contain_cfs = self.in_rect_cfs({'x': columns_area[0], 'y': columns_area[1], 'w': columns_area[2] - columns_area[0], 'h': columns_area[3] - columns_area[1]}, self._text_list)
        grid_schema = {"grid_column": []}
        for cf in contain_cfs:
            text = cf.text
            grid_schema['grid_column'].append({"title": text})
        return grid_schema

    def in_rect_cfs(self, rect, cfs):
        contain_cfs = [cf for cf in cfs if is_contain_rect({"x": cf.x, "y": cf.y, "w": cf.w, "h": cf.h}, rect)]
        contain_cfs.sort(key= lambda cf: cf.x)
        return contain_cfs

    def get_operation_schema(self):
        result = []
        for btnCf in self._operation_list:
            contain_cfs = self.in_rect_cfs({'x': btnCf.x, 'y': btnCf.y, 'w': btnCf.w, 'h': btnCf.h}, self._text_list)
            text = contain_cfs[0].text
            size = approximate_enumsame(btnCf.h, ButtonSize)
            btn_type = 'primary' # 后续识别
            result.append({"text": text, "size": size, "x-left": btnCf.x})

        return result

    def get_filter_schema(self):
        filter_schema = {"has_wrapper": False, "items": []}
        if len(self._filter_list) > 0:
            filter_schema["has_wrapper"] = True
        form_item_list = self._input_list + self._select_list
        form_item_list = reorganize(form_item_list)
        row = 0
        before_cf = None
        for form_item_cf in form_item_list:
            if before_cf and form_item_cf.y - before_cf.y > CommonLimit.formItemHeightMarginLimit:
                row += 1
            before_cf = form_item_cf
            label = ''
            for text_cf in self._text_list:
                if approximate_same(text_cf.x + text_cf.w, form_item_cf.x, CommonLimit.formItemLeftTextLimit) and approximate_same(text_cf.y, form_item_cf.y, 5*CommonLimit.diffPix):
                    label = text_cf.text
                    break
            filter_schema["items"].append({"label": label, "type": FormItemType.get(form_item_cf.category_type.name), "row": row})
        return filter_schema

    def find_grid_top_rect(self, x_left_top, y_left_top, x_right_bottom, y_right_bottom):
        return x_left_top, y_left_top, x_right_bottom,  y_left_top+CommonLimit.gridTop
