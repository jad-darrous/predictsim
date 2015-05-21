
from abc import ABCMeta, abstractmethod
from os import system


libs_dir = 'libs'
train_log_fn = 'svm_rank_learn.log'
classify_log_fn = 'svm_rank_classify.log'


class BatchLearningToRank:
	__metaclass__ = ABCMeta

	@abstractmethod
	def train(self, train_fn, model_fn):
		pass

	@abstractmethod
	def classify(self, test_fn, model_fn, cl_out_fn):
		pass

	#def __str__(self):return ""


class SVM_Rank(BatchLearningToRank):

	def __init__(self, out_dir):
		self.out_dir = out_dir

	def train(self, train_fn, model_fn):
		# -t 2 -g 0.8
		# -t 1 -d 2 -s 100 -r 77 
		system("{0}/svm_rank_learn -c 3 {1}/{2} {1}/{3} > {1}/{4}". \
			format(libs_dir, self.out_dir, train_fn, model_fn, train_log_fn))

	def classify(self, test_fn, model_fn, cl_out_fn):
		system("{0}/svm_rank_classify -v 3 {1}/{2} {1}/{3} {1}/{4} > {1}/{5}". \
			format(libs_dir, self.out_dir, test_fn, model_fn, cl_out_fn, classify_log_fn))


class RankLib(BatchLearningToRank):

	def __init__(self, out_dir):
		self.out_dir = out_dir

	def train(self, train_fn, model_fn):
		system("java -jar {0}/RankLib.jar -ranker 0 -train {1}/{2} -save {1}/{3} > {1}/{4}". \
			format(libs_dir, self.out_dir, train_fn, model_fn, train_log_fn))

	def classify(self, test_fn, model_fn, cl_out_fn):
		system("java -jar {0}/RankLib.jar -rank {1}/{2} -load {1}/{3} -score {1}/{4} > {1}/{5}". \
			format(libs_dir, self.out_dir, test_fn, model_fn, cl_out_fn, classify_log_fn))

		lst = []
		with open(rel(cl_out_fn)) as in_f:
			lst = map(lambda u: u.split()[-1] if len(u) > 0 else "", in_f.read().split('\n'))
		# print lst
		with open(rel(cl_out_fn), 'w') as out_f:
			out_f.write('\n'.join(lst))
 
