import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ibasis import icolor, iformat


def put_ch_txt(img, text, left, top, color, textSize=20):
    if isinstance(img, np.ndarray):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontStyle = ImageFont.truetype("../assert/font/simhei.ttf", textSize, encoding="utf-8")
    draw.text((left, top), text, color, font=fontStyle)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def put_text_with_auto_font_size(img, text, pos, font, max_width, color, thickness, font_scale=0.7):
    """自适应计算font_scale使得文字不超过max_width

    Args:
        img (cv2.image): ~
        text (str): ~
        pos (tuple|list): (x, y) 
        font (cv2.FONT_): 字体类型
        max_width (number): 最大宽度, 通常是图片的宽
        color (tuple): (0, 255, 0), bgr
        thickness (int): 字体宽度
        default_font_scale (float, optional): 默认字体大小. Defaults to 0.7.
    """
    while True:
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        if text_size[0] > max_width:
            font_scale -= 0.1
        else:
            break
    cv2.putText(img, text, pos, font, font_scale, color, thickness, cv2.LINE_AA)


def draw_polygon(img, polygon, draw_info_keys=None, is_disp_key=True, is_debug=False, **kwargs):
    """ draw polygon on image with text info
    Args:
        img: cv2 image
        polygon(dict): 多边形信息, e.g. {((x1,y1), (x2,y2), ...):{txt:标注文字, attr: xxx}}
        draw_info_keys(list): 需要显示的keys e.g. [txt, attr]
    Returns:
    """
    if isinstance(polygon, list):
        polygon = {pts: None for pts in polygon}

    for i, (coords, info_dic) in enumerate(polygon.items()):
        if 'color' in kwargs:
            color = kwargs['color']
        else:
            color = icolor.get_idx_color(i)
        coords = np.array([list(pt) for pt in coords], dtype=np.int32)
        img = cv2.polylines(img, [coords], 1, color, 1)

        # debug 模式会画出每个点的序号
        if is_debug:
            for j, pt in enumerate(coords):
                cv2.putText(img, str(j), pt, cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=color, thickness=1)

        # {txt:标注文字, attr: xxx} -> 'txt:标注文字,attr:xxx'
        if draw_info_keys is not None:
            if is_disp_key:
                info = ','.join([f'{k}:{v}' for k, v in {_k: _v for _k, _v in info_dic.items() if _k in draw_info_keys}.items()])
            else:
                info = ','.join([f'{v}' for _, v in {_k: _v for _k, _v in info_dic.items() if _k in draw_info_keys}.items()])
            # 将文字打印的起始位置做offset
            pt = coords[-1]
            pt[0] = 0
            if 'offset' in kwargs:
                offset = kwargs['offset']
            else:
                offset = 20
            if pt[1] + offset <= img.shape[0]:
                pt[1] += offset
            # fontScale=0.7 可能出现字符超过图像边界
            put_text_with_auto_font_size(img, info, pt, cv2.FONT_HERSHEY_SIMPLEX, max_width=img.shape[1], color=color, thickness=1)
            
    return img


def draw_polygon_ch(img, polygon, draw_info_keys=None, is_debug=False):
    """ draw polygon on image with text info, KILL func: draw_polygen 乱码问题
    Args:
        img: cv2 image
        polygon(dict): 多边形信息, e.g. {((x1,y1), (x2,y2), ...):{txt:标注文字, attr: xxx}}
        draw_info_keys(list): 需要显示的keys e.g. [txt, attr]
    Returns:
    """
    if isinstance(polygon, list):
        polygon = {pts: None for pts in polygon}

    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    fontStyle = ImageFont.truetype("../assets/font/simhei.ttf", 20, encoding="utf-8")

    for i, (coords, info_dic) in enumerate(polygon.items()):
        color = icolor.get_idx_color(i, mode='rgb')
        coords = np.array([list(pt) for pt in coords], dtype=np.float32)
        draw.polygon(coords, outline=color)

        # debug 模式会画出每个点的序号
        if is_debug:
            for j, pt in enumerate(coords):
                draw.text(pt, str(j), color, font=fontStyle)

        # {txt:标注文字, attr: xxx} -> 'txt:标注文字,attr:xxx'
        if draw_info_keys is not None:
            info = ','.join([v for k, v in {_k: _v for _k, _v in info_dic.items() if _k in draw_info_keys}.items()])
            draw.text(coords[-1], info, color, font=fontStyle)
    img = cv2.cvtColor(np.asarray(pil_img), cv2.COLOR_RGB2BGR)
    return img


def draw_ocr_txt(img_size, txt, bg_color, fg_color):
    # img_size 最好给(300, 32)
    # color, BGR
    img = np.zeros((img_size[1], img_size[0], 3), dtype=np.uint8)
    for i in range(3):
        img[:,:, i] = bg_color[i]
    if is_contain_chinese(txt):
        img = draw.put_ch_txt(img, txt, 0, img_size[1]-20, fg_color, textSize=10)
    else:
        img = cv2.putText(img, txt, (0, img_size[1]-10), cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5, color=fg_color, thickness=1)
    return img


def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


if __name__ == '__main__':
    fontStyle = ImageFont.truetype("../assets/font/simhei.ttf", 20, encoding="utf-8")
