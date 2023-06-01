import cv2
import random
import warnings
import pyclipper
import numpy as np
from tqdm import tqdm
import os.path as osp
from PIL import Image
from p_tqdm import p_map
from ibasis.idtbs import DataDir
from ibasis import ibasisF as base
from ibasis import (ipath, icolor, ipoint, imgalg)

from busi import utils as bu
from busi import (fio, parser, idraw)


class ImageDataset(DataDir):
    def __init__(self, 
                pdir=None, 
                img_dir=None, 
                lbl_dir=None,
                msk_dir=None, 
                list_dir=None, 
                vis_dir=None, 
                show_list_dir=None,
                key_mode=2,
                img_file_type='IMAGE',
                lbl_file_type='.json',
                img_stem_append=None,
                lbl_stem_append=None,
                ):
        super(ImageDataset, self).__init__(pdir, 
                                img_dir,
                                lbl_dir, 
                                msk_dir, 
                                list_dir, 
                                vis_dir, 
                                show_list_dir)
        self.key_mode = key_mode
        self.img_file_type = img_file_type
        self.lbl_file_type = lbl_file_type
        self.key_mode = key_mode
        self.img_stem_append = img_stem_append
        self.lbl_stem_append = lbl_stem_append

    def init_bef_call_methods(self):
        self.img_path_dic = ipath.get_paths(self.img_dir, file_type=self.img_file_type, key_mode=self.key_mode, stem_append=self.img_stem_append)
        self.lbl_path_dic = ipath.get_paths(self.lbl_dir, file_type=self.lbl_file_type, key_mode=self.key_mode, stem_append=self.lbl_stem_append)
        self.inter_keys = sorted(list(base.get_intersection_keys(self.img_path_dic, self.lbl_path_dic)))
        self.img_num = len(self.img_path_dic)
        self.lbl_num = len(self.lbl_path_dic)
        self.inter_num = len(self.inter_keys)
        print(f"Image num:{self.img_num}, Label num:{self.lbl_num}, Inter num:{self.inter_num}")

    def __iter__(self):
        for key in self.inter_keys:
            yield [key, self.img_path_dic.get(key), self.lbl_path_dic.get(key)]
    
    def __len__(self):
        return (self.img_num, self.lbl_num, self.inter_num)
    
    def _is_idx_fine(self, idx):
        if idx >= self.inter_num:
            raise IndexError(f"Input idx({idx}) should < length ({self.inter_num})")

    def get_data_pair(self, idx_or_key):
        if isinstance(idx_or_key, int):
            return (self.inter_keys[idx_or_key], 
                    self.img_path_dic[self.inter_keys[idx_or_key]], 
                    self.lbl_path_dic[self.inter_keys[idx_or_key]])
        elif isinstance(idx_or_key, str):
            if idx_or_key in self.inter_keys:
                return (idx_or_key, self.img_path_dic[idx_or_key], self.lbl_path_dic[idx_or_key])
        else:
            warnings.warn(f"{idx_or_key} not in inter_keys, 返回None")
            return (None, None, None)

    def vis_lbl_on_img(self, idx=None, dst_path=None, is_verbose=False):
        key, img_path, lbl_path = self.get_data_pair(idx)
        res_dic = fio.read_neolix_ocr_label(lbl_path, is_icdar_fmt=True)
        img = cv2.imread(img_path) 
        img = idraw.draw_polygon(img, res_dic, draw_info_keys=['txt'], is_disp_key=True)
        rel_path = self.rel(name='img_dir', path=img_path)
        if dst_path is None:
            dst_path = osp.join(self.vis_dir, f"{osp.splitext(rel_path)[0]}.jpg")
        ipath.make_path_dir(dst_path)
        cv2.imwrite(dst_path, img)
        if is_verbose:
            print(f"Save vis img on:{dst_path}")
    
    def get_data_pair_with_kw(self, kw=None):
        for inter_key in self.inter_keys:
            if kw is not None and not kw in inter_key:
                continue    
            yield self.get_data_pair(inter_key)

    def check_label_is_reasonable(self, kw=None):
        i = 0
        for idx, (stem, img_path, lbl_path) in enumerate(tqdm(self.get_data_pair_with_kw(kw))):
            i = idx
            img = cv2.imread(img_path)
            lbl_dic = fio.read_neolix_ocr_label(lbl_path, is_icdar_fmt=True)
            self.vis_lbl_on_img(stem, dst_path='tmp_aopeng.png')
            img = cv2.imread('tmp_aopeng.png')
            for pts, attr_dic in lbl_dic.items():
                x, y, w, h = cv2.boundingRect(np.array(pts))
                # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
                pts = np.array(pts)
                rect_blob = cv2.minAreaRect(pts)
                print(rect_blob)
                four_rotate_rect_pts = cv2.boxPoints(rect_blob)
                print(four_rotate_rect_pts)
                pts = imgalg.sort_rotate_rect(four_rotate_rect_pts)
                infos = imgalg.get_rotate_rect_info(pts)
                print(infos)
                img = cv2.polylines(img, [np.array(pts).astype(int)], 1, (0, 255, 0), 1)
                main_dirc = base.calc_polygon_main_direction(pts)
                for pt, t in zip(pts, ['lt', 'rt', 'rb', 'lb']):
                    cv2.putText(img, t, pt, cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=1)
                cv2.imwrite('tmp_aopeng.png', img)
                print(rect_blob[1][0]/rect_blob[1][1])
                print('-'*50)
                pass
        print(idx)


    def gen_msk(self, idx=None, is_verbose=False):
        def _gen_single(args):
            img_path, lbl_path, out_path = args
            try:
                H, W = cv2.imread(img_path).shape[:2]
                msk = np.zeros((H,W), dtype=np.uint8)
                lbl_dic = fio.read_neolix_ocr_label(lbl_path, is_icdar_fmt=True)
                for pts, attr in lbl_dic.items():
                    cv2.fillPoly(msk, [np.array(pts, dtype=int)], (1))
                msk = Image.fromarray(msk)
                msk.putpalette(icolor.palette)
                ipath.make_path_dir(out_path)
                msk.save(out_path)
                if is_verbose:
                    print('Mask saved at:', out_path)
            except Exception:
                print('Gen mask failed!', img_path)
        
        if idx is not None:
            key, img_path, lbl_path = self.get_data_pair(idx)
            if self.key_mode == 2:
                out_path = self.join('msk_dir', f"{key}.png")
            _gen_single([img_path, lbl_path, out_path])
        else:
            args_lis = list()
            for key, img_path, lbl_path in self.__iter__():
                if self.key_mode == 2:
                    out_path = self.join('msk_dir', f"{key}.png")
                args_lis.append((img_path, lbl_path, out_path))
            p_map(_gen_single, args_lis)

    def parser_lbl(self, mode):
        pass
    
    def wrap(self, func, func_kwargs):
        func(self, **func_kwargs)

    def gen_list_file(self, name, num=-1, is_random=False, is_stem=False):
        idxs = list(range(0, self.inter_num))
        if is_random:
            np.random.shuffle(idxs)
        if num != -1:
            idxs = idxs[:num]
        _img_dir = self.img_dir
        if not _img_dir.endswith('/'):
            _img_dir  += '/'
        if not osp.exists(self.list_dir):
            self.makedirs('list_dir')
        list_file_path = osp.join(self.list_dir, f"{name}.txt")
        with open(list_file_path, 'w') as f:
            for idx in idxs:
                img_path = self.img_path_dic[self.inter_keys[idx]]
                rel_path = img_path.replace(_img_dir, '')
                f.write(f"{rel_path}\n")
        print(f"Gen {name}.txt successfully on {list_file_path}")


class OCR_dataset(ImageDataset):
    def __init__(self, 
                pdir=None, 
                img_dir=None, 
                lbl_dir=None,
                msk_dir=None, 
                list_dir=None, 
                vis_dir=None, 
                show_list_dir=None,
                key_mode=2,
                img_file_type='IMAGE',
                lbl_file_type='.json',
                img_stem_append=None,
                lbl_stem_append=None,
                ):
         super(OCR_dataset, self).__init__(
                pdir=pdir, 
                img_dir=img_dir, 
                lbl_dir=lbl_dir,
                msk_dir=msk_dir, 
                list_dir=list_dir, 
                vis_dir=vis_dir, 
                show_list_dir=show_list_dir,
                key_mode=key_mode,
                img_file_type=img_file_type,
                lbl_file_type=lbl_file_type,
                img_stem_append=img_stem_append,
                lbl_stem_append=lbl_stem_append
         )
         pass


if __name__ == '__main__':
    dbnet_dt = ImageDataset().init_pdir('/data/ocr_dataset/localization/neolix/neolix_1st/localization')
    dbnet_dt.init_bef_call_methods()
    # dbnet_dt.gen_msk()
    print(dbnet_dt.get_data_pair(0))
    # dbnet_dt.vis_lbl_on_img('longmao/2023-01-31_detection_images/1088JT5169946045117_2023-01-31 072352852-wb_2')
    dbnet_dt.check_label_is_reasonable('neolix')