from typing import Callable, Any, Tuple
import hashlib
import pickle
import time
import json
import inspect
import builtins
import os

ENABLE_EXAMPLES = False

# For debug purpose, add this decorator to know whether your functions are called
def call_tracking(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        print(f"{func.__name__} has been called")
        return func(*args, **kwargs)
    return wrapper


class ResultMemorizer:
    _ins = None

    def __init__(self) -> None:
        # Create a ram caching
        self.cache = {}
        # Load the last state to the ram caching
        if os.path.isfile("state.json"):
            try:
                with open("state.json", "r") as f:
                    self.cache = json.loads(f.read())
            except Exception as e:
                pass

    def __new__(cls):
        # Make this class singleton since I love it
        if cls._ins is None:
            cls._ins = super(ResultMemorizer, cls).__new__(cls)
        return cls._ins

    # I don't know why I can't call save function in __del__
    def save(self):
        try:
            with open("state.json", "w+") as f:
                f.write(json.dumps(self.cache, indent=4))
        except Exception as e:
            print(f"Error saving state: {e}")

    # The main decoration
    def memorize(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # First, create unique ID by function name, arguments also source code
            fp = self._get_fingerprint(func, args, kwargs)
            # Whether this function have been called before
            if fp in self.cache:
                # Yes, give called the cached result
                return self.cache[fp]
            else:
                # No, call function, cache result and give caller the result
                result = func(*args, **kwargs)
                self.cache[fp] = result
                return result
        return wrapper

    def _get_fingerprint(self, func: Callable, args: Tuple, kwargs: dict) -> str:
        # Create a unique key based on function name, args, kwargs and source 
        try:
            key = (func.__name__, args, frozenset(kwargs.items()), inspect.getsource(func))
        except OSError:
            key = (func.__name__, args, frozenset(kwargs.items()))
        # print(key)
        # Serialize the key to a string
        key_str = pickle.dumps(key)
        # Use a hash function to create a unique fingerprint
        return hashlib.sha256(key_str).hexdigest()

if ENABLE_EXAMPLES:
    # Create the instance
    memorizer = ResultMemorizer()
    # Define the function with decorator
    @memorizer.memorize
    def add(a, b):
        return a + b

    @memorizer.memorize
    def expensive_func(x):
        time.sleep(1)
        return x * x

    @memorizer.memorize
    def cheap_func(x):
        time.sleep(1)
        return x / x
    # For the type of function that result different for same parameter, it shouldn't be cache
    @memorizer.memorize
    def dyna_func(x):
        x = time.time()
        return x

    print(add(1, 2))  # Should print 3 and cache the result
    print(expensive_func(10))  # Should call function and cache result 100
    print(cheap_func(10))  # Return the result without waiting
    print(add(1, 3))  # Should print 4 and cache the result
    print(expensive_func(10))  # Return the result without waiting

    memorizer.save()
