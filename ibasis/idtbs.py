import os
import os.path as osp


class DataDir:
    def __init__(self, pdir=None, img_dir=None, lbl_dir=None, msk_dir=None, list_dir=None, vis_dir=None, show_list_dir=None):
        """
        Args:
            pdir: parent dir
            img_dir: image dir
            lbl_dir: label dir
            msk_dir: mask_dir
            list_dir: list file dir
            vis_dir: dir to save image which draw label
            show_list_dir: list file for display vis image with Simple Image Classification Tool
        # dir tree
        pdir
        |-- images
        |-- labels
        |-- lists
        |-- masks
        |-- show_lists
        `-- vis
        """
        self.pdir = pdir
        self.img_dir = img_dir
        self.lbl_dir = lbl_dir
        self.msk_dir = msk_dir
        self.list_dir = list_dir
        self.vis_dir = vis_dir
        self.show_list_dir = show_list_dir

    def _get_attr(self, name):
        if hasattr(self, name):
            return self.__getattribute__(name)
        else:
            print(f"输入的属性不存在: {name}")
            return None

    def _get_all_attr(self, include_kw=None, exclude_kw=None):
        """get include or exclude keyword attrs"""
        attrs = [attr for attr in dir(self) if not attr.startswith('__')]
        if include_kw is not None:
            attrs = [attr for attr in attrs if include_kw in attr]
        if exclude_kw is not None:
            attrs = [attr for attr in attrs if exclude_kw not in attr]
        return attrs

    def makedirs(self, name='__ALL__'):
        if name == '__ALL__':
            attrs = self._get_all_attr()
            for attr in attrs:
                attr_v = self._get_attr(attr)
                if type(attr_v) == str and ('path' in attr or 'dir' in attr):
                    if not osp.exists(attr_v):
                        os.makedirs(attr_v, exist_ok=True)
                        print(f"成功创建目录{attr}={attr_v}")
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
            self.vis_dir = osp.join(pdir, 'vis')
            self.list_dir = osp.join(pdir, 'lists')
            self.show_list_dir = osp.join(pdir, 'show_lists')
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
                    print('父目录为None, 无法得到相对路径!')
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
            print(f"{name}: {is_exists}")
            return is_exists

    def __str__(self):
        # TODO auto str attr
        return f"img_dir: {self.img_dir}\n" \
               f"lbl_dir: {self.lbl_dir}\n" \
               f"msk_dir: {self.msk_dir}\n" \
               f"vis_dir: {self.vis_dir}\n" \
               f"list_dir: {self.list_dir}\n" \
               f"show_list_dir: {self.show_list_dir}"
