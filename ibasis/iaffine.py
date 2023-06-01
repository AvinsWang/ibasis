import math
import numpy as np
from typing import Tuple
from numpy.random import uniform


class AffineMatrix(object):
    def __init__(self, M=None):
        if M is None:
            M = np.eye(3, dtype=np.float32)
        self.M = M

    def translate_(self, du, dv):
        M = np.array([
            [1, 0, du],
            [0, 1, dv],
            [0, 0,  1]
        ], dtype=np.float32)
        self._mul(M)
        return self

    def rotate_(self, rad):
        cr, sr = np.cos(rad), np.sin(rad)
        M = np.array([
            [cr,  sr, 0],
            [-sr, cr, 0],
            [0,    0, 1]
        ], dtype=np.float32)
        self._mul(M)
        return self

    def scale_(self, su, sv):
        M = np.array([
            [su, 0, 0],
            [0, sv, 0],
            [0,  0, 1]
        ], dtype=np.float32)
        self._mul(M)
        return self

    def shear_(self, x_rad, y_rad):
        tx, ty = np.tan(x_rad), np.tan(y_rad)
        M = np.array([
            [1,   -tx,      0],
            [-ty, tx*ty+1,  0],
            [0,   0,        1]
        ], dtype=np.float32)
        self._mul(M)
        return self

    def _mul(self, M):
        self.M = M @ self.M     # 左乘


def get_random_params(degree_range=None, translate_range=None, scale_range=None, shear_range=None):
    deg = uniform(*degree_range) if degree_range is not None else 0

    translation = (0, 0)
    if translate_range is not None:
        max_dx, max_dy = translate_range
        translation = (int(uniform(-max_dx, max_dx)), int(uniform(-max_dy, max_dy)))

    scale = 1.0
    if scale_range is not None:
        scale = uniform(*scale_range)

    shear_x = shear_y = 0.0
    if shear_range is not None:
        shear_x = uniform(*shear_range[:2])
        if len(shear_range) == 4:
            shear_y = uniform(*shear_range[2:])
    shear = (shear_x, shear_y)

    return [deg, shear, translation, (scale, scale)]


def get_affine_matrix(center, deg=None, shear=None, translate=None, scale=None):
    aff_mat = AffineMatrix()
    aff_mat.translate_(du=-center[0], dv=-center[1])
    if deg is not None:
        rot = math.radians(deg)
        aff_mat.rotate_(rot)
    if shear is not None:
        sx, sy = [math.radians(s) for s in shear]
        aff_mat.shear_(x_rad=sx, y_rad=sy)
    aff_mat.translate_(du=center[0], dv=center[1])
    if translate is not None:
        aff_mat.translate_(*translate)
    if scale is not None:
        if isinstance(scale, tuple):
            aff_mat.scale_(su=scale[0], sv=scale[1])
        else:
            aff_mat.scale_(su=scale, sv=scale)
    return aff_mat.M


def get_random_affine_matrix(center=None, degree_range=None, translate_range=None, scale_range=None, shear_range=None):
    _params = get_random_params(degree_range, translate_range, scale_range, shear_range)
    return _params, get_affine_matrix(center, *_params)


def __test_cv2(img_path, params):
    img = cv2.imread(img_path)
    img_src = copy.copy(img)
    h, w, _ = img.shape
    center = (w/2, h/2)
    _params, M = get_random_affine_matrix(center=center, **params)
    dsize = int(w*_params[-1][0]), int(h*_params[-1][1]),
    # su, sv = 2, 2
    # M = get_affine_matrix(center=center, degree=10, translate=(0, 0), scale=(su, sv), shear=(0, 0))
    M = np.delete(M, 2, axis=0)
    
    img = cv2.warpAffine(img, M, dsize)

    cv2.imwrite('__tmp_affine.jpg', img)


def __test_PIL(img_path, params):
    img = Image.open(img_path)
    img_src = copy.copy(img)
    w, h = img.size
    center = (w*0.5, h*0.5)
    M = get_random_affine_matrix(center=center, **params)
    # M = get_affine_matrix(center=center, degree=0, translate=(0, 0), scale=0.5, shear=(0, 0))
    M = np.delete(M, 2, axis=0)
    img = img.transform((w, h), Image.AFFINE, M.flatten(), resample=Image.BILINEAR)
    img.show('11')

    # img_show = np.concatenate([img_src, img], axis=1)
    # cv2.imshow('concat', img_show)
    # cv2.imshow('trans', img)
    # cv2.waitKey(0)


if __name__ == '__main__':
    import copy
    from PIL import Image

    img_path = 'asset/lena.jpg'
    params = dict(
        degree_range=(-60, 60),
        translate_range=(50, 50),
        scale_range=(0.5, 2),
    )
    __test_cv2(img_path, params)
    # __test_PIL(img_path)
