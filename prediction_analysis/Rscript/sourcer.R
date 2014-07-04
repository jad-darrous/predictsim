#######BEGINNING OF PATH AND SOURCING MADNESS, Do not alter or you will spend 8 hours on stackoverflow trying to solve your issue.
initial.options <- commandArgs(trailingOnly = FALSE)
file.arg.name <- "--file="
script.name <- sub(file.arg.name, "", initial.options[grep(file.arg.name, initial.options)])
script.basename <- dirname(script.name)
oldwd=getwd()
setwd(script.basename)
setwd(rfold)
for (filename in userfiles) {
source(filename)
}
setwd(oldwd)

rm(oldwd)
rm(initial.options)
rm(file.arg.name)
rm(script.name)
rm(script.basename)


