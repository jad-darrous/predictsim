#!/usr/bin/env python2.4
from unittest import TestCase

import random

import prototype

from event_queue import EventQueue
import workload_parser

def _gen_random_timestamp_events():
    return [
        prototype.JobEvent(timestamp=random.randrange(0,100), job=str(i))
        for i in xrange(30)
    ]

def _create_handler():
    def handler(event):
        handler.called = True
    handler.called = False
    return handler

class test_Job(TestCase):
    def test_str_sanity(self):
        str(prototype.Job(1, 1, 1, 1))

class test_JobEvent(TestCase):
    def test_str_sanity(self):
        str(prototype.JobEvent(timestamp=11, job=None))

    def test_equal(self):
        e1 = prototype.JobEvent(timestamp=10, job="abc")
        e2 = prototype.JobEvent(timestamp=10, job="abc")
        self.assertEqual(e1, e2)

    def test_nonequal_timestamp(self):
        e1 = prototype.JobEvent(timestamp=10, job="abc")
        e2 = prototype.JobEvent(timestamp=22, job="abc")
        self.assertNotEqual(e1, e2)

    def test_nonequal_job(self):
        e1 = prototype.JobEvent(timestamp=10, job="abc")
        e2 = prototype.JobEvent(timestamp=10, job="def")
        self.assertNotEqual(e1, e2)

    def test_nonequal_type(self):
        e1 = prototype.JobEvent(timestamp=10, job="abc")
        e2 = prototype.JobStartEvent(timestamp=10, job="abc") # different type
        self.assertNotEqual(e1, e2)

    def test_sort_order(self):
        e1 = prototype.JobEvent(timestamp=10, job="abc")
        e2 = prototype.JobEvent(timestamp=22, job="abc")
        self.failUnless( e1 < e2 )
        self.failIf( e1 >= e2 )

    def test_sort_order_random(self):
        random_events = _gen_random_timestamp_events()
        sorted_events = sorted(random_events, key=lambda x:x._cmp_tuple)
        self.assertEqual( sorted_events, sorted(random_events) )

class test_EventQueue(TestCase):
    def setUp(self):
        self.queue = EventQueue()
        self.event = prototype.JobEvent(timestamp=0, job=None)
        self.events = [
                prototype.JobEvent(timestamp=i, job=None)
                for i in xrange(10)
            ]

        self.handler = _create_handler()

    def tearDown(self):
        del self.queue, self.event, self.events, self.handler

    def test_len_empty(self):
        self.assertEqual( 0, len(self.queue) )

    def test_len_nonempty(self):
        for event in self.events:
            self.queue.add_event(event)
        self.assertEqual( len(self.events), len(self.queue) )

    def test_add_event_sanity(self):
        self.queue.add_event( self.event )

    def test_add_event_single_event(self):
        self.queue.add_event(self.event)
        self.assertEqual( [self.event], self.queue.sorted_events )

    def test_add_same_event_fails(self):
        self.queue.add_event(self.event)
        self.assertRaises(Exception, self.queue.add_event, self.event)

    def test_add_event_simple(self):
        for event in self.events:
            self.queue.add_event(event)
        self.assertEqual( self.events, list(self.queue.sorted_events) )

    def test_add_event_sorting(self):
        random_events = _gen_random_timestamp_events()
        for event in random_events:
            self.queue.add_event(event)
        self.assertEqual( sorted(random_events), self.queue.sorted_events )

    def test_remove_event_fails_on_empty(self):
        self.assertRaises(Exception, self.queue.remove_event, self.event)

    def test_remove_event_fails_on_missing_event(self):
        event1 = prototype.JobEvent(0, 0)
        event2 = prototype.JobEvent(0, 1)
        assert event1 != event2 # different events
        self.queue.add_event(event1)
        self.assertRaises(Exception, self.queue.remove_event, event2)

    def test_remove_event_succeeds(self):
        self.queue.add_event(self.event)
        self.queue.remove_event(self.event)
        self.failUnless( self.queue.is_empty )

    def test_pop_one_job(self):
        self.queue.add_event( self.event )
        assert self.queue.pop() is self.event

    def test_pop_many_jobs(self):
        for event in self.events:
            self.queue.add_event(event)
        for event in self.events:
            assert self.queue.pop() is event

    def test_pop_empty(self):
        self.assertRaises(AssertionError, self.queue.pop)

    def test_empty_true(self):
        self.failUnless( self.queue.is_empty )

    def test_empty_false(self):
        self.queue.add_event( self.event )
        self.failIf( self.queue.is_empty )

    def test_add_handler_sanity(self):
        self.queue.add_handler(prototype.JobEvent, self.handler)
        self.queue.add_event(self.event)
        self.failIf( self.handler.called )

    def test_get_event_handlers_empty(self):
        self.assertEqual(
            0, len(self.queue._get_event_handlers( prototype.JobEvent ))
        )

    def test_get_event_handlers_nonempty(self):
        self.queue.add_handler(prototype.JobEvent, self.handler)
        self.assertEqual(
            1, len(self.queue._get_event_handlers( prototype.JobEvent ))
        )

    def test_advance_empty_queue(self):
        self.assertRaises(AssertionError, self.queue.advance)

    def test_advance_eats_event(self):
        self._add_event_and_advance(self.event)
        self.failUnless(self.queue.is_empty)

    def test_add_event_earlier_event_after_later_advance(self):
        # after handling an event with a later timestamp, adding an event with
        # an older timestamp should fail
        self._add_event_and_advance(prototype.JobEvent(timestamp=2, job="x"))
        self.assertRaises(Exception, self.queue.add_event, prototype.JobEvent(timestamp=1, job="x"))

    def test_add_event_same_timestamp_after_advance(self):
        # same timestamp should succeed even after an event has been handled
        self._add_event_and_advance(prototype.JobEvent(timestamp=2, job="x"))
        self.queue.add_event(prototype.JobEvent(timestamp=2, job="y"))

    def test_advance_one_handler_handles(self):
        self.queue.add_handler(prototype.JobEvent, self.handler)
        self._add_event_and_advance(self.event)

        self.failUnless( self.handler.called )

    def test_advance_one_handler_doesnt_handle(self):
        self.queue.add_handler(prototype.JobStartEvent, self.handler)
        self._add_event_and_advance(self.event) # JobEvent, different type

        self.failIf( self.handler.called )

    def test_advance_many_handlers(self):
        matching_handlers = [ _create_handler() for i in xrange(5) ]
        nonmatching_handlers = [ _create_handler() for i in xrange(5) ]

        # register handlers that should run
        for handler in matching_handlers:
            self.queue.add_handler(prototype.JobEvent, handler)

        # register handlers that shouldn't run with a different event type
        for handler in nonmatching_handlers:
            self.queue.add_handler(prototype.JobStartEvent, handler)

        self._add_event_and_advance(self.event)

        for handler in matching_handlers:
            self.failUnless( handler.called )

        for handler in nonmatching_handlers:
            self.failIf( handler.called )

    def test_sometimes_relevant_handler(self):
        self.queue.add_handler(prototype.JobEvent, self.handler)
        self._add_event_and_advance(prototype.JobEvent(timestamp=0, job="x"))
        self.failUnless(self.handler.called)
        self.handler.called = False
        self._add_event_and_advance(prototype.JobStartEvent(timestamp=1, job="x"))
        self.failIf(self.handler.called)
        self._add_event_and_advance(prototype.JobEvent(timestamp=2, job="x"))
        self.failUnless(self.handler.called)

    def _add_event_and_advance(self, event):
        self.queue.add_event(event)
        self.queue.advance()

# taken from LANL-CM5-1994-3.1-cln.swf
SAMPLE_JOB_INPUT = """
    5     4009      7   3039  128   2605  1812  128   3600  3200  1   9   8   6  1 -1 -1 -1
    6     4031      5   6253   32 476.00  1004   32    300  1024  0   3   3   3  1 -1 -1 -1
    7     4346     15   2412   32  64.00  6408   32    300  6400  1   6   5   3  1 -1 -1 -1
    8     4393      5    986   32 534.00  2476   32   3300  3840  1   5   4   3  1 -1 -1 -1
    9     4684      6     25  512     -1    -1  512   1800 32768  1   4   1   4  5 -1 -1 -1
   10     5705      3   1105  128  53.00  1732  128   3600  4000  1   7   6   3  1 -1 -1 -1
   11     5872  52632  23087  128  21615  7684  128  21600 32768  0  41   6  22  9 -1 -1 -1
   12     5999      5   1609   32   1198  2476   32   1800  3840  1   5   4   3  1 -1 -1 -1
   13     6063      4    245  512 189.00  8420  512   1800 32768  1   4   1   4  5 -1 -1 -1
   14     6765      4   8908  256   8286  3732  256  10800 32768  1  22  18  15  2 -1 -1 -1
   15     6796      4    300   64  66.00  4940   64    300  4800  1   6   5   3  1 -1 -1 -1
   16     6955      7     48   32   1.00  9140   32    300  1024  1   8   7   5  1 -1 -1 -1
   17     7071      5     23   32     -1  2344   32    300  1024  1   8   7   5  1 -1 -1 -1
   18     7219      8     23   32     -1  2327   32    300  1024  1   8   7   5  1 -1 -1 -1
   19     7307      3    441  128 392.00  7148  128    480  8192  1  11  10   7  1 -1 -1 -1
""".strip().splitlines()

class test_Simulator(TestCase):
    def setUp(self):
        self.jobs = list(prototype._job_inputs_to_jobs(workload_parser.parse_lines(SAMPLE_JOB_INPUT), 1000))
        self.scheduler = prototype.StupidScheduler()

        self.simulator = prototype.Simulator(
            jobs = self.jobs,
            num_processors = 1000,
            scheduler = self.scheduler,
        )

    def tearDown(self):
        del self.simulator

    def test_init_event_queue(self):
        self.assertEqual(
            set(job.id for job in self.jobs),
            set(event.job.id for event in self.simulator.event_queue.events)
        )

    def test_jobs_done(self):
        done_jobs_ids=[]

        def job_done_handler(event):
            done_jobs_ids.append(event.job.id)

        self.simulator.event_queue.add_handler(prototype.JobTerminationEvent, job_done_handler)

        self.simulator.run()

        self.assertEqual(
            set(job.id for job in self.jobs),
            set(done_jobs_ids),
        )

    def test_job_input_to_job(self):
        job_input = workload_parser.JobInput(SAMPLE_JOB_INPUT[0])
        from prototype import _job_input_to_job
        job = _job_input_to_job(job_input, job_input.num_requested_processors)

        self.assertEqual( job.id, job_input.number )
        self.assertEqual( job.user_estimated_run_time, job_input.requested_time )
        self.assertEqual( job.actual_run_time, job_input.run_time )
        self.assertEqual( job.num_required_processors, job_input.num_requested_processors )

class test_simple_job_generator(TestCase):
    def test_unique_id(self):
        previously_seen = set()
        for start_time, job in prototype.simple_job_generator(num_jobs=200):
            self.failIf( job.id in previously_seen )
            previously_seen.add( job.id )

    def test_nondescending_start_times(self):
        prev_time = 0
        for start_time, job in prototype.simple_job_generator(num_jobs=200):
            self.failUnless( start_time >= prev_time )
            prev_time = start_time

def unique_numbers():
    current = 0
    while True:
        current += 1
        yield current

class test_ValidatingMachine(TestCase):
    def setUp(self):
        self.event_queue = EventQueue()
        self.machine = prototype.ValidatingMachine(50, self.event_queue)
        self.unique_numbers = unique_numbers()

    def tearDown(self):
        del self.event_queue, self.machine, self.unique_numbers

    def _unique_job(self, user_estimated_run_time=100, actual_run_time=60, num_required_processors=20):
        return prototype.Job(
                id = self.unique_numbers.next(),
                user_estimated_run_time = user_estimated_run_time,
                actual_run_time = actual_run_time,
                num_required_processors = num_required_processors
            )

    def test_no_jobs_on_init(self):
        self.assertEqual(0, len(self.machine.jobs))

    def test_add_job(self):
        job = self._unique_job()
        self.machine._add_job(job, current_timestamp=0)
        assert job in self.machine.jobs

    def test_add_several_jobs_success(self):
        for i in xrange(5):
            self.machine._add_job( self._unique_job(num_required_processors=5), current_timestamp=0 )

    def test_add_job_too_big(self):
        self.assertRaises(Exception, self.machine._add_job, self._unique_job(num_required_processors=100), current_timestamp=0)

    def test_add_second_job_too_big(self):
        self.machine._add_job( self._unique_job(num_required_processors=40), current_timestamp=0 )
        self.assertRaises(Exception, self.machine._add_job, self._unique_job(num_required_processors=40), current_timestamp=0 )

    def test_free_processors_empty(self):
        self.assertEqual(50, self.machine.free_processors)

    def test_free_processors_nonempty(self):
        for i in xrange(10):
            self.machine._add_job(self._unique_job(num_required_processors=3), current_timestamp=0)
        self.assertEqual(20, self.machine.free_processors)

    def test_free_processors_full(self):
        self.machine._add_job(self._unique_job(num_required_processors=50), current_timestamp=0)
        self.assertEqual(0, self.machine.free_processors)

    def test_busy_processors_empty(self):
        self.assertEqual(0, self.machine.busy_processors)

    def test_busy_processors_nonempty(self):
        for i in xrange(10):
            self.machine._add_job(self._unique_job(num_required_processors=3), current_timestamp=0)
        self.assertEqual(30, self.machine.busy_processors)

    def test_busy_processors_full(self):
        self.machine._add_job(self._unique_job(num_required_processors=50), current_timestamp=0)
        self.assertEqual(50, self.machine.busy_processors)

    def test_add_job_adds_job_end_event(self):
        self.machine._add_job(self._unique_job(), current_timestamp=0)
        self.failIf(self.event_queue.is_empty)

    def test_job_done_removed(self):
        self.machine._add_job(self._unique_job(), current_timestamp=0)
        self.event_queue.advance()
        self.assertEqual(0, self.machine.busy_processors)

    def test_add_job_different_current_timestamp(self):
        self.machine._add_job(current_timestamp=100, job=self._unique_job(actual_run_time=20, num_required_processors=10))
        self.machine._add_job(current_timestamp=120, job=self._unique_job(actual_run_time=40, num_required_processors=5))
        self.event_queue.advance()
        self.assertEqual(5, self.machine.busy_processors)

    def test_add_job_different_current_timestamp2(self):
        self.machine._add_job(current_timestamp=110, job=self._unique_job(actual_run_time=20, num_required_processors=10))
        self.machine._add_job(current_timestamp=100, job=self._unique_job(actual_run_time=40, num_required_processors=5))
        self.event_queue.advance()
        self.assertEqual(5, self.machine.busy_processors)

    def test_start_job_handler(self):
        job = self._unique_job()

        self.event_queue.add_event(
            prototype.JobStartEvent( timestamp=0, job=job )
        )
        self.event_queue.advance()

        assert job in self.machine.jobs


class test_StupidScheduler(TestCase):
    def setUp(self):
        self.scheduler = prototype.StupidScheduler()

    def tearDown(self):
        del self.scheduler

    def test_job_submitted_creates_job_start_event(self):
        job = prototype.Job(id=1, user_estimated_run_time=100, actual_run_time=60, num_required_processors=20)

        new_events = self.scheduler.handleSubmissionOfJobEvent(job=job, timestamp=0)

        self.failUnless( prototype.JobStartEvent in (type(x) for x in new_events) )

if __name__ == "__main__":
    try:
        import testoob
        testoob.main()
    except ImportError:
        import unittest
        unittest.main()
