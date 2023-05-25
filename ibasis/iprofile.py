import cProfile


def profile(log_path=None):
    """分析函数性能
    Args:
        log_path (_type_, optional): 输出的日志. Defaults to None.
            - pip install snakeviz
            - snakeviz log_path
    Use:
    @profile()
    @profile(log_path='profile.prof')
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            result = None
            try:
                profiler.enable()
                result = func(*args, **kwargs)
            finally:
                profiler.disable()
                if log_path is not None:
                    profiler.dump_stats(log_path)
                    print(f"性能分析日志已写入文件：{log_path}")
                else:
                    profiler.print_stats()
            return result
        return wrapper
    return decorator
