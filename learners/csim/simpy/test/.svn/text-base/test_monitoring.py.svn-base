"""
Test cases for SimPy's monitoring capabilities.

"""
# Pytest gets the parameters "env" and "log" from the *conftest.py* file
import pytest

from simpy import monitoring
import simpy


def get_resource_monitor(resource):
    monitor = monitoring.Monitor()
    monitor.configure(monitoring.resource_collector(resource))
    monitoring.patch(resource, monitor, pre_call=('request', 'release'))
    return monitor


def test_whitebox_monitor_implicit(env):
    """*Whitebox monitoring* means that the user monitors the attributes
    of a process from within the process and has thus full access to all
    attributes.  If the process is just a simple method, the
    :class:`~simpy.monitoring.Monitor` has to be passed to it when it is
    activated.

    """
    def pem(env, monitor):
        a = 0
        monitor.configure(lambda: (env.now, a))  # Configure the monitor

        while True:
            a += env.now
            monitor.collect()  # Collect data
            yield env.timeout(1)

    monitor = monitoring.Monitor()
    env.start(pem(env, monitor))
    simpy.simulate(env, 5)

    assert monitor.data == [(0, 0), (1, 1), (2, 3), (3, 6), (4, 10)]


def test_whitebox_monitor_data_object(env):
    """If the *PEM* is an instance method of an object,
    a :class:`~simpy.monitoring.Monitor` can be configured to
    automatically collect a nummber of instance attributes.

    """
    class Spam(object):
        def __init__(self, env):
            self.env = env
            self.a = 0
            self.monitor = monitoring.Monitor()
            self.monitor.configure(lambda: (self.env.now, self.a))
            self.process = env.start(self.pem())

        def pem(self):
            while True:
                self.a += self.env.now
                self.monitor.collect()
                yield self.env.timeout(1)

    spam = Spam(env)  # Spam.__init__ starts the PEM
    simpy.simulate(env, 5)

    assert spam.monitor.data == [(0, 0), (1, 1), (2, 3), (3, 6), (4, 10)]


def test_blackbox_monitor_processes(env):
    """A :class:`~simpy.monitoring.Monitor` also provides a process
    method (:meth:`Monitor.run()`) that collects data from a number of
    objects in regular intervals.

    """
    class Spam(object):
        def __init__(self, env):
            self.a = 0
            self.process = env.start(self.pem(env))

        def pem(self, env):
            while True:
                self.a += env.now
                yield env.timeout(1)

    spams = [Spam(env) for i in range(2)]
    monitor = monitoring.Monitor()

    # configure also accepts a generator that creates a number of
    # collector functions:
    monitor.configure(lambda: [env.now] + [spam.a for spam in spams])
    env.start(monitor.run(env, collect_interval=1))

    simpy.simulate(env, 3)
    assert monitor.data == [
        # (env.now, spam[0].a, spam[1].a)
        [0, 0, 0],
        [1, 1, 1],
        [2, 3, 3],
    ]


def test_namedtuple_backend(env):
    """Monitors can use custom backends to store their data, e.g.
    :func:`~collections.namedtuple()`.

    """
    def pem(env, monitor):
        a = 0
        monitor.configure(collector=lambda: (env.now, a),
                          backend=monitoring.NamedtupleBackend('t, a'))

        while True:
            a += env.now
            monitor.collect()  # Collect data
            yield env.timeout(1)

    monitor = monitoring.Monitor()
    env.start(pem(env, monitor))
    simpy.simulate(env, 5)

    Item = monitor._backend._Item
    assert monitor.data == [Item(0, 0), Item(1, 1), Item(2, 3), Item(3, 6),
                            Item(4, 10)]


def test_printer_backend(env, capsys):
    """The print backend just prints all data to stdout."""
    def pem(env, monitor):
        a = 0
        monitor.configure(collector=lambda: (env.now, a),
                          backend=monitoring.PrinterBackend('x'))

        while True:
            a += env.now
            monitor.collect()  # Collect data
            yield env.timeout(1)

    monitor = monitoring.Monitor()
    env.start(pem(env, monitor))
    simpy.simulate(env, 5)

    assert monitor.data is None
    out, err = capsys.readouterr()
    assert out == 'x(0, 0)\nx(1, 1)\nx(2, 3)\nx(3, 6)\nx(4, 10)\n'
    assert err == ''


@pytest.mark.parametrize('res_mon', [
    get_resource_monitor,
    monitoring.resource_monitor,
])
def test_resource_monitor(env, res_mon):
    def pem(env, resource, wait, use):
        yield env.timeout(wait)
        with resource.request() as req:
            yield req
            yield env.timeout(use)

    resource = simpy.Resource(env, 2)
    monitor = res_mon(resource)
    env.start(pem(env, resource, 0, 1))
    env.start(pem(env, resource, 0, 2))
    env.start(pem(env, resource, 0, 1))
    env.start(pem(env, resource, 3, 3))
    env.start(pem(env, resource, 3, 1))
    env.start(pem(env, resource, 4, 1))
    simpy.simulate(env)
    monitor.collect()

    # Convert the data and replace the ID-lists with their length.
    monitor._backend.data = [(t, len(u), len(g)) for t, u, g in monitor.data]

    assert monitor.data == [
        (0, 0, 0), (0, 1, 0), (0, 2, 0),
        (1, 2, 1),
        (2, 2, 0), (2, 1, 0),
        (3, 0, 0), (3, 1, 0),
        (4, 2, 0), (4, 2, 1),
        (5, 2, 0),
        (6, 1, 0),
        (6, 0, 0),
    ]


@pytest.mark.parametrize(('pre_call', 'post_call', 'expected'), [
    (['request', 'release'], [], [(0, 0, 0), (1, 1, 0)]),
    ([], ['request', 'release'], [(0, 1, 0), (1, 0, 0)]),
    (['request', 'release'], ['request', 'release'], [(0, 0, 0), (0, 1, 0),
                                                      (1, 1, 0), (1, 0, 0)]),
])
def test_object_patching(env, pre_call, post_call, expected):
    """Test if the object patching and the "pre_call" and "post_call"
    prameters work as expected."""
    def pem(env, resource):
        with resource.request() as req:
            yield req
            yield env.timeout(1)

    resource = simpy.Resource(env, 1)
    monitor = monitoring.Monitor()
    monitor.configure(monitoring.resource_collector(resource))
    monitoring.patch(resource, monitor, pre_call=pre_call, post_call=post_call)
    env.start(pem(env, resource))
    simpy.simulate(env)

    # Convert the data and replace the ID-lists with their length.
    monitor._backend.data = [(t, len(u), len(q)) for t, u, q in monitor.data]

    assert monitor.data == expected


def test_container_monitor(env):
    def pem(container, store):
        yield container.put(1)
        yield container.get(0.5)
        yield store.put(1)
        yield store.get()

    container = simpy.Container(env, 1)
    mon1 = monitoring.container_monitor(container)
    store = simpy.Store(env, 1)
    mon2 = monitoring.container_monitor(store)
    env.start(pem(container, store))
    simpy.simulate(env)
    mon1.collect()
    mon2.collect()

    # Convert the data and replace the ID-lists with their length.
    mon1._backend.data = [(t, l, len(p), len(g)) for t, l, p, g in mon1.data]
    mon2._backend.data = [(t, l, len(p), len(g)) for t, l, p, g in mon2.data]

    assert mon1.data == [(0, 0, 0, 0), (0, 1, 0, 0), (0, 0.5, 0, 0)]
    assert mon2.data == [(0, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 0)]
