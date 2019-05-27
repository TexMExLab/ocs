import threading
from contextlib import contextmanager

class TimeoutLock:
    def __init__(self):
        self.job = None
        self._lock = threading.Lock()

    def acquire(self, blocking=True, timeout=-1):
        return self._lock.acquire(blocking, timeout)

    def release(self):
        self._lock.release()

    @contextmanager
    def acquire_timeout(self, timeout, job='unnamed'):
        result = self._lock.acquire(timeout=timeout)

        if result:
            self.job = job
            try:
                yield result
            finally:
                self.job = None
                self._lock.release()

        else:
            yield result


def in_reactor_context():
    """
    Determine whether the current threading context is the twisted
    main (reactor) thread, or a worker pool thread.  Returns True if
    it's the main thread.  Will raise RuntimeError if the thread name
    is confusing.
    """
    t = threading.currentThread()
    if 'PoolThread' in t.name:
        return False
    if 'MainThread' in t.name:
        return True
    raise RuntimeError('Could not determine threading context: '
                       'currentThread.name="%s"' % t.name)
