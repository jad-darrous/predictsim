import time

def print_timing(logger):
    def decorator(func):
        def new_func(*arg):
            t1 = time.time()
            res = func(*arg)
            t2 = time.time()
            logger('%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0))
            return res
        return new_func 
    return decorator
