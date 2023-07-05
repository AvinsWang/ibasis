import warnings
from ibasis import ibasisF as base
from ibasis import (ipath, icolor, ipoint, imgalg)


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
        self.img_path_dic = ipath.get_paths(self.img_dir, file_type=self.img_file_type, 
                                            key_mode=self.key_mode, stem_append=self.img_stem_append)
        self.lbl_path_dic = ipath.get_paths(self.lbl_dir, file_type=self.lbl_file_type, 
                                            key_mode=self.key_mode, stem_append=self.lbl_stem_append)
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
    
    