# coding: utf-8
"""数学计算的公用函数"""
import math
import numpy as np

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def calc_diffs(list_, op='-', N=None, is_tail=False, ndigits=None):
    """
    获取list中的两两差值
    :param list_: 输入数据, list或np.array
    :param N: 需要计算的的差值个数, 即输出值的长度, 如果N>len(list_), N=len(list_)
    :param is_tail: 从尾部开始计算
    :return: list, 两两的差值
    e.g. list_ = [1, 2, 4, 7, 11, 16]
    默认参数:           >>> [1, 2, 3, 4, 5]
    N=2, is_tail=False >>> [1,2]
    N=2, is_tail=True  >>> [4,5]
    """
    L = len(list_)
    N = L if N is None else N
    _range = range(max(L - N, 1), L) if is_tail else range(1, min(N + 1, L))
    if op == '-':
        return [round(list_[i] - list_[i - 1], ndigits) for i in _range]
    if op == '+':
        return [list_[i] + list_[i - 1] for i in _range]
    if op == '/':
        return [list_[i] / list_[i - 1] for i in _range]
    if op == '*':
        return [list_[i] * list_[i - 1] for i in _range]


def get_line_eq(xa, xb):
    """给定两点计算直线k, b"""
    x1, y1 = xa
    x2, y2 = xb
    delta_x = x2 - x1
    if delta_x == 0:
        k = 0
    else:
        k = (y2 - y1) / delta_x
    b = y2 - k * x2
    return k, b


def get_line_eq_pred(x, k, b):
    """计算y=k*x+b"""
    return k * x + b


def calc_eula_dis(pt1, pt2):
    return np.linalg.norm(np.array(pt2) - np.array(pt1))


def calc_cos(a, b):
    # a = np.array([1, 2])
    # b = np.array([3, 4])
    cos = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return cos


def cos2x(a):
    r = calc_eula_dis(a, [0, 0])
    if r == 0:
        return 0
    return a[0] / r

def cos2y(a):
    r = calc_eula_dis(a, [0, 0])
    if r == 0:
        return 0
    return a[1] / r


def dis_pt_to_line(pt, l0, l1):
    pt = np.array(pt)
    l0 = np.array(l0)
    l1 = np.array(l1)
    vec0 = l0 - pt
    vec1 = l1 - pt
    dis = np.abs(np.cross(vec0, vec1)) / np.linalg.norm(l0-l1)
    return dis


def angle_to_x_axis(x, y):
    angle = math.atan2(y, x)
    angle_degrees = math.degrees(angle)
    return angle_degrees


def to_norm_vec(v):
    """向量 -> 单位向量"""
    return v / np.linalg.norm(v)


def is_vec_eq(v1, v2, error=0.01):
    """判断两个向量是否相等
    直接使用以下方式会出现问题, 存在小数后几位不一致, 从而出现异常状况
    (v1 == v2).all()
    """
    return (np.abs((v1 - v2)) < error).all()



if __name__ == '__main__':
    # point = np.array([5,2])
    # line_point1 = np.array([2,2])
    # line_point2 = np.array([3,3])
    # print(dis_pt_to_line(point,line_point1,line_point2))
    x = cos2x([1,1])
    import math
    print(math.degrees(math.acos(x)))
    
    print(x)