import cv2
import numpy as np
from . import icolor


def draw_pts_as_line(img, pts_lis, color, thickness=1):
    """pts_lis: [[x,y], [x,y], ...]"""
    pts_lis = np.array(pts_lis).astype(int)
    return cv2.polylines(img, [pts_lis], color=color, thickness=thickness, isClosed=False)


def draw_pts_as_dot(img, pts_lis, color, radius=1, is_debug=False):
    """pts_lis: [[x,y], [x,y], ...]"""
    for i, xy in enumerate(pts_lis):
        img = cv2.circle(img, (int(xy[0]), int(xy[1])), radius=radius, color=color, thickness=-1)
        if is_debug:    # 画出点的顺序
            img = cv2.putText(img, str(i), (int(xy[0]), int(xy[1])), cv2.FONT_HERSHEY_COMPLEX, 1, color, 1)
    return img


def draw_txt(img, pt, color, info, front_scale=0.8, thickness=1, is_refine=True):
    H, W = img.shape[:2]
    x, y = list(map(int, pt))
    if is_refine:
        x = np.clip(x, 50, W-100)
        y = np.clip(y, 50, H-50)
    return cv2.putText(img, info, (x, y), cv2.FONT_HERSHEY_COMPLEX,
                       fontScale=front_scale, color=color, thickness=thickness)


# === MASK ===

def draw_pts_as_line_mask(img, pts_lis, color, thickness=1):
    """pts_lis: [[x,y], [x,y], ...]"""
    pts_lis = np.array(pts_lis).astype(int)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    mask = cv2.polylines(mask, [pts_lis], color=255, thickness=thickness, isClosed=False)
    mask = mask.astype(bool)
    color_mask = np.array(color, dtype=np.uint8)
    img[mask] = img[mask] * 0.7 + color_mask * 0.3
    return img


def draw_pts_as_dot_mask(img, pts_lis, color, radius=1, is_debug=False):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for i, xy in enumerate(pts_lis):
        mask = cv2.circle(mask, list(map(int, xy)), radius=radius, color=255, thickness=-1)
    mask = mask.astype(bool)
    color_mask = np.array(color, dtype=np.uint8)
    img[mask] = img[mask] * 0.7 + color_mask * 0.3
    return img


def draw_mask_on_img(img, msk, msk_dtype='uint8', msk_type='class', idx_color_offset=0, color=None, exclude_color=None):
    """Draw mask on image
    Args:
        img (cv2): channel = 3, gray
        msk (np.arry): dtype=np.uint8 or np.float
        msk_dtype (str): the data type of input, uint8 or float
        msk_type (str): 'class': each pixel value represent a class,
                        'heatmap' : [0~1]  
    Returns:
        img: img with mask
    """
    def draw_single_mask(_img, _msk, _msk_dtype, _msk_type, color=None, exclude_color=None):
        if _msk_type == 'class':
            for i in np.unique(_msk):
                i = int(i)
                if i == 0:
                    continue
                if color is None:
                    color = icolor.get_idx_color(i+idx_color_offset, exclude=exclude_color)
                msk_i = np.zeros_like(_img)
                msk_i[_msk == i] = color
                _img = cv2.addWeighted(_img, 1, msk_i, 0.5, 0)
        elif _msk_type == 'heatmap':
            if _msk_dtype == 'float':
                _msk = (_msk * 255).astype(np.uint8)
            # if len(img_shape) == 2:
            #     msk = np.tile(msk[..., None], axis=[1,1,3])
            _msk[_msk==0] = 1
            _msk = cv2.applyColorMap(_msk, cv2.COLORMAP_JET)
            _msk[_msk==1] = 0
            _img = cv2.addWeighted(_img, 1, _msk, 0.5, 0)
        return _img
    
    img_shape = img.shape
    msk_shape = msk.shape
    assert img_shape[:2] == msk_shape[:2]
    if len(img_shape) == 2:
        img = np.tile(img[..., None], axis=[1,1,3])
    if len(msk_shape) == 2:
        img = draw_single_mask(img, msk, msk_dtype, msk_type, color, exclude_color)
    else:
        for i in range(3):
            _msk = msk[..., i]
            img = draw_single_mask(img, _msk, msk_dtype, msk_type, color, exclude_color)
    return img