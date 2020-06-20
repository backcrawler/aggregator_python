from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from django.db import connection


class DjangoConnectionThreadPoolExecutor(ThreadPoolExecutor):
    """
    Extending ThreadPoolExecutor class in order to ensure there will be no DB leaks
    when applied inside Django. Function passed to the instance is wrapped with custom decorator so
    close_django_db_connection() must be called inside the thread when it's finished
    """
    def close_django_db_connection(self):
        connection.close()

    def generate_thread_closing_wrapper(self, fn):
        @wraps(fn)
        def new_func(*args, **kwargs):
            try:
                res = fn(*args, **kwargs)
            except Exception as e:
                self.close_django_db_connection()
                raise e
            else:
                self.close_django_db_connection()
                return res
        return new_func

    def submit(*args, **kwargs):
        """The args filtering/unpacking logic is from
        https://github.com/python/cpython/blob/3.7/Lib/concurrent/futures/thread.py
        """
        if len(args) >= 2:
            self, fn, *args = args
            fn = self.generate_thread_closing_wrapper(fn=fn)
        elif not args:
            raise TypeError("descriptor 'submit' of 'ThreadPoolExecutor' object "
                        "needs an argument")
        elif 'fn' in kwargs:
            fn = self.generate_thread_closing_wrapper(fn=kwargs.pop('fn'))  # not an error, self is passed anyway
            self, *args = args

        return super(self.__class__, self).submit(fn, *args, **kwargs)