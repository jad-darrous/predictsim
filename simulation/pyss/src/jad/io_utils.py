from os.path import basename
import os

def write_str_to_file(path, _str):
	with open(path, 'w') as f:
		f.write(_str)
		f.flush()
		os.fsync(f.fileno())
		# assert f.write(_str) == len(_str)

def write_lines_to_file(path, lines):
	# write_str_to_file(path, '\n'.join(lines))
	# return
	with open(path, 'w') as f:
		f.writelines(line+'\n' for line in lines)
		f.flush()
		os.fsync(f.fileno())

def simple_name(path):
	return basename(path).split('.')[0]