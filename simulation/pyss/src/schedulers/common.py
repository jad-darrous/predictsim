
def list_copy(my_list):
        result = []
        for i in my_list:
            result.append(i)
        return result

def list_print(my_list):
	for i in my_list:
            print i 
        print


class Scheduler(object):
    """
    Assumption: every handler returns a (possibly empty) collection of new events
    """
    def __init__(self, num_processors):
        self.num_processors = num_processors

    def new_events_on_job_submission(self, job, current_time):
        raise NotImplementedError()

    def new_events_on_job_termination(self, job, current_time):
        raise NotImplementedError()

class CpuTimeSlice(object):
    """
    represents a "tentative feasible" snapshot of the cpu between the
    start_time until start_time + dur_time.  It is tentative since a job might
    be rescheduled to an earlier slice. It is feasible since the total demand
    for processors ba all the jobs assigned to this slice never exceeds the
    amount of the total processors available.
    Assumption: the duration of the slice is never changed.
    We can replace this slice with a new slice with shorter duration.
    """

    def __init__(self, free_processors, start_time, duration, total_processors):
        assert duration > 0
        assert start_time >= 0
        assert total_processors > 0
        assert 0 <= free_processors <= total_processors

        self.total_processors = total_processors
        self.free_processors = free_processors
        self.start_time = start_time
        self.duration = duration

        self.job_ids = set()

    @property
    def end_time(self):
        return self.start_time + self.duration

    @property
    def busy_processors(self):
        return self.total_processors - self.free_processors

    def addJob(self, job):
        assert job.num_required_processors <= self.free_processors, job
        assert job.id not in self.job_ids, "job.id = "+str(job.id)+", job_ids "+str(self.job_ids)
        self.free_processors -= job.num_required_processors
        self.job_ids.add(job.id)

    def delJob(self, job):
        assert job.num_required_processors <= self.busy_processors, job
        self.free_processors += job.num_required_processors
        self.job_ids.remove(job.id)

    def __str__(self):
        return '%d %d %d %s' % (self.start_time, self.duration, self.free_processors, self.job_ids)

    def quick_copy(self): # copy the slice without the set of job_ids 
        result = CpuTimeSlice(
                free_processors = self.free_processors,
                start_time = self.start_time,
                duration = self.duration,
                total_processors = self.total_processors,
            )

        return result


    def copy(self):
        result = CpuTimeSlice(
                free_processors = self.free_processors,
                start_time = self.start_time,
                duration = self.duration,
                total_processors = self.total_processors,
            )

        result.job_ids = self.job_ids.copy()

        return result

    def split(self, split_time):
        first = self.copy()
        first.duration = split_time - self.start_time

        second = self.copy()
        second.start_time = split_time
        second.duration = self.end_time - split_time

        return first, second


class CpuSnapshot(object):
    """
    represents the time table with the assignments of jobs to available processors
    """
    # Assumption: the snapshot always has at least one slice
    def __init__(self, total_processors):
        self.total_processors = total_processors
        self.slices=[]
        self.slices.append(CpuTimeSlice(self.total_processors, start_time=0, duration=1000, total_processors=total_processors))
        self.archive_of_old_slices=[]
        
    @property
    def snapshot_end_time(self):
        assert len(self.slices) > 0
        return self.slices[-1].end_time


    def _ensure_a_slice_starts_at(self, start_time):
        """
        A preprocessing stage.
        
        Usage:
        First, to ensure that the assignment time of the new added job will
        start at a beginning of a slice.

        Second, to ensure that the actual end time of the job will end at the
        ending of slice.  we need this for adding a new job, or for deleting a tail
        of job when the user estimation is larger than the actual duration.

        The idea: we first append 2 slices, just to make sure that there's a
        slice which ends after the start_time.  We add one more slice just
        because we actually use list.insert() when we add a new slice.
        After that we iterate through the slices and split a slice if needed.
        """

        if self._slice_starts_at(start_time):
            return # already have one

        if start_time < self.snapshot_end_time:
            # split an existing slice
            index = self._slice_index_to_split(start_time)

            # splitting slice s with respect to the start time
            slice = self.slices.pop(index)
            self.slices[index:index] = slice.split(start_time)
            return

        if start_time > self.snapshot_end_time:
            # add slice until start_time
            self._append_time_slice(self.total_processors, start_time - self.snapshot_end_time)
            assert self.snapshot_end_time == start_time

	# add a tail slice, duration is arbitrary whenever start_time >= self.snapshot_end_time
	self._append_time_slice(self.total_processors, 1000)


    def _slice_starts_at(self, time):
        for slice in self.slices:
            if slice.start_time == time:
                return True
        return False # no slice found

    def _slice_index_to_split(self, split_time):
        assert not self._slice_starts_at(split_time)

        for index, slice in enumerate(self.slices):
            if slice.start_time < split_time < slice.end_time:
                return index

        assert False # should never reach here


    def _append_time_slice(self, free_processors, duration):
        self.slices.append(CpuTimeSlice(free_processors, self.snapshot_end_time, duration, self.total_processors))


    def free_processors_available_at(self, time):
        for s in self.slices:
            if s.start_time <= time < s.end_time:
                return s.free_processors
        return self.total_processors

    def canJobStartNow(self, job, current_time):
        return self.jobEarliestAssignment(job, current_time) == current_time

    def jobEarliestAssignment(self, job, time):
        """
        returns the earliest time right after the given time for which the job
        can be assigned enough processors for job.predicted_run_time unit of
        times in an uninterrupted fashion.
        Assumptions: the given is greater than the submission time of the job >= 0.
        """
        assert job.num_required_processors <= self.total_processors, str(self.total_processors)

        self._append_time_slice(self.total_processors, time + job.predicted_run_time + 1)

        partially_assigned = False
        tentative_start_time = accumulated_duration = 0

        assert time >= 0

        for s in self.slices: # continuity assumption: if t' is the successor of t, then: t' = t + duration_of_slice_t
            if s.end_time <= time or s.free_processors < job.num_required_processors:
                # the job can't be assigned to this slice, need to reset
                # partially_assigned and accumulated_duration
                partially_assigned = False
                accumulated_duration = 0

            elif not partially_assigned:
                # we'll check if the job can be assigned to this slice and perhaps to its successive
                partially_assigned = True
                tentative_start_time =  max(time, s.start_time)
                accumulated_duration = s.end_time - tentative_start_time

            else:
                # job is partially_assigned:
                accumulated_duration += s.duration

            if accumulated_duration >= job.predicted_run_time:
                self.slices[-1].duration = 1000 # making sure that the last "empty" slice we've just added will not be huge
                return tentative_start_time

        assert False # should never reach here


    def _slices_time_range(self, start, end):
        assert self._slice_starts_at(start), "start time is: " + str(start) 
        assert self._slice_starts_at(end), "end time is: " + str(end)

        return (s for s in self.slices if start <= s.start_time < end)


    def delJobFromCpuSlices(self, job):
        """
        Deletes an _entire_ job from the slices.
        Assumption: job resides at consecutive slices (no preemptions), and
        nothing is archived!
        """
        for s in self._slices_time_range(job.start_to_run_at_time, job.predicted_finish_time):
            s.delJob(job)

	    
    def delTailofJobFromCpuSlices(self, job):
        """
        This function is used when the actual duration is smaller than the
        estimated duration, so the tail of the job must be deleted from the
        slices. We iterate trough the sorted slices until the critical point is found:
        the point from which the tail of the job starts.
        Assumptions: job is assigned to successive slices.  
        """
        for s in self._slices_time_range(job.finish_time, job.predicted_finish_time):
            s.delJob(job)

    def assignTailofJobToTheCpuSlices(self, job):
	"""
	This function extends the duration of a job, if the predicted duration is smaller
	than the user estimated duration, then the function adds more slices to the job accordingly.
	
	"""
	if job.user_estimated_run_time <= job.predicted_run_time:
		return

	job_estimated_finish_time = job.start_to_run_at_time + job.user_estimated_run_time	
        self._ensure_a_slice_starts_at(job_estimated_finish_time)
        for s in self._slices_time_range(job.predicted_finish_time, job_estimated_finish_time):
            s.addJob(job)

	job.predicted_run_time = job.user_estimated_run_time

	    

    def assignJob(self, job, job_start):
        """
        assigns the job to start at the given job_start time.
        Important assumption: job_start was returned by jobEarliestAssignment.
        """
        job.start_to_run_at_time = job_start
        self._ensure_a_slice_starts_at(job_start)
        self._ensure_a_slice_starts_at(job.predicted_finish_time)
        for s in self._slices_time_range(job_start, job.predicted_finish_time):
            s.addJob(job)
	    

    def assignJobEarliest(self, job, time):
        self.assignJob(job, self.jobEarliestAssignment(job, time))


    def archive_old_slices(self, current_time):
        assert self.slices
	self.unify_slices()
        self._ensure_a_slice_starts_at(current_time)

	size = len(self.slices)
	while size > 0:
	    s = self.slices[0]
            if s.end_time <= current_time:
                self.archive_of_old_slices.append(s)
                self.slices.pop(0)
		size -= 1 
            else:
                break
	
       
    def unify_slices(self):
        assert self.slices

        # optimization
	if len(self.slices) < 10:
		return

        prev = self.slices[0]
        # use a copy so we don't change the container while iterating over it
        for s in list_copy(self.slices[1: ]):
	    assert s.start_time == prev.start_time + prev.duration
            if s.free_processors == prev.free_processors and s.job_ids == prev.job_ids:
                prev.duration += s.duration
                self.slices.remove(s)
            else:
                prev = s


    def _restore_old_slices(self):
        size = len(self.archive_of_old_slices)
        while size > 0:
            size -= 1
            s = self.archive_of_old_slices.pop()
            self.slices.insert(0, s)

    def printCpuSlices(self, str=None):
        if str is not None: 
		print str
        print "start time | duration | #free processors | jobs"
	for s in self.archive_of_old_slices:
	    print s 
        for s in self.slices:
            print s
        print


    def copy(self):
        result = CpuSnapshot(self.total_processors)
        result.slices = [slice.copy() for slice in self.slices]
        return result
    
    def quick_copy(self):
        result = CpuSnapshot(self.total_processors)
        result.slices = [slice.quick_copy() for slice in self.slices]
        return result

    def CpuSlicesTestFeasibility(self):
        self._restore_old_slices()
        duration = 0
        time = 0

        for s in self.slices:
            prev_duration = duration
            prev_time = time

            if s.free_processors < 0 or s.free_processors > self.total_processors:
                print ">>> PROBLEM: number of free processors is either negative or huge", s
                return False

            if s.start_time != prev_time + prev_duration:
                print ">>> PROBLEM: non successive slices", s.start_time, prev_time
                return False

            duration = s.duration
            time = s.start_time

        return True

    def CpuSlicesTestEmptyFeasibility(self):
        self._restore_old_slices()
        duration = 0
        time = 0

        for s in self.slices:
            prev_duration = duration
            prev_time = time

            if s.free_processors != self.total_processors:
                print ">>> PROBLEM: number of free processors is not the total processors", s
                return False

            if s.start_time != prev_time + prev_duration:
                print ">>> PROBLEM: non successive slices", s.start_time, prev_time
                return False

            duration = s.duration
            time = s.start_time

        return True

