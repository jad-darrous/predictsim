'''
	Utilities function used to manipulate swf log files.
'''


from itertools import compress, dropwhile

swf_skip_hdr = lambda u: u.lstrip().startswith(';');
swf_skip_hdr_itr = lambda _file: dropwhile(swf_skip_hdr, _file)


def split_swf(in_file_name, tpercent, parts, dir="./"):

	def write_to_file(fname, jobs):
		out = open(fname, "w")
		out.write('\n'.join(jobs));
		out.close()

	jobs = []
	with open(in_file_name) as f:
		for line in dropwhile(swf_skip_hdr, f):
			jobs.append(line.strip());

	training_size = int(len(jobs) * tpercent)
	part_size = training_size / parts
	training_size = part_size * parts

	str_name_format = "%s/%s_part%%d.swf" % (dir, in_file_name.split('.')[0])

	training_files = []

	for i in range(parts):
		fname = str_name_format % (i+1)
		training_files.append(fname)
		write_to_file(fname, jobs[i*part_size:(i+1)*part_size])

	test_file = "%s/%s_test.swf" % (dir, in_file_name.split('.')[0])
	write_to_file(test_file, jobs[training_size:])

	return training_files, test_file


def conv_features(fname, qid, indices=None):

	if indices is not None:
		mask = [i in indices for i in range(1, 19)]
		size = mask.count(True)
	else:
		size = 18
		mask = [True] * 18

	rng = range(1, size+1)

	score = 1000000-1;
	lines = []
	with open(fname) as f:
		for line in dropwhile(swf_skip_hdr, f):
			job = [int(float(u)) for u in line.strip().split()];
			l = compress(job, mask)
			t = ' '.join(map(lambda v: "%d:%d" % v, zip(rng, l)))
			lines.append("{0} qid:{1} {2}".format(score, qid, t))
			score-=1

	return '\n'.join(lines)



def getMaxProcs(fname):
	with open(fname) as f:
		for line in f.readlines():
			if "; MaxProcs:" in line:
				return int(line.strip().split()[-1])
	raise NameError('No MaxProcs in the log\'s header')


def compute_utilisation(fname):
	first, last, procs, sum_area = float("inf"), 0, getMaxProcs(fname), 0
	with open(fname) as f:
		for line in dropwhile(swf_skip_hdr, f):
			st, wt, rt, pr = [float(v) for v in [u for u in line.strip().split()][1:5]]
			first = min(first, st + wt)
			last = max(last, wt + rt + st)
			sum_area += rt * pr

	print "procs =", procs, "last = ", last, "first = ", first, "sum_area", sum_area
	vals = sum_area / (1.0 * procs * (last-first))
	print vals*100, "%"
	return vals