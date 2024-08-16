import os
import json
import hashlib
import pickle
import inspect
from typing import Callable, Any, Tuple

class ResultMemorizer:
    # Class variable for cache
    cache = {}

    @classmethod
    def _load_state(cls):
        # Load the last state to the cache
        if os.path.isfile("state.json"):
            try:
                with open("state.json", "r") as f:
                    cls.cache = json.loads(f.read())
            except Exception as e:
                print(f"Error loading state: {e}")

    @classmethod
    def _save_state(cls):
        # Save the current state to the file
        try:
            with open("state.json", "w+") as f:
                f.write(json.dumps(cls.cache, indent=4))
        except Exception as e:
            print(f"Error saving state: {e}")

    @classmethod
    def invalidate(cls, func: Callable, *args, **kwargs) -> None:
        # Create unique ID by function name, arguments, and source code
        fp = cls._get_fingerprint(func, args, kwargs)
        # Remove the fingerprint from the cache if it exists
        if fp in cls.cache:
            del cls.cache[fp]
            cls._save_state()

    @classmethod
    def memorize(cls, func: Callable) -> Callable:
        # Ensure state is loaded when using the decorator
        cls._load_state()

        def wrapper(*args, **kwargs) -> Any:
            # Create unique ID by function name, arguments, and source code
            fp = cls._get_fingerprint(func, args, kwargs)
            # Whether this function has been called before
            if fp in cls.cache:
                # Return the cached result
                return cls.cache[fp]
            else:
                # Call function, cache result, and return the result
                result = func(*args, **kwargs)
                cls.cache[fp] = result
                cls._save_state()
                return result

        return wrapper

    @classmethod
    def _get_fingerprint(cls, func: Callable, args: Tuple, kwargs: dict) -> str:
        # Create a unique key based on function name, args, kwargs, and source code
        try:
            key = (func.__name__, args, frozenset(kwargs.items()), inspect.getsource(func))
        except OSError:
            key = (func.__name__, args, frozenset(kwargs.items()))
        # Serialize the key to a string
        key_str = pickle.dumps(key)
        # Use a hash function to create a unique fingerprint
        return hashlib.sha256(key_str).hexdigest()

# Load state at module level to ensure it's available before any function calls
ResultMemorizer._load_state()
