#!/usr/bin/env python3
"""
This script demonstrates a Cache class that uses Redis for storing data,
along with decorators to count calls and log call history.
"""
import redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''Decorator to count how many times methods of Cache class are called'''
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''Wrap the decorated function and return the wrapper'''
        # Increment the count of method calls in Redis
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    '''Decorator to store the history of inputs and
    outputs for a particular function
    '''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''Wrap the decorated function and return the wrapper'''
        # Store input arguments in Redis
        input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input)
        # Execute the method and store the output in Redis
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", output)
        return output
    return wrapper


def replay(fn: Callable):
    '''Function to display the history of calls of a particular function.'''
    r = redis.Redis()
    func_name = fn.__qualname__
    # Get the count of function calls
    c = r.get(func_name)
    try:
        c = int(c.decode("utf-8"))
    except Exception:
        c = 0
    print("{} was called {} times:".format(func_name, c))
    # Retrieve and print input-output history from Redis
    inputs = r.lrange("{}:inputs".format(func_name), 0, -1)
    outputs = r.lrange("{}:outputs".format(func_name), 0, -1)
    for inp, outp in zip(inputs, outputs):
        try:
            inp = inp.decode("utf-8")
        except Exception:
            inp = ""
        try:
            outp = outp.decode("utf-8")
        except Exception:
            outp = ""
        print("{}(*{}) -> {}".format(func_name, inp, outp))


class Cache:
    '''Cache class for storing data in Redis with call tracking and history'''
    def __init__(self):
        '''Initialize Redis connection and flush any existing data'''
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''Store data in Redis and return a unique key'''
        rkey = str(uuid4())
        self._redis.set(rkey, data)
        return rkey

    def get(self,
            key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        '''Retrieve data from Redis and optionally apply
        a conversion function
        '''
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        '''Retrieve data as a string'''
        value = self._redis.get(key)
        return value.decode("utf-8")

    def get_int(self, key: str) -> int:
        '''Retrieve data as an integer'''
        value = self._redis.get(key)
        try:
            value = int(value.decode("utf-8"))
        except Exception:
            value = 0
        return value


if __name__ == "__main__":
    cache = Cache()

    # Store a binary data and print the returned key
    data = b"hello"
    key = cache.store(data)
    print(key)

    # Fetch and print the data from Redis using the key
    local_redis = redis.Redis()
    print(local_redis.get(key))
