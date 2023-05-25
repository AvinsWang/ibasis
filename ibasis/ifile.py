import os
import shutil
import os.path as osp
from tqdm import tqdm

from . import ipath


def migrate(dir_, out_dir, kw=None, mode='cp'):
    """将目录中含有关键词的文件复制/拷贝到指定文件夹
    Args:
        dir_: 目录
        out_dir: 输出路径
        kw: 包含的关键词
        mode: 'cp' or 'mv'
    Returns:
    """
    path_dic = ipath.get_paths(dir_, file_type='IMAGE', key_mode=1)
    cnt = 0
    for key, path in tqdm(path_dic.items()):
        if kw in path:
            dst_path = osp.join(out_dir, key)
            if mode == 'mv':
                shutil.move(path, dst_path)
            if mode == 'cp':
                shutil.copy(path, dst_path)
            print(mode, path, '->', dst_path)
            cnt += 1
    print(f"迁移{cnt}/{len(path_dic)}")


if __name__ == '__main__':
    pdir = '/data1/dataset/lanedet_online_dataset'
    dir_ = '/data1/dataset/lanedet_online_dataset/raw/x3p10_2022-10-19/images_reserve'
    outdir = '/data1/dataset/lanedet_online_dataset/raw_merge/images'
    os.makedirs(outdir, exist_ok=True)
    migrate(dir_, outdir, kw='images_reserve', mode='cp')
