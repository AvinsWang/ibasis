import json
import traceback
import numpy as np
from collections import defaultdict

from ibasis import ipath, ipoint


def parse_nums_to_coord(nums, dim=2, dtype=int):
    """convert nums to coords
    Args:
        nums: interable
        dim: coord dim
        dtype: data type
    Returns: tuple
    >>> parser_nums_to_coord([1, 2, 3, 4, 5, 6, 7, 8], 2)
    ((1, 2), (3, 4), (5, 6), (7, 8))
    """
    nums = list(map(dtype, nums))
    L = len(nums)
    if L % dim != 0:
        raise RuntimeError(f"Length of numbers({L}) is not match dim({dim}), expect lenght % dim == 0")
    return tuple(tuple(nums[i:i + dim]) for i in range(0, L, dim))


def order_points(pts):
    ''' sort rectangle points by clockwise '''
    sort_x = pts[np.argsort(pts[:, 0]), :]
    
    Left = sort_x[:2, :]
    Right = sort_x[2:, :]
    # Left sort
    Left = Left[np.argsort(Left[:,1])[::-1], :]
    # Right sort
    Right = Right[np.argsort(Right[:,1]), :]
    
    return np.concatenate((Left, Right), axis=0)


def keep_one_blank(ipt, blank=" "):
    """'a b c    d' -> 'a b c d'"""
    def _filter(S):
        opt = ""
        i = 0
        is_find_blank = False
        while i < len(S):
            c = S[i]
            if c != blank:
                opt += c
                if is_find_blank is True:
                    is_find_blank = False
            else:
                if is_find_blank is False:
                    opt += c
                    is_find_blank = True
            i += 1
        return opt
    if isinstance(ipt, str):
        return _filter(ipt)
    if isinstance(ipt, list):
        return [_filter(s) for s in ipt]


def parse_aopeng_three_segmentation_label(json_dic):
    """解析奥鹏三段码标注文件
    {
    "auditId": "d556ba2b-5208-404e-b208-8a104a51a43a.247.audit",
    "instances": [
        {
            "id": "e58e4e5e-9603-42ec-90a2-70aa6df5ee8b",
            "category": "三段码",
            "categoryName": "三段码",
            "number": 1,
            "attributes": "",
            "children": [
                {
                    "id": "39682603-890f-4664-a431-be0bdfc7b620",
                    "name": "新组件",
                    "displayName": "新组件",
                    "displayColor": "#fcdc00",
                    "number": 1,
                    "cameras": [
                        {
                            "camera": "default",
                            "frames": [
                                {
                                    "isKeyFrame": true,
                                    "shapeType": "polygon",
                                    "shape": {
                                        "points": [
                                            {
                                                "x": 21.001745,
                                                "y": 37.074783
                                            },
                                            {
                                                "x": 193.932066,
                                                "y": 37.562827
                                            },
                                            {
                                                "x": 193.769384,
                                                "y": 54.969736
                                            },
                                            {
                                                "x": 20.676382,
                                                "y": 54.156329
                                            }
                                        ]
                                    },
                                    "order": 0,
                                    "attributes": "",
                                    "isOCR": true,
                                    "isFormula": "102G D087-22 019"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ],
    "frames": [
        {
            "camera": "default",
            "frames": [
                {
                    "imageUrl": "https://projecteng.oss-cn-shanghai.aliyuncs.com/0_ProjectData/upload_data/xsqsdm0214_c313e82dae5446ee818455cbe082826f/images2/312182592797349_2022-11-24+070920023_0000.png",
                    "imageWidth": 225,
                    "imageHeight": 224,
                    "valid": true,
                    "rotation": 0
                }
            ]
        }
    ],
    "relationships": [],
    "attributes": {},
    "statistics": "https://oss-prd.appen.com.cn:9001/tool-prod/9edeaef4-d14c-4e50-aa5d-7c8934643900/9edeaef4-d14c-4e50-aa5d-7c8934643900.CLO04AMQAA3d3d_2023-02-15T061126Z.247.result.stat.json"
    }
    """
    # return polygon_dic, refer __init__.py
    out_dic = dict()
    if len(json_dic) == 0:
        return out_dic
    instance_lis = json_dic["instances"]
    for ins_dic in instance_lis:
        if len(ins_dic['children']) == 0:
            continue
        assert ins_dic["category"] == "三段码"
        try:
            # 注意: 默认children只有一个元素
            if len(ins_dic['children'][0]) == 0:
                continue
            frames = ins_dic['children'][0]["cameras"][0]["frames"]
            pts_dic_lis = frames[0]["shape"]["points"]     # [{"x":1, "y":1}, ...]
            pts_tup = tuple([(int(_d["x"]), int(_d["y"])) for _d in pts_dic_lis]) # -> ((1,1), (2,2), ...)
            # assert len(pts_tup) == 4, f"len pts: {len(pts_tup)}"
            pts_tup = tuple(map(tuple, pts_tup))
            text = frames[0]["isFormula"]
            if text == '###':
                text = ''
            if '#' in text:
                print('标注不合规范:', text, end='')
                text = text.replace('#', '&')
                print('-->', text)
            text = keep_one_blank(text)
            out_dic[pts_tup] = {'txt': text}
        except Exception:
            traceback.print_exc()
    return out_dic


def parse_longmao_three_segmentation_label(json_dic):
    """解析龙猫三段码标注
    {
    "version": "4.5.7",
    "flags": {},
    "shapes": [
        {
        "label": "L5",
        "points": [
            [
            159.87223825272204,
            866.6768459139525
            ],
            [
            246.96333314783143,
            860.9694518048727
            ],
            [
            246.96333314783143,
            930.2735231294035
            ],
            [
            153.2577247163846,
            937.6116012696482
            ]
        ],
        "shape_type": "quadrangle",
        "flags": {}
        },
        {
        "label": "563L-007A",
        "points": [
            [
            97.17162161202238,
            332.1127710697926
            ],
            [
            440.390743584345,
            328.09627301346893
            ],
            [
            443.64915297015824,
            378.704148523147
            ],
            [
            96.08548515008464,
            385.1305454132649
            ]
        ],
        "shape_type": "quadrangle",
        "flags": {}
        }
    ],
    "imagePath": "5IMG_0931_0000.png",
    "imageData": "",
    "imageHeight": 1390,
    "imageWidth": 1143
    }
    """
    shape_lis = json_dic['shapes']
    out_dic = dict()
    try:
        for _dic in shape_lis:
            pts_tup = tuple([(int(xy[0]), int(xy[1])) for xy in _dic['points']])
            # assert len(pts_tup) == 4, f"len pts: {len(pts_tup)}"
            text = _dic['label'].strip()
            if text == '###':
                    text = ''
            if '#' in text:
                print('标注不合规范:', text, end='')
                text = text.replace('#', '&')
                print('-->', text)
            text = keep_one_blank(text)
            out_dic[pts_tup] = {'txt': text}
    except:
        traceback.print_exc()
    return out_dic


def parse_cocotext_json(json_dic):
    # 'cats', 'anns', 'imgs', 'imgToAnns', 'info'
    anns = json_dic['anns']
    imgs = json_dic['imgs']
    imgToAnns = json_dic['imgToAnns']
    out_dic = defaultdict(dict)
    # for img_key, anno_key_lis in imgToAnns.items():
    #     if img_key not in imgs:
    #         continue
    #     for anno_key in anno_key_lis:
    #         if anno_key not in anns:
    #             continue
    #         # pts = parse_nums_to_coord()
    #         print(1)

    for img_key, img_info_dic in imgs.items():
        if img_key in anns:
            pirnt(1)
    
    print(1)


def parse_longmao_waybill_label(json_dic):
    res_dic = dict()
    for _dic in json_dic['objects']:
        polygon = ipoint.fmt_2d_pts(_dic['kuang'], is_tuple=True, is_int=True)
        cate_name = _dic['label']
        vec = ipoint.fmt_2d_pts([_dic['tou'][0], _dic['wei'][0]])
        res_dic[polygon] = {'cate_name': cate_name, 'vec': vec}
    return res_dic


def parse_binglian_waybill_label(json_dic):
    res_dic = dict()
    for anno_dic in json_dic:
        anno_lis = anno_dic['annotation']
        stem = ipath.get_stem(anno_dic['name'])
        one_res_dic = dict()
        for _anno_dic in anno_lis:
            cate_name = _anno_dic['category']
            pts = _anno_dic['geo']
            pts = ipoint.fmt_2d_pts(pts, is_tuple=True, is_int=True)
            vec = ipoint.fmt_2d_pts(_anno_dic['head'])
            one_res_dic[pts] = {'cate_name': cate_name, 'polygon': pts, 'vec': vec}
        res_dic[stem]= one_res_dic
    return res_dic


def convert_ICDAR_dic2neolix_dic(dic, rel_path=''):
    lbl_lis = list()
    for pts, _dic in dic.items():
        _dic['pts'] = pts
        lbl_lis.append(_dic)
    return {'rel_path': rel_path, 'label': lbl_lis}


def convert_neolix_dic2ICDAR_dic(dic):
    return {ipoint.fmt_2d_pts(dic.pop('pts'), is_tuple=True, is_int=True): dic for dic in dic['label']}


if __name__ == '__main__':
    # import doctest
    # doctest.testmod()
    from busi import fio
    json_dic = fio.read_json_file("/data16t/ocr_dataset/recg/open_dataset/10_COCO_Text_V2/cocotext.v2.json")
    x = parse_cocotext_json(json_dic)
    print(x)
