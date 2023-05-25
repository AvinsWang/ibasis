from multiprocessing import Pool


def multi_pool(func, args_lis):
    """
    multiprocess
    Args:
        func: func name, only have one para!
        args_lis: arguments list
    Returns:
        res_lis
    e.g.
    def func(arg_lis):
        a, b = arg_lis
        return a+b
    args_lis = [[1,2], [3,4]]
    res_lis: [3, 7]
    """
    p = Pool()
    res_lis = p.map(func, args_lis)
    p.close()
    p.join()
    return res_lis

