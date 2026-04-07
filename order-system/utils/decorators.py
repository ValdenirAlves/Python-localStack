import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        
        result = func(*args, **kwargs)
        
        end = time.time()
        print(f"{func.__name__} executed in {end - start:.4f}s")
        
        return result
    return wrapper