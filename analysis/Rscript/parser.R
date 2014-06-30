library("argparse")

#Parser for both swf and cgn files.

#almost empty parser, just help.
parser_help<-function(description,epilog){
	parser<-ArgumentParser(description=description,epilog=epilog)
	return(parser)
}

#minimal parser for a Rscript. no formatting options except ratio.
parser_minimal<-function(description,epilog){
	parser<-ArgumentParser(description=description,epilog=epilog)
	parser$add_argument('-v', '--verbose', action='store_true', default=FALSE, help='print extra output',dest='verbosity')
	parser$add_argument('-o', '--output',metavar='FILE',default='',type='character', help='output filename')
	parser$add_argument('-d', '--device',dest='device',default='x11',metavar='DEVICE',type='character', help='R device for the output: pdf,x11,x11-notcl.  x11 by default. Use x11-notcl if you do not have the tcl package or if you hate popup messages!!')
	parser$add_argument('-r', '--ratio',default=1 ,metavar='INTEGER',type='integer', help='width to height ratio for the output graphics. 1 by default.')
	return(parser)
}

#basic parser for a Rscript.
parser_common<-function(description,epilog){
	parser<-ArgumentParser(description=description,epilog=epilog)
	parser$add_argument('-v', '--verbose', action='store_true', default=FALSE, help='print extra output',dest='verbosity')
	parser$add_argument('-o', '--output',metavar='FILE',default='',type='character', help='output filename')
	parser$add_argument('-d', '--device',dest='device',default='x11',metavar='DEVICE',type='character', help='R device for the output: pdf,x11,x11-notcl.  x11 by default. Use x11-notcl if you do not have the tcl package or if you hate popup messages!!')
	parser$add_argument('-r', '--ratio',default=1 ,metavar='INTEGER',type='integer', help='width to height ratio for the output graphics. 1 by default.')
	parser$add_argument('-g','--grey', dest='grey', action='store_true', default=FALSE,help='plot in grayscale')
	parser$add_argument('-l','--labels',dest='labels', nargs='+',metavar='STRING',default='',type='character',help='plot labels')
	parser$add_argument('-lt','--labelstitle',dest='labelstitle', nargs='+',metavar='STRING',default='',type='character',help='plot labels title')


	return(parser)
}

#parser to load both cgn and swf files.
parser_swf_cgn<-function(description,epilog){
	parser<-parser_common(description,epilog)
	parser$add_argument('-s', '--swf_input',dest='swf_filenames',nargs='+',metavar='FILE',type='character', help='input swf file(s)',required=TRUE)
	parser$add_argument('-c', '--cgn_input',dest='cgn_filenames',nargs='+',metavar='FILE',type='character', help='input cgn file(s)')
	return(parser)
}

#parser to load cgn files.
parser_cgn<-function(description,epilog){
	parser<-parser_common(description,epilog)
	parser$add_argument('-c', '--cgn_input',dest='cgn_filenames',nargs='+',metavar='FILE',type='character', help='input cgn file(s)')
	return(parser)
}

#parser to load column files.
parser_pred<-function(description,epilog){
	parser<-parser_common(description,epilog)
	parser$add_argument('pred_filenames',nargs='+',metavar='FILE',type='character', help='input file(s). first file is the true value')
	return(parser)
}


#parser to load swf files.
parser_swf<-function(description,epilog){
	parser<-parser_common(description,epilog)
	parser$add_argument('swf_filenames',nargs='+',metavar='FILE',type='character', help='input swf file(s)')
	return(parser)
}

parser_cli<-function(description,epilog){
	parser<-ArgumentParser(description=description,epilog=epilog)
	parser$add_argument('-v', '--verbose', action='store_true', default=FALSE, help='print extra output',dest='verbosity')
	return(parser)
}
parser_cli_swf<-function(description,epilog){
	parser<-parser_cli(description,epilog)
	parser$add_argument('swf_filenames',nargs='+',metavar='FILE',type='character', help='input swf file(s)')
	return(parser)

}

#swf parser that asks for cores
parser_swf_with_cores<-function(description,epilog){
	parser<-parser_swf(description,epilog)
	parser$add_argument('-c','--cores',nargs='+',dest='cores',metavar='INTEGER',type='integer', help='amount of cores in the system. will be generated with the max_cores method if not given.')
	return(parser)
}

parser_swf_minimal <- function( description,epilog ) {
	parser<-parser_minimal(description,epilog)
	parser$add_argument('swf_filenames',nargs='+',metavar='FILE',type='character', help='input swf file(s)')
	return(parser)
}

