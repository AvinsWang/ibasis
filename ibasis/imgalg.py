import cv2
import math
import traceback
import numpy as np
from scipy.spatial import ConvexHull
from .imath import (to_norm_vec, is_vec_eq, calc_eula_dis, cos2x)


def calc_polygon_main_direction(polygon):
    """计算polygon的主方向

    Args:
        polygon (list): [[x,y], ...]
    Returns:
        (x, y): norm to [0, 1] 
    """
    hull = ConvexHull(polygon)
    hull_points = np.zeros((len(hull.vertices), 2))
    for i, vertex_index in enumerate(hull.vertices):
        hull_points[i, :] = polygon[vertex_index]
    
    # 计算主方向
    pca = np.linalg.svd(hull_points - np.mean(hull_points, axis=0))[2]
    main_direction = pca[0, :]
    
    return main_direction


def sort_rotate_rect(pts, error=0.01):
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
    if len(x_left_lis) != len(x_right_lis):
        # 左边有三个点
        if len(x_left_lis) > len(x_right_lis):
            x_left_lis = sorted(x_left_lis, key=lambda x:x[1])
            x_right_lis.append(x_left_lis.pop(0))
        else:
            x_right_lis = sorted(x_right_lis, key=lambda x:x[1], reverse=True)
            x_left_lis.append(x_right_lis.pop(0))
        
    matched = []
    for l, r in search_idxs:
        l1_pt = x_left_lis[l]
        r1_pt = x_right_lis[r]
        l2_pt = x_left_lis[1-l]
        r2_pt = x_right_lis[1-r]
        v1 = to_norm_vec(r2_pt - l1_pt)
        v2 = to_norm_vec(r1_pt - l2_pt)
        # 四边形需要修改此处
        if is_vec_eq(v1, v2, error):
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


def four_pts_transform(img, pts, opt_size=(100, 32), fill_value=0):
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


def get_min_area_rect(pts, is_sort=True):
    """获取polygon的最小外接矩形
    Args:
        pts(np.arr, list): polygon points, e.g. [(x,y), ...]
    Return:
        four rect points: order [lt, rt, rb, lb]
    """
    pts = np.array(pts)
    cxcy_hw_angle = cv2.minAreaRect(pts)
    four_rotate_rect_pts = cv2.boxPoints(cxcy_hw_angle)
    if is_sort:
        four_rotate_rect_pts = sort_rotate_rect(four_rotate_rect_pts)
    return four_rotate_rect_pts



def get_rotate_rect_info(rotate_rect):
    """[lt, rt, rb, lb] 获取(lb-rb) 与x轴夹角, 宽Len(lt, rt), 高Len(lt, rb)"""
    lt, rt, rb, lb = np.array(rotate_rect)
    v_lbrb = rb-lb
    deg = math.degrees(math.acos(cos2x(v_lbrb)))   # 与y轴正方向夹角
    # deg = 90 - deg
    W = calc_eula_dis(rb, lb)
    H = calc_eula_dis(lb, lt)
    return W, H, deg