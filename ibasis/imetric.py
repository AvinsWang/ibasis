# def calc_ap(res, mode='101'):
#     """clac ap for single

#     Args:
#         res (_type_): _description_
#         mode (str, optional): _description_. Defaults to '101'.
#     """

import numpy as np

def compute_ap(recall, precision):
    """计算单类别的 average precision"""
    # 将 recall 和 precision 拼接成一个矩阵
    ap = 0.0
    mrec = np.concatenate(([0.0], recall, [1.0]))
    mpre = np.concatenate(([0.0], precision, [0.0]))

    # 计算每个 recall 区间的最大 precision
    for i in range(mpre.size - 1, 0, -1):
        mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

    # 计算每个 recall 区间的面积
    for i in range(mpre.size - 1):
        ap += (mrec[i + 1] - mrec[i]) * mpre[i + 1]

    return ap

def compute_map(confidences, labels, num_classes):
    """计算多类别的 mean average precision"""
    aps = []
    for c in range(num_classes):
        # 找到所有属于当前类别的样本
        class_indices = np.where(labels == c)[0]

        # 如果当前类别没有样本，则将其 ap 设为 0
        if class_indices.size == 0:
            aps.append(0.0)
            continue

        # 根据置信度排序样本
        sorted_indices = np.argsort(-confidences[class_indices])
        sorted_labels = labels[class_indices][sorted_indices]

        # 计算每个样本的 recall 和 precision
        tp = sorted_labels == c
        fp = sorted_labels != c
        tp_cumsum = np.cumsum(tp)
        fp_cumsum = np.cumsum(fp)
        recall = tp_cumsum / tp.sum()
        precision = tp_cumsum / (tp_cumsum + fp_cumsum)

        # 计算单类别的 average precision
        ap = compute_ap(recall, precision)
        aps.append(ap)

    # 计算多类别的 mean average precision
    map = np.mean(aps)

    return map

if __name__ == '__main__':
    # 读取置信度和标签
    confidences = []
    labels = []
    with open('__metric.txt', 'r') as f:
        for line in f.readlines():
            confidences.append(float(line.strip().split(',')[-1]))
            labels.append(0)
    # with open('confidences.txt', 'r') as f:
    #     for line in f:
    #         confidences.append(float(line.strip()))
    # with open('labels.txt', 'r') as f:
    #     for line in f:
    #         labels.append(int(line.strip()))

    # # 转换为 numpy 数组
    # confidences = np.array(confidences)
    # labels = np.array(labels)

    # # 计算多类别的 mean average precision
    # num_classes = np.max(labels) + 1
    # map = compute_map(confidences, labels, num_classes)

    # # 输出结果
    # print('mAP: {:.4f}'.format(map))
    cnt = 0
    for c in confidences:
        if c >= 0.75:
            cnt += 1
    print(round(cnt/len(confidences), 4))