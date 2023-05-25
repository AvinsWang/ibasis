# 检查图片完整性
# 在传输过程中是否损坏

import os
import cv2
import numpy as np
from p_tqdm import p_map
from functools import partial
from . import ishell, ipath


cv2.ocl.setUseOpenCL(False)
cv2.setNumThreads(0)


# === 图片完整性检查 ===
def _check_cv2(fpath):
    if cv2.imread(fpath) is not None:
        return True
    return False


def _check_identify(fpath):
    res = ishell.exec_shell(f"identify {fpath}", decode_type='utf-8', is_res=True)
    if 'insufficient' in res or 'error' in res:
        return False
    return True


def _check_img_integrity(fpath, is_del=False, mode='identify'):
    if mode == 'cv2':
        f = _check_cv2(fpath)
    if mode == 'identify':
        f = _check_identify(fpath)
    if f is False:
        if is_del:
            os.remove(fpath)
        print(f"发现缺损图片, 是否删除: {is_del}, {fpath}")
    return f


def check_img_integrity(dir_, is_del=False, file_type='IMAGE', mode='identify'):
    path_lis = ipath.get_paths(dir_, file_type=file_type, key_mode=3, is_lis=True)
    print(f"开始扫描缺损图片目录: {dir_}, 是否删除: {is_del}, 图片数量: {len(path_lis)}")
    if len(path_lis) == 0:
        print(f"图片数量为0, 结束!")
        return
    
    # check identify package 是否存在
    if mode == 'identify':
        res = ishell.exec_shell(f"identify {path_lis[0]}", decode_type='utf-8', is_res=True, is_verbose=True)
        if len(res) == 0:
            raise RuntimeError('identify not be installed, plz install imagemagick to use it.')

    func = partial(_check_img_integrity, is_del=is_del, mode=mode)
    res = p_map(func, path_lis, num_cpus=0.95)
    res = ~np.array(res).astype(bool)
    print(f"损坏/总数: {sum(res)}/{len(path_lis)}")


if __name__ == '__main__':
    check_img_integrity('/data/ocr_dataset/localization/neolix/neolix_1st/images', is_del=False, mode='cv2')