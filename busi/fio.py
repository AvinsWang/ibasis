#coding: utf-8
import json
import uuid
import traceback
import numpy as np
import os.path as osp
from ibasis import ipath, ipoint

from busi import parser


def read_json_file(fpath):
    try:
        f = open(fpath, 'r')
        data_dic = json.load(f)
    except Exception:
        print(f"读取文件失败: {fpath}")
        traceback.print_exc()
        data_dic = dict()
    return data_dic


def read_ICDAR_label(path, blank_map=['###', ''], mode='FIX'):
    """x1,y1,x2,y2,..., 标注文字 -> {((x1,y1), (x2,y2), ...):{txt:标注文字}}
    Args:
        path: file path
        blank_map: 将标注文件无标注标记替换成返回字典无标注标记
        mode: 模式, 
            * FIX 固定前8位为坐标, 后一位为字符; 
            * AUTO 自动解析, 前面的为坐标, 后一个',' 为字符
            * POINTS 全为坐标
        e.g. 标注文件中无标注标志为 ###, 返回字典是 None
        label content: x1,y1,...,### -> {((x1,y1),...): {txt:None}}
    Returns: dict <- {((x1,y1), (x2,y2), ...):{txt:标注文字}}
    Note: 返回的坐标为 int
    """
    def is_num(lis):
        try:
            [int(s) for s in lis]
        except Exception:
            return False
        return True
    
    txt_idx = -1
    data_dic = dict()
    with open(path, 'r') as f:
        for raw in f.readlines():
            raw = raw.strip()
            if raw.endswith(','):
                raw = raw[:-1]
            if len(raw) == 0:
                continue
            if mode == 'POINTS':
                _sep_lis = raw.split(',')
                raw_pts_lis = _sep_lis
                txt = ''
            if mode == 'AUTO':
                _sep_lis = raw.split(',')
                L = len(_sep_lis)
                if L < 8:
                    continue
                elif L == 8:
                    raw_pts_lis = _sep_lis
                    txt = '###'
                else:
                    # 标注文字可能出现 ','
                    L = len(_sep_lis)
                    f_idx = -1
                    for reverse_idx in range(-1, -(L+1-8), -1):
                        _pts = _sep_lis[:reverse_idx]
                        _txt = _sep_lis[reverse_idx:]
                        if len(_pts) % 2 == 0 and is_num(_pts) and not is_num(_txt):
                            f_idx = reverse_idx
                            break
                        else:
                            continue
                    raw_pts_lis = _sep_lis[:f_idx]
                    txt = ','.join(_sep_lis[f_idx:])


            if mode == 'FIX':
                _sep_lis = raw.split(',', 8)
                L = len(_sep_lis)
                if L == 8:
                    raw_pts_lis = _sep_lis
                    txt = '###'
                elif L == 9:
                    raw_pts_lis = _sep_lis[:-1]
                    txt = _sep_lis[-1]
                else:
                    print(f"解析ICDAR 标注格式出现错误, 长度: {L}, raw: {raw}")
            try:
                coords = parser.parse_nums_to_coord(raw_pts_lis, dim=2)
                data_dic[coords] = {'txt': blank_map[1] if (blank_map is not None and txt == blank_map[0]) else txt}
            except:
                traceback.print_exc()
    return data_dic


def write_ICDAR_label(path, data_dic, blank_map=['', '###'], is_write_empty_file=False):
    """{((x1,y1), (x2,y2), ...):{txt:标注文字}} -> x1,y1,x2,y2,..., 标注文字
    Args:
        path:
        data_dic:
        blank_map:
    Returns:
    """
    out_lis = list()
    for coords, info_dic in data_dic.items():
        coords_flatten = ",".join(np.array(coords).flatten().astype(str))
        infos = []
        for _k, _v in info_dic.items():
            if _k == 'txt' and _v == blank_map[0]:
                infos.append(blank_map[1])
            else:
                infos.append(_v)
        if len(infos) > 0:
            infos = ','.join(infos)
            out_lis.append(f"{coords_flatten},{infos}\n")
    if len(out_lis) > 0:
        with open(path, 'w') as f:
            for row in out_lis:
                if len(row.strip()) == 0:
                    print('存在一行为空', path, data_dic, out_lis)
                else:
                    f.write(row)
    else:
        if is_write_empty_file:
            with open(path, 'w') as f:
                f.write('')


def read_binglian_three_seg_json(path):
    """读取兵联标注的OCR文件
    [{
        "annotation": [
            {
                "attributes": {
                    "sdm": "102G D087-22 019"
                },
                "category": "三段码",
                "categoryId": "custom-1628295480297623553",
                "geo": [
                    [
                        35.7094672093687,
                        42.989307441286456
                    ],
                    [
                        35.318435093281025,
                        61.56333295545112
                    ],
                    [
                        112.35176196255345,
                        59.21714025892506
                    ],
                    [
                        213.23804791317423,
                        63.51849353588951
                    ],
                    [
                        211.2828873327358,
                        41.816211093023426
                    ],
                    [
                        111.17866561429044,
                        38.883470222365844
                    ],
                    [
                        35.7094672093687,
                        42.989307441286456
                    ]
                ],
                "id": "5ject4eeq1",
                "type": "polygon"
            }
        ],
        "name": "433031071641413_2023-01-31+070854327_0000.png"
    }]
    """
    json_lis = read_json_file(path)
    res_dic = dict()
    for anno_dic in json_lis:
        anno_lis = anno_dic['annotation']
        stem = ipath.get_stem(anno_dic['name'])
        one_res_dic = dict()
        for _anno_dic in anno_lis:
            txt = _anno_dic['attributes']['sdm']
            pts = _anno_dic['geo']
            pts = tuple(((int(xy[0]), int(xy[1])) for xy in pts))
            one_res_dic[pts] = {'txt': txt}
        res_dic[stem] = one_res_dic
    return res_dic


def read_longmao_waybill_label(path):
    _json = read_json_file(path)
    return parser.parse_longmao_waybill_label(_json)


def read_binglian_waybill_label(path):
    _json = read_json_file(path)
    return parser.parse_binglian_waybill_label(_json)


def read_aopeng_three_seg_label(path):
    _json = read_json_file(path)
    return parser.parse_aopeng_three_segmentation_label(_json)


def read_longmao_three_seg_label(path):
    _json = read_json_file(path)
    return parser.parse_longmao_three_segmentation_label(_json)


def write_neolix_ocr_label(path, data_dic):
    """Write neolix ocr json format label
    Args:
        path (os.pathlike): path to save label
        data_dic (dict): data dict e.g.
            {'uuid': '',
             'rel_path': '',
             'label': [
                {'pts': [(x,y), ...],
                 'txt': 'abc',
                 'other_attr': ''
                },
                ]
            }
    """
    if 'uuid' not in data_dic:
        data_dic['uuid'] = str(uuid.uuid1())
    with open(path, 'w') as f:
        json.dump(data_dic, f)
    

def read_neolix_ocr_label(path, is_icdar_fmt=False):
    """
    Args:
        path (_type_): _description_
        is_icdar_fmt (bool, optional): _description_. Defaults to False.
    Returns:
        _type_: _description_
    Example:
        {'label': [{'pts': [], attr: ...}]}
    """
    res_dic = read_json_file(path)
    if is_icdar_fmt:
        if 'label' in res_dic:
            res_dic = parser.convert_neolix_dic2ICDAR_dic(res_dic)
        else:
            res_dic = {}
    return res_dic


def read_txt_file(fpath):
    lines = None
    with open(fpath, 'r') as f:
        lines = f.readlines()
    return lines


def read_ocr_multi_label(fpath, is_keep_line=False, key_mode=1):
    """
    Args:
        fpath (_type_): _description_
        key_mode: Align to base.get_paths args: key_mode
    Example:
    image_name,text
    """
    data_dic = dict()
    cnt = 0
    with open(fpath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if len(line) <= 1:
                continue
            if ',' in line:
                s_split = line.split(',', maxsplit=1)
                if len(s_split) == 2:
                    s1, s2 = s_split
                    if is_keep_line:
                        s2 = line
                    data_dic[s1] = s2
                    cnt += 1
    print(f"读取:{fpath}\n获取有效数据:{cnt}/{len(lines)}")
    return data_dic


def read_visual_select_file(fpath, key_mode='name'):
    """读取视觉选图结果文档, file content e.g. 
    2023_0513_OCR/002027000063-wb_1.jpg,FILTER
    """
    selected_dic = dict()
    filtered_dic = dict()
    for line in read_txt_file(fpath):
        line = line.strip()
        s_split = line.split(',')
        if len(s_split) != 2:
            continue
        key = s_split[0]
        if key_mode == 'name':
            key = osp.basename(key)
        if 'FILTER' in s_split[-1]:
            filtered_dic[key] = s_split[-1]
        if 'SELECTED' in s_split[-1]:
            selected_dic[key] = s_split[-1]
    return selected_dic, filtered_dic


def read_list_file(fpath, key_mode=3):
    list_dic = dict()
    lines = read_txt_file(fpath)
    for line in lines:
        line = line.strip()
        key = line
        if key_mode == 2:
            key = osp.splitext(key)[0]
        list_dic[key] = line
    return list_dic
    


def write_txt_file(fpath, content, mode='w', content_append=None):
    if isinstance(content, str):
        content = [content]
    if content_append is not None:
        content = [f"{c}{content_append}" for c in content]
    with open(fpath, mode) as f:
        f.writelines(content)



if __name__ == '__main__':
    pass