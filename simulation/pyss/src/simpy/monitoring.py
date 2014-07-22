"""
This module contains SimPy's monitoring capabilities.

The :class:`Monitor` is the central class to collect and store data
from your simulation.

It can use different back ends to define how the data is stored (e.g.,
in plain lists, in a database or even in an Excel sheet if you want).
All back ends should inherit :class:`Backend`. SimPy has three built-in
back end types: :class:`ListBackend` (the default),
:class:`NamedtupleBackend` and :class:`PrinterBackend`.

You can also automatically collect data when a certain method is called
(e.g., ``Resource.request()`` or ``Container.put()``). The function
:func:`patch()` patches an object to automatically call
:meth:`Monitor.collect()` before or after a method call.

SimPy offers two shortcut functions to patch a resource
(:func:`resource_monitor()`) and a container/store
(:func:`container_monitor()`). They are using the collector functions
returned by :func:`resource_collector()` and
:func:`container_collector()`, respectively.

"""
import collections


class Monitor(object):
    """Monitors can be used to (semi-)automatically collect data from
    processes, resources and other objects involved in a simulation.

    A monitor consists of a collector and a back end. The collector is
    responsible for retrieving the required data from a process,
    resource or something else. The back end then stores that data in
    some place. By default, the :class:`ListBackend` is used which
    simply appends everything that the collector returns to a list.


    Before a monitor can be used, it has to be configured via
    :meth:`configure()`. You can then simply call :meth:`collect()` to
    to collect and add data to it. You can access the data via the
    :attr:`data` property.

    The monitor also offers a simple process :meth:`run()` that
    automatically collects data in user defined intervals.

    """
    def __init__(self):
        self._backend = None
        self._collector = None

    @property
    def data(self):
        """All collected data. Its type depends on the back end used."""
        return self._backend.data

    def run(self, env, collect_interval=1):
        """A simple process that calls :meth:`collect()` every
        *collect_interval* steps.

        *env* is a :class:`~simpy.Environment` instance.

        """
        while True:
            self.collect()
            yield env.timeout(collect_interval)

    def configure(self, collector, backend=None):
        """Configure the *collector* function and the *backend*.

        The collector can be any callable with no arguments. It should
        usually return a list or tuple with the collected values.

        Per default, the :class:`ListBackend` is used as back end. You
        can pass an instance of another back end type to change this.
        Back ends need to have *data* attribute and implement an
        *append()* method that takes that data returned by the collector
        and appends it to *data*.

        """
        self._collector = collector
        if not backend:
            backend = ListBackend()
        self._backend = backend

    def collect(self):
        """Call the collector and append the collected data to the monitor."""
        data = self._collector()
        self._backend.append(data)


class Backend(object):
    """Base class for all backends."""
    data = None

    def append(self, data):
        """Append *data* to ``self.data``."""
        raise NotImplementedError


class ListBackend(Backend):
    """This is the default backend. It just appends all data to a list."""
    def __init__(self):
        self.data = []

    def append(self, data):
        """Append *data* to ``self.data``."""
        self.data.append(data)


class NamedtupleBackend(Backend):
    """Stores collected data as :func:`collections.namedtuple()`.

    *field_names* is the list of attribute names that are passed to
    :func:`~collections.namedduple()`.

    """
    def __init__(self, attributes):
        self._Item = collections.namedtuple('Item', attributes)
        self.data = []

    def append(self, data):
        """Create a :func:`~collections.namedtuple()` from data and append
        it to ``self.data``.

        """
        self.data.append(self._Item._make(data))


class PrinterBackend(Backend):
    """Just prints all collected values to *stdout*.

    The string *prefix* is prepended to every line.

    """
    def __init__(self, prefix=''):
        self._prefix = prefix

    def append(self, data):
        """Print *data* to stdout."""
        print(self._prefix + str(data))


# class H5pyBackend(Backend):
#     def __init__(self, h5file, groupname='', attributes):
#         self.h5file = h5file
#         self.groupname = groupname
#         if groupname:
#             self.data = h5file.create_group(groupname)
#         else:
#             self.data = h5file
#         self.datasets = []
#         self.size = 10  # TODO: Dynamically increase size
#         self._next_index = 0
#
#         for name, dtype in attributes:
#             ds = self.data.create_dataset(name, self.size, dtype=dtype)
#             self.datasets.append(ds)
#
#     def append(self, data):
#         # TODO: Collect data in memory and continuously add it to
#         # the dataset.
#         # Make self.data a property that flushes the buffer on each
#         # access.
#         for i, d in enumerate(data):
#             self.datasets[i][self._next_index] = d
#         self._next_index += 1
#
#
# # Hdf5Monitor
# m = Monitor()
# b = H5pyBAckend(h5py.File('/tmp/test.hdf5', 'w', driver='stdio'), 'groupname',
#                 [('a', int), ('b', float)])
# m.configure(lambda: a, b, backend=b)


def patch(obj, monitor, pre_call=(), post_call=()):
    """Monkey patch some of methods of *obj* to automatically call
    *monitor's* :meth:`~Monitor.collect()` method when they are called.

    *pre_call* and *post_call* are lists containing method names.

    Patch all methods in *pre_call* to call :meth:`Monitor.collect()`
    just before they are called. Patch all methods in *post_call* to
    call :meth:`Monitor.collect()` after they were called.  A method
    name can be in both lists at the same time.

    """
    def get_wrapper(obj, name, monitor, pre, post):
        orig_method = getattr(obj, name)

        def call_and_collect(*args, **kwargs):
            if pre:
                monitor.collect()
            ret = orig_method(*args, **kwargs)
            if post:
                monitor.collect()
            return ret

        return call_and_collect

    names = set(pre_call) | set(post_call)
    for name in names:
        wrapper = get_wrapper(obj, name, monitor, name in pre_call,
                              name in post_call)
        setattr(obj, name, wrapper)


def resource_monitor(resource, backend=None):
    """Shortcut for creating a resource monitor.

    The :class:`Monitor` returned is already configured. The *resource*
    is monkey patched to automatically call its
    :meth:`~Monitor.collect()` method before each *request* and
    *release*.

    It works for :class:`~simpy.resources.Resource` and its subclasses.
    It collects the current simulation time, the users and the
    the queue every time ``request()`` or ``release()`` were
    called (see :func:`resource_collector()` for details).

    You can optionally specify a custom *backend*.

    """
    monitor = Monitor()
    monitor.configure(resource_collector(resource), backend=backend)
    patch(resource, monitor, pre_call=('request', 'release'))
    return monitor


def resource_collector(resource, include_time=True):
    """Return a collector method for *resource*.

    This collector works for :class:`~simpy.resources.Resource` and its
    subclasses. It collects lists or process IDs for each, the
    resource's users and queue. If *include_time* is ``True``, it also
    collects the current simulation time.

    It either returns ``(time, user_ids, queued_ids)`` or ``(user_ids,
    queued_ids)``, where the time is a number (usually an ``int``, but
    maybe a ``float`` or something else) and the other values are
    lists of strings.

    This information allows you to analyze how many processes were using
    (or waiting for) the resource at any time and how long a process
    was using the resource or waiting for it.

    """
    def collector():
        data = (resource.count, len(resource.get_queued()))
        data = (
            [str(id(proc)) for proc in resource.get_users()],
            [str(id(proc)) for proc in resource.get_queued()],
        )
        if include_time:
            data = (resource._env.now,) + data
        return data
    return collector


def container_monitor(container, backend=None):
    """Shortcut for creating a container monitor.

    The :class:`Monitor` returned is already configured. The *container*
    is monkey patched to automatically call its
    :meth:`~Monitor.collect()` method before each *put* and *get*.

    It works for :class:`~simpy.resources.Container`,
    :class:`~simpy.resources.Store` and their subclasses. It collects
    the current simulation time, the *count* or *level* and the process
    IDs of all processes in the put/get queue every time ``put()``,
    ``get()`` or ``release()`` were called (see
    :func:`container_collector()` for details).

    You can optionally specify a custom *backend*.

    """
    monitor = Monitor()
    monitor.configure(container_collector(container), backend=backend)
    patch(container, monitor, pre_call=('put', 'get', 'release'))
    return monitor


def container_collector(container, include_time=True):
    """Return a collector method for *container*.

    This collector works for :class:`~simpy.resources.Container`,
    :class:`~simpy.resources.Store` and their subclasses. It collects
    its level/count and a lists for the processes's IDs in each, the put
    and get queue. If *include_time* is ``True``, it also collects the
    current simulation time.

    It either returns ``(time, level, put_queued_ids, get_queued_ids)`` or
    ``(level, put_queued_ids, get_queued_ids)``, where the time is a number
    (usually an ``int``, but maybe a ``float`` or something else), the
    count or level is an integer for ``Store`` and (usually a float for
    ``Container`` and the remaining two values are lists of strings.

    This information allows you to analyze how many processes were
    waiting to put something in or get something out of the resource at
    any time and how long a process was waiting for it.

    """
    def collector():
        if hasattr(container, 'level'):
            level = container.level
        else:
            level = container.count
        data = (
            level,
            [str(id(proc)) for proc in container.get_put_queued()],
            [str(id(proc)) for proc in container.get_get_queued()],
        )
        if include_time:
            data = (container._env.now,) + data
        return data
    return collector
