import random, string, hashlib, time, base64, json
from urllib.parse import quote
import requests

APP_ID = "2157142779"
APP_KEY = "2LigVCF8Qu9IPNO2"

def ocr(img_path):
    params = getParam(img_path)
    if params:
        return request(params)

def getParam(img_path):

    # 获得时间戳(秒级)，防止请求重放
    time_stamp = int(time.time())
    # 获得随机字符串，保证签名不被预测
    nonce_str = ''.join(random.sample(
        string.ascii_letters + string.digits, 10))

    with open(img_path, 'rb') as f:
        image_data = f.read()
        base64_data = base64.b64encode(image_data)  # base64编码
        img_base64_str = str(base64_data,'utf-8')
        # 组合参数（缺少sign，其值要根据以下获得）
        params = {
            'app_id': str(APP_ID),
            'time_stamp': str(time_stamp),
            'nonce_str': nonce_str,
            'image': img_base64_str,
        }
        # 获得sign对应的值
        sign_before = ''
        # 对key排序拼接
        for key in sorted(params):
            sign_before += '{}={}&'.format(key,quote(params[key], safe=''))
        # 将应用秘钥以app_key为键名，拼接到before_sign的末尾
        sign_before += 'app_key={}'.format(APP_KEY)
        # 对获得的before_sign进行MD5加密（结果大写），得到借口请求签名
        sign = hashlib.md5(sign_before.encode("utf-8")).hexdigest().upper()
        # 将请求签名添加进参数字典
        params["sign"] = sign
        return params
    return False

def request(params):
    url = "https://api.ai.qq.com/fcgi-bin/ocr/ocr_generalocr"
    res = requests.post(url=url, data=params)
    print(res.status_code)
    if int(res.status_code) == 200:
        data = res.json()["data"]["item_list"]
    else:
        data = []
    return data
