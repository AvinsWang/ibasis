import numpy as np
import torch


def parse_img_from_tensor(tensor, idx=None, ipt_fmt='NCHW', ipt_type='float', opt_fmt='HWC', opt_type='uint8', mean=None, std_var=None):
    """Get cv2 image from tensor
    Args:
        tensor (torch.Tensor): inpurt tensor 
        idx (int, optional): index. Defaults to None. None mean get all
        ipt_fmt (str, optional): input format. Defaults to 'NCHW'
        ipt_type (str, optional): inpurt type. Defaults to float[0~1] or uint8
        opt_fmt (str, optional): output format. Defaults to 'HWC'
        opt_type (str, optional): output type. Defaults to 'uint8'
        mean (np.arr, optional): mean, length should map with input,
            e.g. input is NCHW, or CHW (c! = 1), mean should be: [v1, v2, v3]
            e.g. input is NCHW, or CHW (c == 1) or C NOT IN input, mean = [v1]
        std_var (float, optional): standard variance
    Returns:
        list: [img, ...]
    """
    if isinstance(tensor, torch.Tensor):
        array = tensor.to('cpu').detach().numpy()
    else:
        array = tensor
    
    is_convert_value = ipt_type != opt_type
    
    if ipt_fmt.startswith('N'):         # ['NCHW', 'NHW', 'NHWC']
        arr_lis = [array[i] for i in range(len(array))]
        if idx is not None:
            arr_lis = [arr_lis[idx]]
        ipt_fmt = ipt_fmt[1:]
    else:                               # ['CHW', 'HW', 'HWC']
        arr_lis = [array]
    
    # auto squeeze axis when axis == 1
    if 'C' in ipt_fmt:
        c_idx = ipt_fmt.find('C')
        if c_idx != -1:
            sqz_arr_lis = [arr.squeeze(c_idx) if arr.shape[c_idx] == 1 else arr for arr in arr_lis]
            if len(sqz_arr_lis[0].shape) == len(arr_lis[0].shape)-1:
                ipt_fmt = ipt_fmt.replace('C', '')
                if 'C' in opt_fmt:
                    opt_fmt = opt_fmt.replace('C', '')
                arr_lis = sqz_arr_lis
    einsum_rule = ''
    if ipt_fmt != opt_fmt:
        if len(ipt_fmt) != len(opt_fmt):
            raise TypeError(f"Input format '{ipt_fmt}' DO NOT match Output format '{opt_fmt}'")
        else:
            einsum_rule = f"{ipt_fmt}->{opt_fmt}"

    res_lis = []
    for arr in arr_lis:
        if einsum_rule:
            arr = np.einsum(einsum_rule, arr)
        if is_convert_value:
            arr *= 255
            if std_var is not None:
                arr *= std_var
            if mean is not None:
                arr += mean
            arr = np.clip(arr, 0, 255)
        if 'uint8' in opt_type:
            # use: arr = arr.astype(arr) get ERROR
            # img = cv2.polylines(img, [coords], 1, color, 1)
            # cv2.error: OpenCV(4.5.5) :-1: error: (-5:Bad argument) in function 'polylines'
            # > Overload resolution failed:
            # >  - Layout of the output array img is incompatible with cv::Mat
            # >  - Expected Ptr<cv::UMat> for argument 'img'
            arr = np.ascontiguousarray(arr).astype(np.uint8)
        res_lis.append(arr)
    return res_lis