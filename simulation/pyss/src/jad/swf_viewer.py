#!/usr/bin/pypy
# encoding: utf-8
'''
Convert a .swf file to HTML page to let it be easy for human analysis.

Usage:
	swf_viewer.py <swf_file> [<html_file>] [-n] [-v] [-r]

Options:
	-h --help			Show this help message and exit.
	-v --verbose		Be verbose.
	-n --normalize		Normalize jobs IDs.
	-r --identical		Remove identical columns.
'''

from base.docopt import docopt
import sys
import itertools

hdrs = ["Job Number", "Submit Time", "Wait Time", "Run Time", "Number of Allocated Processors", "Average CPU Time Used", "Used Memory", "Requested Number of Processors", "Requested Time", "Requested Memory", "Status", "User ID", "Group ID", "Executable (Application) Number", "Queue Number", "Partition Number", "Preceding Job Number", "Think Time from Preceding Job"];

clos = len(hdrs)

html_header = """
<!doctype html>
<html>
<head>
	<title>SWF Viewer - %s</title>
	<style>
		th {
			FONT-SIZE: 13px; FONT-STYLE: normal;
			font-family: Verdana, Arial, Sans-Serif, Verdana;
			font-weight: bold;
			color: #0018cb;
		}
		.right {
			float:left;
		}
		.hide {
			display:none
		}
	</style>
	<script>
		function toggle_messege() {
			if (document.getElementById("href_about").innerHTML == '-') {
				document.getElementById("href_about").innerHTML = '+';
				document.getElementById("div_messege").style.display = 'none';
			} else {
				document.getElementById("href_about").innerHTML = '-';
				document.getElementById("div_messege").style.display = 'inline';
			}
		}
	</script>
</head>
<body>
<a class="right" href="javascript:toggle_messege()" id='href_about'>+</a> <br />
""";

if __name__ == "__main__":
	#Retrieve arguments
	arguments = docopt(__doc__, version='1.0.0rc2')

	verbose = arguments["-v"]
	input_file = arguments["<swf_file>"]

	if arguments["<html_file>"] is None:
		output_file = "{0}.html".format(input_file.split(".")[0])
	else:
		output_file = arguments["<html_file>"]

	if verbose:	print "[SWF-Viewer] Reading the swf file.."

	info = []
	jobs = []
	with open(input_file) as f:
		for line in f:
			if not line.lstrip().startswith(';'):
				jobs.append([int(u) for u in line.strip().split()]);
			else:
				info.append(line.strip().split(';')[1])

	if arguments["-r"]:
		if verbose:	print "[SWF-Viewer] Filtering attributes.."
		rm_idx = set()
		for idx in range(2, clos):
			vals = set()
			for job in jobs:
				vals.add(job[idx])
				if len(vals) > 1: break
			if len(vals) == 1:
				rm_idx.add(idx)
		mask = [i not in rm_idx for i in range(clos)]
	else:
		mask = [True] * clos

	if verbose:	print "[SWF-Viewer] Writing the html page.."

	out = open(output_file, "w")
	out.write(html_header % arguments["<swf_file>"]);

	out.write("<div id='div_messege' class='hide'>\n");
	out.write("<p>")
	for i in info:
		out.write("%s<br />" % i)
	out.write("</p>")
	out.write("</div>\n")

	out.write("<table border=\"1\"><tbody>")

	out.write("<tr>")
	for idx, h in enumerate(itertools.compress(hdrs, mask)):
		out.write("<th>%s</th>" % h)
	out.write("</tr>\n")

	for job in jobs:
		for idx, pr in enumerate(itertools.compress(job, mask)):
			out.write("<td>%i</td>" % pr)
		out.write("</tr>\n")

	out.write("</tbody></table>")
	out.write("</body></html>")
	out.close()

	if verbose:	 print "[SWF-Viewer] Conversion done:", input_file, "-->", output_file
