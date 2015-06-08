from os.path import basename


def write_str_to_file(path, _str):
	with open(path, 'w') as f:
		f.write(_str)
		# assert f.write(_str) == len(_str)

def write_lines_to_file(path, lines):
	# write_str_to_file(path, '\n'.join(lines))
	# return
	with open(path, 'w') as f:
		f.writelines("%s\n" % line for line in lines)

def simple_name(path):
	return basename(path).split('.')[0]