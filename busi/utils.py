import cv2
import time
import math
import warnings
import traceback
import pyclipper
import numpy as np
from functools import wraps
from ibasis import ipath, imath


def check_txt_in_alphabet(txt, alphabet):
    """Check if the text chars are all in the alphabet
    Args:
        txt(str): text to be checked
        alphabet(str): e.g. "ABCD"
    Return:
        is_all_in(bool): if all text char in alphabet, return True
        not_in_lis(list): char(s) not in alphabet
    """
    is_all_in = True
    not_in_lis = [char for char in txt if char not in alphabet]
    if len(not_in_lis) > 0:
        is_all_in = False
    return is_all_in, not_in_lis


def xywh_to_ltrb(xywh, is_int=True):
    """[x,y,w,h] -> [lt, rb]"""
    x, y, w, h = xywh
    h_w = w/2.
    h_h = h/2.
    if is_int:
        return ((int(x-h_w), int(y-h_h)), (int(x+h_w), int(y+h_h)))
    else:
        return ((x-h_w, y-h_h), (x+h_w, y+h_h))


def xywy_to_four_rect_pts(xywh, is_int=True):
    x, y, w, h = xywh
    h_w = w/2.
    h_h = h/2.
    if is_int:
        return (
            (int(x-h_w), int(y-h_h)),
            (int(x+h_w), int(y-h_h)),
            (int(x+h_w), int(y+h_h)),
            (int(x-h_w), int(y+h_h))
        )
    else:
        return (
            (x-h_w, y-h_h),
            (x+h_w, y-h_h),
            (x+h_w, y+h_h),
            (x-h_w, y+h_h)
        )


def expand_polygon(data_dic, expand_dis):
    res_dic = dict()
    for pts, attr_dic in data_dic.items():
        padding = pyclipper.PyclipperOffset()
        padding.AddPath(pts, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        shrinked = padding.Execute(expand_dis)
        if len(shrinked) > 0:
            res_dic[ipoint.fmt_2d_pts(np.array(shrinked[0]).reshape(-1, 2), is_tuple=True, is_int=True)] = attr_dic
        else:
            warnings.warn(f"Data expand polygon error")
    return res_dic


def to_norm_vec(v):
    """向量 -> 单位向量"""
    return v / np.linalg.norm(v)


def is_vec_eq(v1, v2, error=0.01):
    """判断两个向量是否相等
    直接使用以下方式会出现问题, 存在小数后几位不一致, 从而出现异常状况
    (v1 == v2).all()
    """
    return (np.abs((v1 - v2)) < error).all()


def sort_rotate_rect(pts):
    """将任意角度的矩形的四个点进行排序
    Args:
        pts(np.arr): 矩形的四个点 [(x, y), ...], len == 4
    Return:
        tuple((x:int, y:int), ...): 排序后的四个点, (lt, rt, rb, lb)
    流程:
        - 求矩形几何中心
        - 划分左边点和右边点
        - 找到左边点对角点
        - 找出lb点
        - 确定所有点的顺序
    注意:
        此方法只适用于矩形, 四边形和多边形均不适用
    """
    # 求矩形几何中心
    center_pt = np.mean(pts, axis=0)
    # 划分左边点和右边点
    x_left_lis, x_right_lis = list(), list()
    for pt in pts:
        if pt[0] < center_pt[0] or (pt[0]==center_pt[0] and pt[1] < center_pt[1]):
            x_left_lis.append(pt)
        else:
            x_right_lis.append(pt)
    # 找到左边点对角点
    search_idxs = [[0, 0], [0, 1]]
    matched = []
    for l, r in search_idxs:
        l1_pt = x_left_lis[l]
        r1_pt = x_right_lis[r]
        l2_pt = x_left_lis[1-l]
        r2_pt = x_right_lis[1-r]
        v1 = to_norm_vec(r2_pt - l1_pt)
        v2 = to_norm_vec(r1_pt - l2_pt)
        # 四边形需要修改此处
        if is_vec_eq(v1, v2):
            matched = [[l, r], [1-l, 1-r]]
            break
    # 找出lb点
    ld = x_left_lis[0]
    if x_left_lis[1][1] > x_left_lis[0][1]:
        ld = x_left_lis[1]
    # 确定所有点的顺序
    sorted_pts = list()
    for l, r in matched:
        if is_vec_eq(x_left_lis[l], ld):
            sorted_pts = [
                x_left_lis[1-l],
                x_right_lis[r],
                x_right_lis[1-r],
                x_left_lis[l]
            ]
            break
    return tuple([(int(xy[0]), int(xy[1])) for xy in sorted_pts])


def four_pts_transform(img, pts, opt_size=(100, 32)):
    """从图片中截取四边形->指定大小矩形
    Args:
        img(cv2): 任意图片
        pts(np.arr): 有顺序的四边形点, [lt, rt, rb, lb]
    Return:
        cv2格式图片: 截取出的图片
    注意:
        默认pts点都在图片内
    """
    tgt_pts = [
        [0, 0],
        [opt_size[0]-1, 0],
        [opt_size[0]-1, opt_size[1]-1],
        [0, opt_size[1]-1]
    ]
    # notice: roi_det & dst dtype should be np.float32
    try:
        perspective_M = cv2.getPerspectiveTransform(np.array(pts, dtype=np.float32), np.array(tgt_pts, dtype=np.float32))
        img = cv2.warpPerspective(img, perspective_M, opt_size)
    except:
        traceback.print_exc()
        warn_info = f"Perspective transform failed. src pts: {pts}, dst pts: {tgt_pts}, Perspective_M: "
        if 'perspective_M' in locals().keys():
            warn_info += f"True, M: {perspective_M}"
        else:
            warn_info += 'False'
            
        img = None
    return img


def get_min_area_rect(pts):
    """获取polygon的最小外接矩形
    Args:
        pts(np.arr, list): polygon points, e.g. [(x,y), ...]
    Return:
        four rect points: order [lt, rt, rb, lb]
    """
    pts = np.array(pts)
    hw_angle = cv2.minAreaRect(pts)
    four_rotate_rect_pts = cv2.boxPoints(hw_angle)
    four_rotate_rect_pts = sort_rotate_rect(four_rotate_rect_pts)
    return four_rotate_rect_pts


def expand_quad(quad_pts, expand_dis, size=None):
    """将四边形按照给定距离进行扩大
    Args:
        quad_pts(np.arr, list): four points, [lt, rt, rb, lb]
        expand_dis(list): [lt, rt, rb, lb]
        size(tuple): (W, H)
    Return:
        expanded_quad_pts:
    """
    # 简易版本
    # TODO: 考虑边界情况
    lt, rt, rb, lb = quad_pts
    lt_o, rt_o, rb_o, lb_o = expand_dis
    l, t, r, b = [8,0,5,0]
    lt = [lt[0]-l, lt[1]-t]
    rt = [rt[0]+r, rt[1]-t]
    rb = [rb[0]+r, rb[1]+b]
    lb = [lb[0]-l, lb[1]+b]
    _pts = [lt, rt, rb, lb]
    return tuple([(int(xy[0]), int(xy[1])) for xy in _pts])



def get_rotate_rect_info(rotate_rect):
    """[lt, rt, rb, lb] 获取(lb-rb) 与x轴夹角, 宽Len(lt, rt), 高Len(lt, rb)"""
    lt, rt, rb, lb = np.array(rotate_rect)
    v_lbrb = rb-lb
    deg = math.degrees(math.acos(imath.cos2x(v_lbrb)))   # 与y轴正方向夹角
    # deg = 90 - deg
    W = imath.calc_eula_dis(rb, lb)
    H = imath.calc_eula_dis(lb, lt)
    return W, H, deg
    


def timeit_return(func):
    @wraps(func)
    def _timeit(*args, **kwargs):
        st = time.time()
        res = func(*args, **kwargs)
        used = round((time.time() - st) * 1000, 3)
        return res, used
    return _timeit


def timeit_print(func):
    @wraps(func)
    def _timeit(*args, **kwargs):
        st = time.time()
        res = func(*args, **kwargs)
        print(f"Function {func.__name__} used [{(time.time() - st) * 1000:.3f}] ms")
        return res
    return _timeit


def timeit_record(used, is_ms=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            st = time.time()
            res = func(*args, **kwargs)
            used[0] = time.time() - st
            if is_ms:
                used[0] *= 1000
            used[0] = round(used[0], 3)
            return res
        return wrapper
    return decorator

# example
used = [0]
@timeit_record(used=used, is_ms=True)
def _t():
    time.sleep(1)
    print(1)
