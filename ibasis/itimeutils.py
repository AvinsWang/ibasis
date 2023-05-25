import time
from functools import wraps


def timeit_return(func):
    @wraps(func)
    def _timeit(*args, **kwargs):
        st = time.time()
        res = func(*args, **kwargs)
        used = round((time.time() - st) * 1000, 3)
        return res, used
    return _timeit


def timeit_print(func):
    @wraps(func)
    def _timeit(*args, **kwargs):
        st = time.time()
        res = func(*args, **kwargs)
        print(f"Function {func.__name__} used [{(time.time() - st) * 1000:.6f}] ms")
        return res
    return _timeit


def timeit_print_avg(times=1, drop_n=0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            used_lis = []
            for i in range(times):
                st = time.time()
                res = func(*args, **kwargs)
                if drop_n != 0 and i > drop_n:
                    used_lis.append(time.time() - st)
            print(f"Function {func.__name__} exec {times-drop_n} times avg used [{sum(used_lis)/len(used_lis) * 1000:.6f}] ms")
            return res
        return wrapper
    return decorator


def timeit_record(used, is_ms=False):
    """_summary_
    Args:
        used (_type_): _description_
        is_ms (bool, optional): _description_. Defaults to False.
    Example:
    used = [0]
    @timeit_record(used=used, is_ms=True)
    def _t():
        time.sleep(1)
        print(1)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            st = time.time()
            res = func(*args, **kwargs)
            used[0] = time.time() - st
            if is_ms:
                used[0] *= 1000
            used[0] = round(used[0], 3)
            return res
        return wrapper
    return decorator
