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


import math
import itertools

def extract_features(job, rt=None):
    x = []
    T = x.append

    T(job.submit_time)
    T(job.start_to_run_at_time - job.submit_time)
    T(job.actual_run_time)
    T(job.num_required_processors)
    T(job.user_estimated_run_time)

    return tuple(str(i) for i in x)

    T(1)
    # Submit time (F. 2)
    # T(job.submit_time)
    # Predicted run-time, instead of actuacl_run_time (F. 4)
    if rt is None:
        T(job.actual_run_time)
    else:
        T(rt)
    # Requested time (F. 9)
    T(job.user_estimated_run_time)
    # Required/Allocated procs (F. 5 & 8)
    T(job.num_required_processors)

    # second of day
    sec_of_day = 2.0*math.pi*float(job.submit_time % (3600*24))/(3600.0*24.0)
    T(math.cos(sec_of_day))
    T(math.sin(sec_of_day))
    # day of week trough seconds
    day_of_week = 2.0*math.pi*float(job.submit_time % (3600*24*7))/(3600.0*24.0*7.0)
    T(math.cos(day_of_week))
    T(math.sin(day_of_week))

    # for a,b,c in itertools.combinations(x[1:],3):
    #     T(a*b*c)

    return tuple(str(i) for i in x)


def train(lib, train_fn, model_fn):
    lib.train(train_fn, model_fn)


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

class OnlineL2RMauiScheduler(EasyBackfillScheduler):

    # I_NEED_A_PREDICTOR = True

    max_parts_num = 1000
    job_per_part = 500

    out_dir = "out_"

    rel = lambda self, fn: "%s/%s" % (OnlineL2RMauiScheduler.out_dir, fn);

    indices = (2,3,4,5,9)
    # indices = (2,3,4) # best
    # indices = (3,4,10,11,12,13)

    config = {
        "scheduler": {
            "name":'maui_scheduler',
            "progressbar": False,
            },
        "stats": False,
        "verbose": False
    }

    def __init__(self, options, weights_list=None, weights_backfill=None):
        super(OnlineL2RMauiScheduler, self).__init__(options)

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

        self.init_predictor(options)
        self.init_corrector(options)

        self.curr_part_num = 0
        self.curr_jobs_num = 0
        self.curr_model_fn = None
        self.best_all = deque()
        self.queries = deque()
        self.terminated_jobs = []

        OnlineL2RMauiScheduler.out_dir = "out/out_" + str(int(time.time()))
        os.system("mkdir " + OnlineL2RMauiScheduler.out_dir)
        print "pwd:", OnlineL2RMauiScheduler.out_dir

        self.batchL2Rlib = SVM_Rank(OnlineL2RMauiScheduler.out_dir)

        self.every = 0

        from ctypes import cdll, c_char_p
        self.lib = cdll.LoadLibrary('libs/lib_svm_rank_classify_single.so')
        self.lib.rank.restype = c_char_p
        # self.lib.print_help()

        OnlineL2RMauiScheduler.config["num_processors"] = self.num_processors

        self.oldF = False


    def new_events_on_job_submission(self, just_submitted_job, current_time):
        "Overriding parent method"
        just_submitted_job.maui_counter = self.maui_counter
        self.maui_counter += 1

        # just_submitted_job.actual_run_time = just_submitted_job.user_estimated_run_time
        # self.predictor.predict(just_submitted_job, current_time, self.running_jobs)
        # just_submitted_job.actual_run_time = just_submitted_job.predicted_run_time

        if self.curr_model_fn is None:
            just_submitted_job.think_time = just_submitted_job.submit_time
        else:
            test_fn = "test.txt"

            if self.oldF:
                lst_str_job = [OnlineL2RMauiScheduler._convert_job_to_str(just_submitted_job)]
                mat = extract_columns_from_itr(lst_str_job, OnlineL2RMauiScheduler.indices)
                # mat = normalize_mat(mat, min_max)
                features = convert_to_ml_format(mat, 0)[0]
            else:
                f = extract_features(just_submitted_job, rt=just_submitted_job.predicted_run_time)
                features = convert_job_to_ml_format(f, score=99999)

            # print features
            write_str_to_file(self.rel(test_fn), features+'\n')

            # gc.collect()

            score_str = self.lib.rank(self.rel(test_fn))
            just_submitted_job.think_time = int(float(score_str) * 1000)

        return super(OnlineL2RMauiScheduler, self).new_events_on_job_submission(just_submitted_job, current_time)


    def new_events_on_job_termination(self, job, current_time):

        # self.predictor.fit(job, current_time)

        self.terminated_jobs.append(OnlineL2RMauiScheduler._convert_job_to_str(job))
        self.curr_jobs_num += 1

        if self.curr_jobs_num == OnlineL2RMauiScheduler.job_per_part:
            self.curr_jobs_num = 0
            self.curr_part_num += 1

            training_file = self.rel("train.swf")
            write_lines_to_file(training_file, self.terminated_jobs)

            # gc.collect()

            self.terminated_jobs[:] = []

            outf = self._prepare_training_set_file(training_file)
            # print "outf", outf
            if self.curr_part_num >= OnlineL2RMauiScheduler.max_parts_num:
                self.best_all.popleft()
                self.queries.popleft()
            self.best_all.append(outf)

            if self.oldF:
                query = OnlineL2RMauiScheduler._convert_to_ml_query(outf, self.curr_part_num)
            else:
                x = parse_lines(open(outf))
                jobs = _job_inputs_to_jobs_with_wait(x, self.num_processors)
                jobs_str = map(lambda u: extract_features(u), jobs)
                query = convert_jobs_to_ml_format(jobs_str, self.curr_part_num)
            self.queries.append(query)

            self.every += 1
            self.every %= 10
            if self.every == 0:
                train_fn = 'train.txt'
                # features = OnlineL2RMauiScheduler._merge_and_create_ml_training_file(\
                #     self.best_all)
                write_lines_to_file(self.rel(train_fn), self.queries)
                model_fn = "model_{0}.txt".format(self.curr_part_num)

                # ## single process trainin
                # self.batchL2Rlib.train(train_fn, model_fn)
                # self.curr_model_fn = model_fn
                # print "curr_model_fn:", self.curr_model_fn
                # self.lib.update_model(self.rel(self.curr_model_fn))

                ## training in another thread
                p = multiprocessing.Process(target=train, \
                    args=(self.batchL2Rlib, train_fn, model_fn))
                p.start()
                p.join(50 * 60)

                # If thread is still active
                if p.is_alive():
                    print "running... let's kill it..."
                    p.terminate()
                    p.join()
                else:
                    self.curr_model_fn = model_fn
                    print "curr_model_fn:", self.curr_model_fn
                    self.lib.update_model(self.rel(self.curr_model_fn))

        return super(OnlineL2RMauiScheduler, self).new_events_on_job_termination(job, current_time)


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

        weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0)]

        def simulate(path):
            config = OnlineL2RMauiScheduler.config
            out_swf = []
            for idx, w in enumerate(weights_options):
                config["weights"] = w
                config["input_file"] = path
                config["output_swf"] = "%s_%d_%d.swf" % (path.split('.')[0], self.curr_part_num, idx)
                parse_and_run_simulator(config)
                out_swf.append(config["output_swf"])
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
            obj_fun_val = BoundedSlowdown(swf).average()
            if obj_fun_val < best:
                best = obj_fun_val
                index = idx
                outf = swf
        # print index, best

        return outf

    @staticmethod
    def _merge_and_create_ml_training_file(best_all):

        indices = OnlineL2RMauiScheduler.indices

        # print "[Creating the ML training file..]"
        cols_matrix = [[] for i in range(len(indices))]
        for idx, fname in enumerate(best_all):
            cols = extract_columns(fname, indices)
            for i in range(len(indices)):
                cols_matrix[i].extend(cols[i])

        global min_max
        min_max = map(lambda u: (min(u), max(u)), cols_matrix)
        # print min_max

        features = []
        for idx, fname in enumerate(best_all):
            mat = extract_columns(fname, indices)
            # mat = normalize_mat(mat, min_max)
            queries = convert_to_ml_format(mat, idx+1)
            features.extend(queries)

        return features

    @staticmethod
    def _convert_to_ml_query(swf, qid):

        indices = OnlineL2RMauiScheduler.indices
        mat = extract_columns(swf, indices)
        lines = convert_to_ml_format(mat, qid)
        return '\n'.join(lines)

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

        return super(OnlineL2RMauiScheduler, self)._schedule_jobs(current_time)

    def _unscheduled_jobs_in_backfilling_order(self, current_time):
        # sort the tail, keep the first job first
        return self.unscheduled_jobs[0:1] + \
            sorted(self.unscheduled_jobs[1:], key=lambda x: self.backfilling_weight(x, current_time), reverse=True )

    def _backfill_jobs(self, current_time):
        "Overriding parent method"
        self.unscheduled_jobs = self._unscheduled_jobs_in_backfilling_order(current_time)

        result = super(OnlineL2RMauiScheduler, self)._backfill_jobs(current_time)

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
