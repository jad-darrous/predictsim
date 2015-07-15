from common import CpuSnapshot

from collections import deque

import sys
sys.path.append("..")


from run_simulator import parse_and_run_simulator
from swf_utils import *

from io_utils import *
from batch_learning_to_rank import *
from scheduling_performance_measurement import *

import os
import gc

import time
import multiprocessing

from base.prototype import JobStartEvent

from base.workload_parser import parse_lines
from base.prototype import _job_inputs_to_jobs, _job_inputs_to_jobs_with_wait



def gen_weights():
    import random
    weights_options = set()
    weights_options.add((1, 0, 0, 0, 0, 0))
    weights_options.add((0, 1, 0, 0, 0, 0))
    w = [0] * 6
    for _ in range(100):
        for i in range(6):
            w[i] = random.randint(0, 5)
            m = min(w)
            w = map(lambda u: u-m, w)
        weights_options.add(tuple(w))
    # weights_options = sorted(weights_options)
    # print "#weights_options", len(weights_options), weights_options
    weights_options = []
    for x1 in range(-3, 4):
        for x2 in range(-3, 4):
            for x3 in range(-3, 4):
                weights_options.append((x1, x2, 0,0,0, x3))
    return weights_options


class Weights(object):
    # this class defines the configuration of weights for the MAUI
    def __init__(self, w_wtime=1, w_sld=0, w_user=0, w_bypass=0, w_admin=0, w_size=0, w_l2r=0):
        self.wtime  = w_wtime  # weight of wait time since submission
        self.sld    = w_sld    # weight of slow down
        self.user   = w_user   # weight of user desired quality of service
        self.bypass = w_bypass # weight of being skipped over in the waiting list
        self.admin  = w_admin  # weight of asmin desired quality of service
        self.size   = w_size   # weight of job size (= num_required_processors)
        self.l2r    = w_l2r    # the l2r hypothesis


# a first toy version for the maui -- essentially the difference between this
# simplified version of maui and easy backfilling is that the maui has another
# degree of freedom: maui may consider the jobs not necessarily by order of
# submission, as opposed to the easy backfill.

from easy_backfill_scheduler import EasyBackfillScheduler

class AdaptiveMauiScheduler(EasyBackfillScheduler):

    job_per_part = 500

    config = {
        "scheduler": {
            "name":'maui_scheduler',
            "progressbar": False,
            },
        "stats": False,
        "verbose": False
    }

    weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0)]

    def __init__(self, options, weights_list=None, weights_backfill=None):
        super(AdaptiveMauiScheduler, self).__init__(options)

        self.maui_counter = 0

        # weights for calculation of priorities for the jobs in MAUI style
        if weights_list is not None:
            self.weights_list = Weights(*weights_list)
        else:
            self.weights_list = Weights() # sort the jobs by order of submission

        if weights_backfill is not None:
            self.weights_backfill = Weights(*weights_backfill)
        else:
            self.weights_backfill = Weights() # sort the jobs by order of submission

        self.curr_part_num = 0
        self.curr_jobs_num = 0
        self.curr_model_fn = None
        self.best_all = deque()
        self.queries = deque()
        self.terminated_jobs = []

        self.out_dir = "out/out_" + str(int(time.time()))
        os.system("mkdir " + self.out_dir)
        print "pwd:", self.out_dir

        self.rel = lambda fn: "%s/%s" % (self.out_dir, fn);

        AdaptiveMauiScheduler.config["num_processors"] = self.num_processors
        AdaptiveMauiScheduler.weights_options = gen_weights()
        AdaptiveMauiScheduler.weights_options = [(0, 1, 0, 0, 0, 0)]


    def _update_weights_list(self, best_weights):
        self.weights_list = Weights(*best_weights)
        self.weights_backfill = Weights(*best_weights)

    def new_events_on_job_submission(self, just_submitted_job, current_time):
        "Overriding parent method"
        just_submitted_job.maui_counter = self.maui_counter
        self.maui_counter += 1
        return super(AdaptiveMauiScheduler, self).new_events_on_job_submission(just_submitted_job, current_time)

    def new_events_on_job_termination(self, job, current_time):

        self.terminated_jobs.append(AdaptiveMauiScheduler._convert_job_to_str(job))
        self.curr_jobs_num += 1

        if self.curr_jobs_num == AdaptiveMauiScheduler.job_per_part:
            self.curr_jobs_num = 0
            self.curr_part_num += 1

            training_file = self.rel("train.swf")
            write_lines_to_file(training_file, self.terminated_jobs)

            # gc.collect()

            self.terminated_jobs[:] = []

            best_weights = self._prepare_training_set_file(training_file)
            print "best_weights", best_weights
            self._update_weights_list(best_weights)

        return super(AdaptiveMauiScheduler, self).new_events_on_job_termination(job, current_time)


    def new_events_on_job_under_prediction(self, job, current_time):
        assert job.predicted_run_time <= job.user_estimated_run_time

        if not hasattr(job,"num_underpredict"):
            job.num_underpredict = 0
        else:
            job.num_underpredict += 1

        if self.corrector.__name__=="ninetynine":
            new_predicted_run_time = self.corrector(self.pestimator,job,current_time)
        else:
            new_predicted_run_time = self.corrector(job, current_time)

        #set the new predicted runtime
        self.cpu_snapshot.assignTailofJobToTheCpuSlices(job, new_predicted_run_time)
        job.predicted_run_time = new_predicted_run_time

        return [JobStartEvent(current_time, job)]


    # @staticmethod
    def _prepare_training_set_file(self, training_file):

        def simulate(path):
            config = AdaptiveMauiScheduler.config
            out_swf = []
            for idx, w in enumerate(AdaptiveMauiScheduler.weights_options):
                config["weights"] = w
                config["input_file"] = path
                config["output_swf"] = "%s_%d_%d.swf" % (path.split('.')[0], self.curr_part_num, idx)
                parse_and_run_simulator(config)
                out_swf.append((w, config["output_swf"]))
                # out_swf.append(config["terminated_jobs"])
            # gc.collect() # to ensure that the output files are closed
            return out_swf

        redirect_sim_output = True

        # Redirect the stdout temporary to get rid of simulator output.
        if redirect_sim_output: sys.stdout = open('/dev/null', 'w')

        out_swf = simulate(training_file)

        # Redirect the stdout again to its default state.
        if redirect_sim_output: sys.stdout = sys.__stdout__

        best = float("inf")
        for idx, swf in enumerate(out_swf):
            obj_fun_val = BoundedSlowdown(swf[1]).average()
            if obj_fun_val < best:
                best = obj_fun_val
                index = idx
                outf = swf[0]
        return outf

    @staticmethod
    def _convert_job_to_str(job):
        outl = []
        #1. Job Number
        outl.append(str(job.id))
        #2. Submit Time
        outl.append(str(job.submit_time))
        #3. Wait Time
        outl.append(str(job.start_to_run_at_time - job.submit_time))
        #4. Run Time
        outl.append(str(job.actual_run_time))
        #5. Number of Allocated Processors
        outl.append(str(job.num_required_processors))
        #6. Average CPU Time Used
        outl.append("-1")
        #7. Used Memory
        outl.append("-1")
        #8. Requested Number of Processors.
        outl.append(str(job.num_required_processors))
        #9. Requested Time
        outl.append(str(job.user_estimated_run_time))
        #10. Requested Memory
        outl.append("-1")
        #11. Status. This field is meaningless for models, so would be -1.
        outl.append("-1")
        #12. User ID
        outl.append(str(job.user_id))
        #13. Group ID
        outl.append("-1")
        #14. Executable (Application) Number
        outl.append("-1")
        #15. Queue Number
        outl.append("-1")
        #16. Partition Number
        if hasattr(job,"is_backfilled"):
            outl.append(str(job.is_backfilled))
        else:
            outl.append("-1")
        #17. Preceding Job Number
        if hasattr(job,"num_underpredict"):
            outl.append(str(job.num_underpredict))
        else:
            outl.append("-1")
        #18. Think Time
        if hasattr(job,"initial_prediction"):
            outl.append(str(job.initial_prediction))
        else:
            outl.append("-1")

        return ' '.join(outl)


    def _schedule_jobs(self, current_time):
        "Overriding parent method"
        self.unscheduled_jobs.sort(
                # TODO
                key = lambda x: self.waiting_list_weight(x, current_time),
                reverse=True
            )

        return super(AdaptiveMauiScheduler, self)._schedule_jobs(current_time)

    def _unscheduled_jobs_in_backfilling_order(self, current_time):
        # sort the tail, keep the first job first
        return self.unscheduled_jobs[0:1] + \
            sorted(self.unscheduled_jobs[1:], key=lambda x: self.backfilling_weight(x, current_time), reverse=True )

    def _backfill_jobs(self, current_time):
        "Overriding parent method"
        self.unscheduled_jobs = self._unscheduled_jobs_in_backfilling_order(current_time)

        result = super(AdaptiveMauiScheduler, self)._backfill_jobs(current_time)

        for job in result:
            self.increment_bypass_counters(job)

        return result

    def increment_bypass_counters(self, backfilled_job):
        for job in self.unscheduled_jobs:
            if job.maui_counter < backfilled_job.maui_counter:
                job.maui_bypass_counter += 1

    def aggregated_weight_of_job(self, weights, job, current_time):

        return job.think_time

        wait = current_time - job.submit_time # wait time since submission of job
        sld = (wait + job.user_estimated_run_time) /  job.user_estimated_run_time

        # print job.think_time,
        return (
            weights.wtime  * wait +
            weights.sld    * sld +
            weights.user   * job.user_QoS +
            weights.bypass * job.maui_bypass_counter +
            weights.admin  * job.admin_QoS +
            weights.size   * job.num_required_processors +
            weights.l2r    * job.think_time
        )

    def waiting_list_weight(self, job, current_time):
        return self.aggregated_weight_of_job(self.weights_list, job, current_time)

    def backfilling_weight(self, job, current_time):
        return self.aggregated_weight_of_job(self.weights_backfill, job, current_time)

    def print_waiting_list(self):
        for job in self.unscheduled_jobs:
            print job, "bypassed:", job.maui_bypass_counter
        print
