import os
import warnings
import os.path as osp
from pathlib import Path
from . import ibasic


# Path Enhancement
# path: a/b/c.jpg
# dir: a/b/


__test_unix_path = '/a/b/w/y/z/y/aa.bcd_xyz.txt'
__test_win_path = 'C:\\a\\b\\w\\y\\z\\y\\aa.bcd_xyz.txt'


# https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
class DisplayablePath(object):
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    # @property
    # def displayname(self):
    #     if self.path.is_dir():
    #         return self.path.name + '/'
    #     return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None, is_count_file=False):
        cls.is_count_file = is_count_file
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path for path in root.iterdir() if criteria(path)), key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria,
                                         is_count_file=is_count_file,
                                         )
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            path = self.path.name + '/'
            if self.is_count_file:
                path += '\t' + str(len(get_paths(str(self.path), key_mode=3, is_lis=True)))
            return path

        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))


def count_files_recursively(dir_):
    total = 0
    for root, dirs, files in os.walk(dir_):
        total += len(files)
    return total


def get_basename(path):
    return osp.basename(path)       # 这个windows格式不行


def get_stem(path):
    """获取路径中的stem, e.g. aa.bcd_xyz.txt -> aa.bcd_xyz"""
    # return Path(path).stem
    # return Path(path).stem                        # 1e7: 38.14346 s
    # return osp.splitext(get_basename(path))[0]    # 1e7: 17.9048 s
    # 10.8232 s
    return get_basename(path)[::-1].split('.', 1)[-1][::-1]


def get_suffix(path):
    """abc.jpg -> .jpg"""
    return osp.splitext(path)[-1]


def make_dirs(dir_, exist_ok=True):
    if dir_ is not None:
        os.makedirs(dir_, exist_ok=exist_ok)

def is_path_like(uri):
    sp_l = osp.split(uri)
    if '.' in sp_l[-1]:
        return True
    else:
        return False


def make_path_dir(path, exist_ok=True):
    pdir = osp.dirname(path)
    if pdir:
        os.makedirs(pdir, exist_ok=exist_ok)


def __speed(func, arg, K=1e6):
    import time
    st = time.time()
    for i in range(int(K)):
        func(arg)
    end = time.time()
    used = end-st
    print(f"used:{used:.5f}, per:{used/K :5e}")


# === 功能函数 ===

def get_paths(dir_, 
              file_type=None, 
              key_mode=0, 
              stem_append=None, 
              is_rel=False, 
              is_lis=False, 
              is_sort=False, 
              is_debug=False,
              ):
    """
    获取一个目录下所有文件路径
    Args:
        dir_:
        file_type: 指定文件类型 e.g. ['.txt'], ['.jpg', '.png']
        key_mode: 0: stem, 1: name,  2: rel_stem, 3: rel_name
        stem_append: 在stem中过滤给出的字段, e.g. 'xxx.lines.jpg' stem_append='.lines' -> 'xxx'
        注意, 该字段需要在key_mode 为 0和2 才能执行
        e.g. path='/a/b/c/d.jpg', dir='/a'
        0: {'d': '/a/b/c/d.jpg'}
        1: {'d.jpg': '/a/b/c/d.jpg'}
        2: {'b/c/d': '/a/b/c/d.jpg'}
        3: {'b/c/d.jpg': '/a/b/c/d.jpg'}
        4: {'c/d: '/a/b/c/d.jpg'}           # 保留其上一层文件夹
        5: {'c/d.jpg: '/a/b/c/d.jpg'}       # 同上, 保留后缀
        # 增加2,3 是为了防止出现重名情况
    Returns:
    # TODO: windows路径没有处理
    """
    def rm_stem_append(input):
        if stem_append is not None:
            return input.replace(stem_append, '')
        else:
            return input

    if isinstance(file_type, str):
        if file_type == 'IMAGE':
            file_type = ['.png', '.jpg', '.jpeg']
        else:
            file_type = [file_type]

    path_dic = dict()
    _replace_dir = dir_
    if not _replace_dir.endswith('/'):
        _replace_dir += '/'
    for root, dirs, name_lis in os.walk(dir_):
        for name in name_lis:
            stem, suffix = osp.splitext(name)
            suffix = suffix.lower()
            abs_path = osp.join(root, name)
            rel_path = abs_path.replace(_replace_dir, '')
            if file_type is not None and suffix not in file_type:
                continue
            if key_mode in [0, 1]:
                key = name              # == 1
                if key_mode == 0:
                    key = rm_stem_append(stem)
            elif key_mode in [2, 3]:
                key = rel_path
                if key_mode == 2:
                    key = rm_stem_append(osp.splitext(key)[0])
            elif key_mode in [4, 5]:
                split_lis = rel_path.split('/')
                if len(split_lis) <= 1:
                    key = rel_path
                    if key_mode == 4:
                        key = rm_stem_append(osp.splitext(key)[0])
                else:
                    key = '/'.join(split_lis[-2:])
                    if key_mode == 4:
                        key = rm_stem_append(osp.splitext(key)[0])
            else:
                raise NotImplementedError(f'key mode 类型有误, 期望[0,1,2,3,4,5], 输入:{key_mode}')
            if key in path_dic:
                warnings.warn(f"Key: {key} exists on path_dic, will update old key, path: {abs_path}")
            if is_rel:
                path_dic[key] = rel_path
            else:
                path_dic[key] = abs_path
            if is_debug:
                print(key, path_dic[key])
    if is_sort:
        path_dic = {k: path_dic[k] for k in sorted(path_dic.keys())}
    if is_lis:
        return list(path_dic.values())
    return path_dic


def get_dirs(dir_, max_level=1, is_abs=False):
    """获取目录下所有子目录, 并以列表返回
    Args:
        dir_: ~
        max_level:
            0, 往下一级 +1
            -1, 递归遍历然后输出所有子目录
    Return:
        list
    e.g.
    root/
        a/
        b/c
        c/d/e
    >>> get_dirs('root', 0)
    ['root']
    >>> get_dirs('root', 1)
    ['root/a', 'root/c', 'root/b']
    >>> get_dirs('root', 2)
    ['root/a', 'root/c/d', 'root/b/c']
    >>> get_dirs('root', 2)
    ['root/a', 'root/c/d/e', 'root/b/c']
    >>> get_dirs('root', -1)
    ['root/a', 'root/c/d/e', 'root/b/c']
    e.g.
    root/
    >>> get_dir('root', 0)
    ['root']
    """
    dirs = list()

    def has_sub_dir(_dir):
        for name in os.listdir(_dir):
            if osp.isdir(osp.join(_dir, name)):
                return True
        return False
    
    cur_level = 0
    def _get_dir(_dir, cur_level):
        cnt = 0
        if cur_level == max_level:
            dirs.append(_dir)
            return
        for name in os.listdir(_dir):
            uri = osp.join(_dir, name)
            if osp.isdir(uri):
                cnt += 1
                if has_sub_dir(uri):
                    _get_dir(uri, cur_level+1)
                else:
                    dirs.append(uri)
        # To solve get_dir('root', 0) -> [] when root/ is empty or don't have subdir, expected -> ['root'] 
        if cnt == 0:
            dirs.append(_dir)
    _get_dir(dir_, cur_level)
    if is_abs:
        dirs = [osp.abspath(d) for d in dirs]
    return dirs


def get_variable_name(variable):
    for key in locals():
        if locals()[key] == variable:
            return key


def get_dataset_pair(dir1, dir2, file_type1=None, file_type2=None, key_mode1=0, key_mode2=0,
                     stem_append1=None, stem_append2=None, is_sort=True, is_lis=False):
    print('获取路径下配对文件:')
    print('dir1:', dir1)
    print('dir2:', dir2)
    img_path_dic = get_paths(dir1, file_type=file_type1, key_mode=key_mode1, stem_append=stem_append1)
    lbl_path_dic = get_paths(dir2, file_type=file_type2, key_mode=key_mode2, stem_append=stem_append2)
    inter_keys = ibasic.get_intersection_keys(img_path_dic, lbl_path_dic, is_sort=is_sort)
    if is_lis:
        return [[k, img_path_dic[k], lbl_path_dic[k]] for k in inter_keys]
    else:
        for key in inter_keys:
            yield [key, img_path_dic.get(key), lbl_path_dic.get(key)]


def add_stemappend(path, stemappend='.lines', suffix=None):
    _stem, _suffix = osp.splitext(osp.basename(path))
    if stemappend in _stem:
        print(f"该路径以满足stemappend={stemappend}, {path}")
        return path
    _dir = osp.dirname(path)
    if suffix is not None:
        _suffix = suffix
    return osp.join(_dir, f"{_stem}{stemappend}{_suffix}")


def splice(route, pdir, dst_dir=None, sep='__', is_reverse=False):
    """
    Args:
        route: path or dir
        pdir: parent dir
        sep: split sign
        is_reverse: bool, True: '/'->'_', False: '_'->'/'
    Returns:
    route: /a/b/c/d.jpg   pdir: /a/b   sep: __,  is_reveerse: False
    -> /a/b/c__d.jpg
    route: /a/b/c__d.jpg   pdir: /a/b   sep: __,  is_reveerse: True
    -> /a/b/c/d.jpg
    """
    if dst_dir is None:
        dst_dir = pdir
    _pdir = pdir+'/' if not pdir.endswith('/') else pdir
    return osp.join(dst_dir, route.replace(_pdir, '').replace('/', sep))


def get_rel_path(path, dir_):
    """/a/b/c.jpg  /a/b  -> c.jpg"""
    if not dir_.endswith('/'):
        dir_ += '/'
    return path.replace(dir_, '', 1)


def pretty_print_dir(dir_, is_count_file=False):
    """print
    Args:
        dir_dic:
    Returns:
    """
    # With a criteria (skip hidden files)
    def is_not_hidden(path):
        return not path.name.startswith(".") and not osp.isfile(path)

    paths = DisplayablePath.make_tree(Path(dir_), criteria=is_not_hidden, is_count_file=is_count_file)
    for path in paths:
        print(path.displayable())

def change_path_suffix(path, suffix):
    if not suffix.startswith('.'):
        suffix = '.'+suffix
    return f"{osp.splitext(path)[0]}{suffix}"

# === test func ===
def __test_get_stem():
    __speed(get_stem, __test_unix_path)
    res = get_dirs('../', max_level=2)
    print(res)


def __test_splice():
    path = '/data16t/dataset/lanedet_online_dataset/tmp/2022-11-13_x3p96/meta/2022.11.13_10-44-01.992.json'
    new_path = '/data16t/dataset/lanedet_online_dataset/tmp/2022-11-13_x3p96_meta_2022.11.13_10-44-01.992.json'
    pdir = '/data16t/dataset/lanedet_online_dataset/tmp'
    a = splice(new_path, pdir)
    print(a)


if __name__ == '__main__':
    pretty_print_dir('/data/ocr_dataset/detection/OCRExpressDet/labels', True)