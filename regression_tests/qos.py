"""
    Quality of Service (QoS) support.
"""

import logging
import time


class WithQoS:
    """A wrapper around other objects providing Quality of Service (QoS)
    support.

    Basically, it wraps a created object. Upon a method call, it delegates it
    to the wrapped object. If it raises an exception, it retries this call
    after some specified wait time. This is done for the given maximal number
    of times. Each failed method call is logged.

    .. warning::

        Does not work on properties/descriptors at the moment.
    """

    def __init__(self, obj, max_tries=5, wait_time=None):
        """
        :param obj: Object to be wrapped.
        :param int max_tries: Maximal number of tries.
        :param int wait_time: Number of seconds to wait between successive
                              tries.
        """
        self._obj = obj
        self._max_tries = max_tries
        self._wait_time = wait_time

    def __getattribute__(self, attr):
        method = getattr(object.__getattribute__(self, '_obj'), attr)
        max_tries = object.__getattribute__(self, '_max_tries')
        wait_time = object.__getattribute__(self, '_wait_time')
        return _MethodWithQoS(method, max_tries, wait_time)


class _MethodWithQoS:
    """An internal method wrapper."""

    def __init__(self, method, max_tries, wait_time):
        self._method = method
        self._max_tries = max_tries
        self._wait_time = wait_time

    def __call__(self, *args, **kwargs):
        max_tries = self._max_tries
        while max_tries > 0:
            try:
                return self._method(*args, **kwargs)
            except Exception as ex:
                max_tries = self._raise_when_no_try_left(max_tries)
                self._log(ex)
                self._wait()

    def _raise_when_no_try_left(self, max_tries):
        max_tries = max_tries - 1
        if max_tries == 0:
            raise
        return max_tries

    def _log(self, ex):
        logging.exception('caught {}; will retry'.format(ex.__class__.__name__))

    def _wait(self):
        if self._wait_time:
            time.sleep(self._wait_time)
