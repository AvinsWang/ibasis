import os
import os.path as osp
from loguru import logger

from ibasis import ipath
from ibasis import ibasic


class DataDir:
    def __init__(self,
                 pdir=None,
                 img_dir=None,
                 lbl_dir=None,
                 msk_dir=None,
                 list_dir=None,
                 vis_dir=None,
                 ):
        """
        Args:
            pdir: parent dir
            img_dir: image dir
            lbl_dir: label dir
            msk_dir: mask_dir
            list_dir: list file dir
            vis_dir: dir to save image which draw label
        # dir tree
        pdir
        |-- images
        |-- labels
        |-- lists
        |-- masks
        `-- vis
        """
        self.pdir = pdir
        self.img_dir = img_dir
        self.lbl_dir = lbl_dir
        self.msk_dir = msk_dir
        self.list_dir = list_dir
        self.vis_dir = vis_dir

    def _get_attr(self, name):
        if hasattr(self, name):
            return self.__getattribute__(name)
        else:
            logger.error(f"输入的属性不存在: {name}")
            return None

    def _get_all_attr(self, include_kw=None, exclude_kw=None):
        """get include or exclude keyword attrs"""
        attrs = [attr for attr in dir(self) if not attr.startswith('__')]
        if include_kw is not None:
            attrs = [attr for attr in attrs if include_kw in attr]
        if exclude_kw is not None:
            attrs = [attr for attr in attrs if exclude_kw not in attr]
        return attrs

    def _get_all_routes(self):
        attrs = sorted(self._get_all_attr())
        for attr in attrs:
            attr_v = self._get_attr(attr)
            if type(attr_v) == str and attr.endswith(('path', 'dir')):
                yield (attr, attr_v)

    def makedirs(self, name='ALL'):
        if name == 'ALL':
            for attr, attr_v in self._get_all_routes():
                if not osp.exists(attr_v):
                    os.makedirs(attr_v, exist_ok=True)
                    logger.debug(f"成功创建目录{attr}={attr_v}")
        else:
            _dir = self._get_attr(name)
            if _dir is not None:
                os.makedirs(_dir, exist_ok=True)

    def add_attr(self, is_makedir=False, dir_dic={}, **kwargs):
        if isinstance(kwargs, dict) and len(kwargs) > 0:
            dir_dic.update(kwargs)
        for k, v in dir_dic.items():
            setattr(self, k, v)
            if is_makedir:
                self.makedirs(k)
        del dir_dic

    def update_attr(self, is_makedir=False, **kwargs):
        self.add_attr(is_makedir, **kwargs)
    
    def join(self, *, name='pdir', path=None):
        _pdir = self._get_attr(name)
        if isinstance(path, str):
            _path = osp.join(_pdir, path)
        elif isinstance(path, tuple):
            _path = osp.join(_pdir, *path)
        else:
            raise NotImplementedError()
        return _path

    def init_pdir(self, pdir):
        if pdir is not None:
            self.pdir = pdir
            self.img_dir = osp.join(pdir, 'images')
            self.lbl_dir = osp.join(pdir, 'labels')
            self.msk_dir = osp.join(pdir, 'masks')
            self.list_dir = osp.join(pdir, 'lists')
            self.vis_dir = osp.join(pdir, 'vis')
        return self

    def rel(self, *, name='img_dir', path=None):
        """get name relative path to pdir, name='img_dir',
        Args:
            name (str, optional): . Defaults to 'img_dir'.
            path (_type_, optional): path
                if is None: return name(attr) to pdir rel path
                else:       return path to name rel path
        Returns:
            os.pathlike: rel path
        """
        if path is None:
            _dir = self._get_attr(name)
            if _dir is not None:
                if self.pdir is not None:
                    _pir = self.pdir
                    if not _pir.endswith('/'):
                        _pir += '/'
                    return _dir.replace(self.pdir, '', 1)
                else:
                    logger.warning('父目录为None, 无法得到相对路径!')
        else:
            _dir = self._get_attr(name)
            if _dir is not None:
                if not _dir.endswith('/'):
                    _dir += '/'
                return path.replace(_dir, '', 1)

    def _check_exists(self, name):
        """check whether name exist, name='img_dir' etc. """
        _dir = self._get_attr(name)
        if _dir is not None:
            if osp.exists(_dir):
                return True
            else:
                return False

    def check_exists(self, name='__ALL__'):
        if name == '__ALL__':
            attrs = self._get_all_attr()
            state = {}
            for attr in attrs:
                attr_v = self._get_attr(attr)
                if type(attr_v) == str and ('path' in attr or 'dir' in attr):
                    state.update({attr: self._check_exists(attr)})
            [print(f"{k}: {v}") for k, v in state]
            return all(state.values())
        else:
            is_exists = self._check_exists(name)
            logger.debug(f"{name}: {is_exists}")
            return is_exists

    def __str__(self):
        lis = list()
        for attr, attr_v in sorted(self._get_all_routes(), key=lambda x: len(x[0])):
            prefix = 'd'
            if 'path' in attr:
                prefix = '-'
            lis.append(f"{prefix} [{attr}] {osp.exists(attr_v)} {attr_v}")
        return '\n'.join(lis)


class DataDirDT(DataDir):
    def __init__(self,
                 pdir=None,
                 img_dir=None,
                 lbl_dir=None,
                 msk_dir=None,
                 list_dir=None,
                 vis_dir=None,
                 img_key_mode=2,
                 lbl_key_mode=2,
                 img_file_type='IMAGE',
                 lbl_file_type='.json',
                 img_stem_append=None,
                 lbl_stem_append=None,
                 ):
        super(DataDirDT, self).__init__(pdir,
                                        img_dir,
                                        lbl_dir,
                                        msk_dir,
                                        list_dir,
                                        vis_dir,
                                        )
        self.img_file_type = img_file_type
        self.lbl_file_type = lbl_file_type
        self.img_key_mode = img_key_mode
        self.lbl_key_mode = lbl_key_mode
        self.img_stem_append = img_stem_append
        self.lbl_stem_append = lbl_stem_append

    def init_bef_call_methods(self):
        self.img_path_dic = ipath.get_paths(self.img_dir, file_type=self.img_file_type, 
                                            key_mode=self.key_mode, stem_append=self.img_stem_append)
        self.lbl_path_dic = ipath.get_paths(self.lbl_dir, file_type=self.lbl_file_type, 
                                            key_mode=self.key_mode, stem_append=self.lbl_stem_append)
        self.inter_keys = sorted(list(ibasic.get_intersection_keys(self.img_path_dic, self.lbl_path_dic)))
        self.img_num = len(self.img_path_dic)
        self.lbl_num = len(self.lbl_path_dic)
        self.inter_num = len(self.inter_keys)
        logger.info(f"Image num:{self.img_num}, Label num:{self.lbl_num}, Inter num:{self.inter_num}")

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
            logger.warning(f"{idx_or_key} not in inter_keys, 返回None")
            return (None, None, None)


class TestUnit():
    def __init__(self):
        self.pdir = 'tmp'

    def test_data_dir(self):
        dd = DataDir().init_pdir(self.pdir)
        dd.add_attr(test_dir=dd.join(name='pdir', path='test'))
        dd.add_attr(test_path=dd.join(name='pdir', path='test.txt'))
        print(dd)

    def test_data_dirDT(self):
        dd = DataDir().init_pdir(self.pdir)
        dd.add_attr(test_dir=dd.join(name='pdir', path='test'))
        dd.add_attr(test_path=dd.join(name='pdir', path='test.txt'))
        print(dd)


if __name__ == "__main__":
    tu = TestUnit()
    tu.test_data_dir()
    tu.test_data_dirDT()
