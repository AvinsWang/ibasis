import timeit
import warnings
import functools


def dic2lis(dic):
    """convert {'a': 1} -> [['a', 1]]"""
    return [[k, v] for k, v in dic.items()]


def get_dic_item(dic, idx):
    if idx > len(dic):
        warnings.warn(f"The index {idx} is out of dict length {len(dic)}")
    for i, (k, v) in enumerate(dic.items()):
        if i == idx:
            return k,v


def separate_lis(lis):
    """[[a, b], [d, e]] -> [a, d], [b, e]"""
    if len(lis) == 0:
        return lis
    if not isinstance(lis[0], list):
        return lis
    L = len(lis[0])
    _lis = [[] for _ in range(L)]
    for i, sub_lis in enumerate(lis):
        if not len(sub_lis) == L:
            warnings.warn("Each sub list should have same length, failed!")
            return lis
        for j, sub_e in enumerate(sub_lis):
            print(i, j)
            _lis[j].append(sub_e)
    return _lis


def separate_dic(dic):
    """{k1: v1, k2: v2} -> [[k1, k2], [v1, v2]]"""
    return list(dic.keys()), list(dic.values())


def show_dic(dic, len=None):
    _len = len(dic)
    if len is None or _len < len:
        len = _len
    for i, (k, v) in enumerate(dic.items()):
        print(i, k, v)
        if i == len-1:
            break


def dic_ndarr2lis_(dic):
    # inplace func
    if isinstance(dic, dict):
        for k, v in dic.items():
            if isinstance(v, dict):
                dic_ndarr2lis_(v)
            elif isinstance(v, np.ndarray):
                dic[k] = v.tolist()
            else:
                pass


def get_intersection_keys(*args, is_sort=False):
    inter_keys = args[0].keys()
    for i, dic_ in enumerate(args):
        print(f"dict:{i}={len(dic_)}", end=' ')
        if i > 0:
            inter_keys = inter_keys & dic_.keys()
    if is_sort:
        inter_keys = sorted(inter_keys)
    print(f"inters={len(inter_keys)}")
    return inter_keys


def compose_two_func(f, g):
    return lambda *a, **kw: f(g(*a, **kw))


def compose_funcs(*fs):
    return functools.reduce(compose_two_func, fs[::-1])