from functools import wraps
from time import perf_counter
from typing import Callable, Any


def get_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        print(f'{end_time - start_time:.3f}s <-- exec time"{func.__name__}()"')
        return result

    return wrapper
