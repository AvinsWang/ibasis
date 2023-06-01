from busi import fio


def __test_read_ICDAR_label():
    from ibasis import ipath
    import shutil
    import os
    path_lis  = ipath.get_paths('/code/ocr/NeolixOCR_74/OCRTextDet/Neolix3/0227_loc/merge_devied/train/labels', is_lis=True)
    cnt = 0 
    for path in path_lis:
        data_dic = fio.read_ICDAR_label(path)
        for k, v in data_dic.items():
            if k == '':
                print(path)
            if len(k) < 4 or len(v) == 0:
                print(path)
                print(len(k), v)
    print(cnt)


def __test_read_ICDAR_label_auto():
    """
    expect: {((0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)): {'txt': '6,abc'},
            ((0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (7, 7)): {'txt': 'xy,3,6,abc'}}
    """
    _path = './tmp_icdar.txt'
    with open(_path, 'w') as f:
        f.write('0,0,1,1,2,2,3,3,4,4,5,5,6,abc\n')
        f.write('0,0,1,1,2,2,3,3,4,4,7,7,xy,3,6,abc\n')
        f.write('0,0,1,1,2,2,3,3,4,4,7,7,10,9,abc\n')   # 假设文字是 '10,9,abc', 这种无法解决
    res_dic = fio.read_ICDAR_label(_path, mode='AUTO')
    print(res_dic)


def __test_all():
    __test_read_ICDAR_label()


if __name__ == '__main__':
    # __test_all()
    __test_read_ICDAR_label_auto()