from enums import AreaCategory, CommonLimit
from functools import cmp_to_key


def approximate_same(*args):
    if (len(args) == 2):
        a, b = args
        return abs(a-b) < CommonLimit.diffPix
    else:
        a, b, x = args
        return abs(a-b) < x


def approximate_inrange(data, a, b):
    return data >= a - CommonLimit.diffPix and data <= b + CommonLimit.diffPix


def approximate_enumsame(v, my_enum):
    r = []
    for item in my_enum:
        r.append({"diff": abs(item.value - v), "item": item})
    r.sort(key=lambda elem: elem["diff"])
    if r[0]["diff"] < CommonLimit.diffPix:
        return r[0]["item"].name
    else:
        return False


def is_same_range(r1, r2):
    diffPix = CommonLimit.diffPix
    return abs(r1[0] - r2[0]) < diffPix/2 and abs(r1[1] - r2[1]) < diffPix/2 and abs(r1[2] - r2[2]) < diffPix/2 and abs(r1[3] - r2[3]) < diffPix/2

def is_contain_rect(rect1, rect2):
    # rect1 in rect2
    return rect1['x'] >= rect2['x'] and rect1['y'] >= rect2['y'] and rect1['x'] + rect1['w'] <= rect2['x'] + rect2['w'] and rect1['y'] + rect1['h'] <= rect2['y'] + rect2['h']

def reorganize(cfs):
    def my_sort(cf1, cf2):
        center1_y = cf1.y + cf1.h / 2
        center1_x = cf1.x + cf1.w / 2
        center2_y = cf2.y + cf2.h / 2
        center2_x = cf2.x + cf2.w / 2
        if center1_y - center2_y > CommonLimit.diffPix:
            return 1
        elif center1_y - center2_y < -CommonLimit.diffPix:
            return -1
        elif center1_y - center2_y > -CommonLimit.diffPix and  center1_y - center2_y < CommonLimit.diffPix:
                if center1_x - center2_x > CommonLimit.diffPix:
                    return 1
                elif center1_x - center2_x < -CommonLimit.diffPix:
                    return -1
                elif center1_x - center2_x > -CommonLimit.diffPix and  center1_x - center2_x < CommonLimit.diffPix:
                    return 0
        return 0
    return sorted(cfs, key = cmp_to_key(my_sort))

def str_find_in_list(s, t_list):
    return any([s.find(item) != -1 for item in t_list])