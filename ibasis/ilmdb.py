import os
import cv2
import six
import lmdb
import numpy as np
import os.path as osp
from PIL import Image
from tqdm import tqdm
from p_tqdm import p_map
import matplotlib.pyplot as plt
from . import ipath


class LMDB:
    def __init__(self, lmdb_dir, cache_dic=None, map_size=1099511627776):
        # cache_dic both k,v should be byte
        # map_size(KB), default=1T
        self.lmdb_dir = lmdb_dir
        self.cache_dic = cache_dic
        self.env = lmdb.open(lmdb_dir, map_size)

    def _cvt_key(self, key):
        # expect key: int float str
        return key.encode() if not isinstance(key, bytes) else key

    def write(self, append_cache_dic={}):
        assert isinstance(append_cache_dic, dict), "append_cache should be dict"
        append_cache_dic.update(self.cache_dic)
        with self.env.begin(write=True) as txn:
            for k, v in append_cache_dic.items():
                txn.put(self._cvt_key(k), self._cvt_key(v))

    def get(self, key):
        key = self._cvt_key(key)
        with self.env.begin() as txn:
            return txn.get(key)

    def get_all(self, only_key=False, only_value=False, include=None):
        with self.env.begin() as txn:
            for key, value in txn.cursor():
                if include is not None:
                    if include not in str(key.decode()):
                        continue
                if only_key:
                    yield str(key.decode())
                elif only_value:
                    yield value
                else:
                    yield str(key.decode()), value

    def __del__(self):
        self.env.close()


class LMDB_OCR(LMDB):
    def __init__(self, lmdb_dir, cache_dic=None, map_size=1099511627776):
        super(LMDB_OCR, self).__init__(lmdb_dir, cache_dic, map_size)

    def _cvt_imgbuf_to_img(self, key, imgbuf):
        buf = six.BytesIO()
        buf.write(imgbuf)
        buf.seek(0)
        try:
            img = Image.open(buf)
        except IOError:
            img = None
            print(f"Convert imgbug -> pil.img failed with key: {key.decode() if isinstance(key, bytes) else key}")
        return img

    def get_img(self, key):
        imgbuf = self.get(key)
        return self._cvt_imgbuf_to_img(key, imgbuf)

    def get_lbl(self, key):
        key = self._cvt_key(key)
        return str(self.get(key).decode())

    def get_batch_img(self, batchs_size=None, is_shuffle=False):
        k_lis = list(self.get_all(only_key=True, include='image'))
        if is_shuffle:
            np.random.shuffle(k_lis)
        if batchs_size is not None:
            k_lis = k_lis[:batchs_size]
        for k in k_lis:     # k: str here
            yield k, self.get_img(k)

    def write(self, append_cache_dic={}):
        super().write(append_cache_dic)
        append_cache_dic.update(self.cache_dic)
        with self.env.begin(write=True) as txn:
            txn.put(b'num-samples', str(len(append_cache_dic)//2).encode())

def write(arg):
    cv2.imwrite(arg[0], arg[1])

def gen_img_lbl(lmdb_dir, out_dir):
    locr = LMDB_OCR(lmdb_dir)
    img_dir = osp.join(out_dir, 'images')
    lbl_dir = osp.join(out_dir, 'labels')
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lbl_dir, exist_ok=True)
    res_lis = []
    path_dic = ipath.get_paths(img_dir, key_mode=0)
    arg_lis = []
    for k in tqdm(locr.get_all(only_key=True)):
        if k in path_dic:
            continue
        if 'image' in k:
            continue
            img = np.array(locr.get_img(k), dtype=np.uint8)
            cv2.imwrite(osp.join(img_dir, f"{k}.jpg"), img)
        if 'label' in k:
            res_lis.append(f"{k.replace('label', 'image')}.jpg,{locr.get_lbl(k)}\n")
    print(len(res_lis))
    with open(osp.join(lbl_dir, 'labels.txt'), 'w') as f:
        f.writelines(res_lis)

def __test():
    lmdb_dir = '/code/ocr/ocr_pipeline/text_render/__data/eng_1M/train'
    # lmdb_dir = 'data/0217/0217_7.5k'
    # lmdb_dir = '/code/ocr/NeoOCR/data/0215_cus/val_72'
    locr = LMDB_OCR(lmdb_dir)
    print(locr.get('num-samples'))
    print(list(locr.get_all(only_key=True))[:10])
    batch_img = locr.get_batch_img(batchs_size=20, is_shuffle=True)
    tmp_out = '/data/ocr_dataset/localization/neolix/synthisis/images'
    os.makedirs(tmp_out, exist_ok=True)
    for k, img in batch_img:
        print(k)
        img = np.array(img, dtype=np.uint8)
        path = os.path.join(tmp_out, f"{k}.jpg")
        cv2.imwrite(path, img)


if __name__ == '__main__':
    lmdb_dir = '/code/ocr/ocr_pipeline/text_render/__data/eng_1M/train'
    out_dir = '/data/ocr_dataset/localization/neolix/synthisis/'
    gen_img_lbl(lmdb_dir, out_dir)
