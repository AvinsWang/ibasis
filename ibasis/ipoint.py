def fmt_2d_pts(lis, is_tuple=False, is_int=False, round_n=None):
    # round=0  -> float  e.g. 123.12 -> 123.0
    res = list()
    for (x, y) in lis:
        if is_int:
            x = int(x)
            y = int(y)
        if round_n is not None:
            x = round(x, round_n)
            y = round(y, round_n)
        if is_tuple:
            res.append((x, y))
        else:
            res.append([x, y])
    if is_tuple:
        res = tuple(res)
    return res