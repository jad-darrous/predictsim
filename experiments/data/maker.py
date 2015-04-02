
import glob
import os.path, time
import os

class Maker:
	
	def __init__(self, verbose=False):
		self.verbose = verbose

	def listToGlob(self, l):
		if type(l) == list:
			return l[0] + '*' + l[1]
		else:# l is a string
			return l


	def ageOf(self, files):
		files = self.listToGlob(files)
		if type(files) == list:
			fs = []
			for fil in files:
				fs += glob.glob(fil)
		else:
			fs = glob.glob(files)
		if len(fs) == 0:
			return 0
		age = 0
		for f in fs:
			age = max(age, os.path.getmtime(f))
		return age


	def isNewer(self, source, dest):
		return self.ageOf(source) > self.ageOf(dest)


	def doTask(self, source, dest, command):
		
		list_of_task = []
		
		if type(source) == list:
			if type(dest) == list:
				# N to N
				sources = glob.glob(self.listToGlob(source))
				for s in sources:
					list_of_task.append( (s, dest[0] + s[len(source[0]):-len(source[1])] + dest[1], command) )
				
			else:
				# N to 1
				list_of_task.append( (source, dest, command) )
		else:
			if type(dest) == list:
				# 1 to N
				list_of_task.append( (source, dest, command) )
			else:
				# 1 to 1
				list_of_task.append( (source, dest, command) )
			
		
		#print list_of_task
	
		for task in list_of_task:
			src = task[0]
			dst = task[1]
			cmd = task[2]
			
			if( self.isNewer(src, dst) ):
				if self.verbose: print("[Maker]: Source ("+str(src)+") is newer than dest ("+str(dst)+").")
				
			
				os.environ["SOURCE"] = self.listToGlob(source)
				os.environ["SOURCE_GLOB"] = " ".join(glob.glob(self.listToGlob(source)))
				os.environ["DEST"] = self.listToGlob(dest)
				
				os.environ["SOURCE_FILE"] = self.listToGlob(src)
				if type(src) != list:
					os.environ["SOURCE_FILE_SHORT"] = os.path.splitext(os.path.basename(src))[0]
					os.environ["SOURCE_FILE_BASE"] = os.path.basename(src)
				
				os.environ["DEST_FILE"] = self.listToGlob(dst)
				if type(dst) != list:
					os.environ["DEST_FILE_SHORT"] = os.path.splitext(os.path.basename(str(dst)))[0]
					os.environ["DEST_FILE_BASE"] = os.path.basename(str(dst))
				
				if self.verbose: print("[Maker]: Launching: "+str(cmd))
				f = os.popen(cmd)
				out = f.read()
				if out != "":
					print(f.read())
			
			else:
				if self.verbose: print("[Maker]: Nothing to do for "+str(src)+" => "+str(dst)+")")




b = Maker(True)


b.doTask(
	source=["simulations/", ".swf.gz"], dest=["sim_analysis/individual/", ".csv"],
	command="""../../../simulation_analysis/swf2vis_metrics.R $SOURCE_FILE -o $DEST_FILE""")
b.doTask(
	source=["sim_analysis/individual/", ".csv"], dest="sim_analysis/metrics",
	command="../../data_manipulation/merge_to_metrics.sh $SOURCE > $DEST_FILE")

b.doTask(
	source="sim_analysis/metrics", dest="sim_analysis/metrics_complete",
	command="python ../../data_manipulation/fill_metrics.py run.db 'sim_analysis/metrics' > $DEST_FILE")





